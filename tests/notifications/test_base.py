from app.notifications.base import NotifierBase, NotificationMessage


def test_notification_message_fields() -> None:
    msg = NotificationMessage(subject="Test", body="Hello")
    assert msg.subject == "Test"
    assert msg.html_body is None
    assert msg.metadata is None


def test_notifier_base_cannot_be_instantiated() -> None:
    try:
        NotifierBase()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
