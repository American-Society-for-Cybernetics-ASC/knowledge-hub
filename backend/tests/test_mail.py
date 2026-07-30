from mail.module import Email, MailModule
from mail.provider.mock_provider import MockMailProvider


def test_dead_letter(test_server):
    MockMailProvider.fail_next_n_mail(1)
    MailModule().send_mail(
        Email(
            sender="Sender", recipients=["A", "B"], subject="Subject", content="Content"
        )
    )

    assert len(MockMailProvider.sent_mail()) == 0
    assert MailModule().get_failed_emails()[0].email.content == "Content"
    assert "content" not in test_server.get("/mail/failed").json()[0]["email"]
