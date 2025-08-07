import smtplib
from email.message import EmailMessage
from typing import Optional

from .config import SMTPConfig


def send_email_with_attachment(
    smtp: SMTPConfig,
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            data = f.read()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="pdf",
            filename=attachment_path.split("/")[-1],
        )

    with smtplib.SMTP(smtp.host, smtp.port) as server:
        server.starttls()
        if smtp.user:
            server.login(smtp.user, smtp.password)
        server.send_message(msg)