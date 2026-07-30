from mail.module import Email, MailModule
from mail.provider.mock_provider import MockMailProvider


def test_email_failure(test_server):
    """Test that a failed email gets recorded in the database"""
    MockMailProvider.fail_next_n_mail(1)
    MailModule().send_mail(
        Email(
            sender="Sender", recipients=["A", "B"], subject="Subject", content="Content"
        )
    )

    assert len(MockMailProvider.sent_mail()) == 0
    assert MailModule().get_failed_emails()[0].email.content == "Content"
    # Content gets redacted when exposed publicly
    assert "content" not in test_server.get("/mail/failed").json()[0]["email"]
