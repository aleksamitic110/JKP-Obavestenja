from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.notifications.base import NotifierBase, NotificationMessage


class EmailNotifier(NotifierBase):
    channel_name = "email"

    async def send(self, recipient: str, message: NotificationMessage) -> bool:
        try:
            await asyncio.to_thread(self._send_sync, recipient, message)
            return True
        except Exception:
            return False

    def _send_sync(self, recipient: str, message: NotificationMessage) -> None:
        msg = EmailMessage()
        msg["Subject"] = message.subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = recipient

        if message.html_body:
            msg.add_alternative(message.html_body, subtype="html")
        msg.set_content(message.body)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
