from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from water_alerts.models import Alert


@dataclass(frozen=True)
class EmailSettings:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipients: tuple[str, ...]
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "EmailSettings":
        recipients = tuple(
            item.strip()
            for item in os.environ.get("EMAIL_TO", "").split(",")
            if item.strip()
        )
        required = {
            "SMTP_HOST": os.environ.get("SMTP_HOST"),
            "SMTP_USERNAME": os.environ.get("SMTP_USERNAME"),
            "SMTP_PASSWORD": os.environ.get("SMTP_PASSWORD"),
            "EMAIL_FROM": os.environ.get("EMAIL_FROM"),
        }
        missing = [name for name, value in required.items() if not value]
        if not recipients:
            missing.append("EMAIL_TO")
        if missing:
            raise RuntimeError(
                "Missing email environment variables: " + ", ".join(sorted(missing))
            )

        return cls(
            host=required["SMTP_HOST"] or "",
            port=int(os.environ.get("SMTP_PORT", "587")),
            username=required["SMTP_USERNAME"] or "",
            password=required["SMTP_PASSWORD"] or "",
            sender=required["EMAIL_FROM"] or "",
            recipients=recipients,
            use_tls=os.environ.get("SMTP_USE_TLS", "true").lower() not in {"0", "false", "no"},
        )


class EmailNotifier:
    def __init__(self, settings: EmailSettings, subject_prefix: str = "[Vodovod]") -> None:
        self.settings = settings
        self.subject_prefix = subject_prefix

    def send(self, alert: Alert) -> None:
        message = EmailMessage()
        message["Subject"] = self._subject(alert)
        message["From"] = self.settings.sender
        message["To"] = ", ".join(self.settings.recipients)
        message.set_content(self._body(alert))

        with smtplib.SMTP(self.settings.host, self.settings.port, timeout=30) as smtp:
            if self.settings.use_tls:
                smtp.starttls()
            smtp.login(self.settings.username, self.settings.password)
            smtp.send_message(message)

    def _subject(self, alert: Alert) -> str:
        locations = ", ".join(match.name for match in alert.matches)
        return f"{self.subject_prefix} {locations}: {alert.post.title}"

    def _body(self, alert: Alert) -> str:
        matched_keywords = ", ".join(
            keyword for match in alert.matches for keyword in match.matched_keywords
        )
        sections = "\n\n".join(alert.matched_sections) if alert.matched_sections else alert.content_preview
        return (
            "Pronadjeno je novo obavestenje koje se poklapa sa tvojim lokacijama.\n\n"
            f"Naslov: {alert.post.title}\n"
            f"Datum objave: {alert.post.published_at or 'nije pronadjen'}\n"
            f"Poklapanja: {matched_keywords}\n"
            f"Link: {alert.post.url}\n\n"
            "Relevantan tekst:\n"
            f"{sections}\n"
        )

