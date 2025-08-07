import sqlite3
from contextlib import contextmanager
from typing import Iterable, Optional


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_schema()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS teachers (
                    telegram_id INTEGER PRIMARY KEY,
                    name TEXT
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_telegram_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    UNIQUE (teacher_telegram_id, email),
                    FOREIGN KEY (teacher_telegram_id) REFERENCES teachers(telegram_id) ON DELETE CASCADE
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS homework_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_telegram_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    level TEXT NOT NULL,
                    num_questions INTEGER NOT NULL,
                    due_date TEXT NOT NULL,
                    pdf_path TEXT,
                    status TEXT NOT NULL DEFAULT 'created',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()

    def ensure_teacher(self, telegram_id: int, name: Optional[str]) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO teachers (telegram_id, name) VALUES (?, ?)",
                (telegram_id, name),
            )
            conn.commit()

    def set_teacher_name(self, telegram_id: int, name: str) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE teachers SET name = ? WHERE telegram_id = ?",
                (name, telegram_id),
            )
            conn.commit()

    def add_student(self, teacher_telegram_id: int, name: str, email: str) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO students (teacher_telegram_id, name, email) VALUES (?, ?, ?)",
                (teacher_telegram_id, name, email),
            )
            conn.commit()

    def remove_student(self, teacher_telegram_id: int, email: str) -> int:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM students WHERE teacher_telegram_id = ? AND email = ?",
                (teacher_telegram_id, email),
            )
            conn.commit()
            return cur.rowcount

    def list_students(self, teacher_telegram_id: int) -> list[sqlite3.Row]:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, email FROM students WHERE teacher_telegram_id = ? ORDER BY name",
                (teacher_telegram_id,),
            )
            return cur.fetchall()

    def create_job(self, teacher_telegram_id: int, subject: str, topic: str, level: str, num_questions: int, due_date: str) -> int:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO homework_jobs (teacher_telegram_id, subject, topic, level, num_questions, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (teacher_telegram_id, subject, topic, level, num_questions, due_date),
            )
            conn.commit()
            return cur.lastrowid

    def update_job_pdf(self, job_id: int, pdf_path: str) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE homework_jobs SET pdf_path = ?, status = 'rendered' WHERE id = ?",
                (pdf_path, job_id),
            )
            conn.commit()

    def update_job_status(self, job_id: int, status: str) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE homework_jobs SET status = ? WHERE id = ?",
                (status, job_id),
            )
            conn.commit()