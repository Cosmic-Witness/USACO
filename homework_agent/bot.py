import asyncio
import os
from datetime import datetime
from typing import Tuple

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

from .config import load_config
from .db import Database
from .generator import HomeworkGenerator
from .pdf_service import render_markdown_to_pdf
from .email_service import send_email_with_attachment
from .utils import parse_int, validate_date

# Conversation states
(SUBJECT, TOPIC, LEVEL, NUM_Q, DUE_DATE) = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cfg = context.bot_data["cfg"]
    db: Database = context.bot_data["db"]
    user = update.effective_user
    db.ensure_teacher(user.id, user.full_name)
    await update.message.reply_text(
        "Welcome! I can create custom homework, export as PDF, and email it to your students.\n\n"
        "Commands:\n"
        "/add_student <Name> <email> - Add or update a student\n"
        "/remove_student <email> - Remove a student\n"
        "/list_students - List your students\n"
        "/create_homework - Start interactive homework creation\n"
        "/set_name <Your Name> - Update your display name on homework"
    )


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.bot_data["db"]
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /set_name Firstname Lastname")
        return
    name = " ".join(args)
    db.set_teacher_name(user.id, name)
    await update.message.reply_text(f"Updated your name to: {name}")


async def add_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.bot_data["db"]
    user = update.effective_user
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /add_student <Name> <email>")
        return
    name = " ".join(args[:-1])
    email = args[-1]
    db.add_student(user.id, name, email)
    await update.message.reply_text(f"Added/updated student: {name} <{email}>")


async def remove_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.bot_data["db"]
    user = update.effective_user
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /remove_student <email>")
        return
    count = db.remove_student(user.id, args[0])
    if count:
        await update.message.reply_text("Removed student.")
    else:
        await update.message.reply_text("No matching student found.")


async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.bot_data["db"]
    user = update.effective_user
    rows = db.list_students(user.id)
    if not rows:
        await update.message.reply_text("You have no students yet. Use /add_student <Name> <email> to add one.")
        return
    lines = ["Your students:"]
    for r in rows:
        lines.append(f"- {r['name']} <{r['email']}>")
    await update.message.reply_text("\n".join(lines))


async def create_homework_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("What is the subject? (e.g., Math, History)")
    return SUBJECT


async def create_homework_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text.strip()
    await update.message.reply_text("Great. What is the topic?")
    return TOPIC


async def create_homework_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["topic"] = update.message.text.strip()
    await update.message.reply_text("Level or grade? (e.g., Grade 7, Beginner, AP)")
    return LEVEL


async def create_homework_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["level"] = update.message.text.strip()
    await update.message.reply_text("How many questions? (default 10)")
    return NUM_Q


async def create_homework_numq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["num_questions"] = parse_int(update.message.text.strip(), 10)
    await update.message.reply_text("Due date (YYYY-MM-DD)?")
    return DUE_DATE


async def create_homework_duedate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    due = update.message.text.strip()
    if not validate_date(due):
        await update.message.reply_text("Please provide a date as YYYY-MM-DD.")
        return DUE_DATE
    context.user_data["due_date"] = due

    # Kick off generation and sending in background
    asyncio.create_task(_process_homework_job(update, context))

    await update.message.reply_text("Got it! Generating homework and emailing your students. I will update you when done.")
    return ConversationHandler.END


async def _process_homework_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg = context.bot_data["cfg"]
    db: Database = context.bot_data["db"]

    user = update.effective_user
    subject = context.user_data["subject"]
    topic = context.user_data["topic"]
    level = context.user_data["level"]
    num_questions = context.user_data["num_questions"]
    due_date = context.user_data["due_date"]

    job_id = db.create_job(user.id, subject, topic, level, num_questions, due_date)

    gen = context.bot_data["generator"]

    try:
        md = gen.generate(subject, topic, level, num_questions, due_date, user.full_name)
        filename = f"homework_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(cfg.output_dir, filename)
        render_markdown_to_pdf(md, output_path)
        db.update_job_pdf(job_id, output_path)

        # Email students
        students = db.list_students(user.id)
        if not students:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No students found; skipping emails.")
        else:
            subject_line = f"{subject} Homework: {topic} (Due {due_date})"
            body = (
                f"Hello,\n\nPlease find attached your homework for {subject} on {topic}.\n"
                f"Due date: {due_date}.\n\n"
                f"Best,\n{cfg.from_name}"
            )

            loop = asyncio.get_running_loop()
            tasks = []
            for s in students:
                tasks.append(
                    loop.run_in_executor(
                        None,
                        send_email_with_attachment,
                        cfg.smtp,
                        cfg.from_email,
                        cfg.from_name,
                        s["email"],
                        subject_line,
                        body,
                        output_path,
                    )
                )
            await asyncio.gather(*tasks, return_exceptions=True)
        db.update_job_status(job_id, "sent")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Homework sent!")
    except Exception as e:
        db.update_job_status(job_id, "failed")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Failed to complete job: {e}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def build_app():
    cfg = load_config()
    if not cfg.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    db = Database(cfg.database_path)
    generator = HomeworkGenerator(cfg.openai_api_key, cfg.openai_model)

    app = Application.builder().token(cfg.telegram_bot_token).build()

    # Inject shared objects
    app.bot_data["cfg"] = cfg
    app.bot_data["db"] = db
    app.bot_data["generator"] = generator

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("set_name", set_name))
    app.add_handler(CommandHandler("add_student", add_student))
    app.add_handler(CommandHandler("remove_student", remove_student))
    app.add_handler(CommandHandler("list_students", list_students))

    conv = ConversationHandler(
        entry_points=[CommandHandler("create_homework", create_homework_start)],
        states={
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_homework_subject)],
            TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_homework_topic)],
            LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_homework_level)],
            NUM_Q: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_homework_numq)],
            DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_homework_duedate)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    return app


def main():
    app = build_app()
    app.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()