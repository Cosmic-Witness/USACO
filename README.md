# Homework Agent Bot

Telegram bot that lets teachers generate custom homework, export to PDF, and email to their students.

## Setup

1. Create a Telegram Bot via @BotFather and get the token.
2. Copy `.env.example` to `.env` and fill values (Telegram token, SMTP credentials, OpenAI API key optional).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m homework_agent.bot
```

## Commands
- /start: Help and initialize your teacher profile
- /set_name <Your Name>: Set your display name
- /add_student <Name> <email>: Add or update a student
- /remove_student <email>: Remove a student
- /list_students: List students
- /create_homework: Interactive flow to generate, PDF, and email

## Notes
- OpenAI key is optional. Without it, a simple fallback generator is used.
- PDFs are saved under `homework_agent/out/`.
- Uses SQLite at `homework_agent/data.db`.