import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    return value


@dataclass
class SMTPConfig:
    host: str
    port: int
    user: str
    password: str


@dataclass
class AppConfig:
    telegram_bot_token: str
    openai_api_key: str | None
    openai_model: str
    smtp: SMTPConfig
    from_email: str
    from_name: str
    database_path: str
    output_dir: str


def load_config() -> AppConfig:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    openai_api_key = get_env("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")

    from_email = os.getenv("FROM_EMAIL", smtp_user)
    from_name = os.getenv("FROM_NAME", "Homework Agent")

    database_path = os.getenv("DATABASE_PATH", "/workspace/homework_agent/data.db")
    output_dir = os.getenv("OUTPUT_DIR", "/workspace/homework_agent/out")

    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    return AppConfig(
        telegram_bot_token=telegram_bot_token,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        smtp=SMTPConfig(host=smtp_host, port=smtp_port, user=smtp_user, password=smtp_pass),
        from_email=from_email,
        from_name=from_name,
        database_path=database_path,
        output_dir=output_dir,
    )