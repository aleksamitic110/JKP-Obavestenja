from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationMessage:
    """Unified notification payload."""
    subject: str
    body: str
    html_body: str | None = None
    metadata: dict | None = None


class NotifierBase(ABC):
    """
    Every notification channel implements this interface.
    To add Telegram/Discord later:
      1. Create notifications/channels/telegram.py
      2. Implement send()
      3. Add to dispatch.py channel list
    """

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Unique channel identifier: 'email', 'telegram', 'discord'."""
        ...

    @abstractmethod
    async def send(self, recipient: str, message: NotificationMessage) -> bool:
        """
        Send a notification. Returns True on success.
        `recipient` format depends on channel:
          - email: "user@example.com"
          - telegram: chat_id
          - discord: webhook_url
        """
        ...

    async def close(self) -> None:
        """Cleanup resources. Override if needed."""
        pass
