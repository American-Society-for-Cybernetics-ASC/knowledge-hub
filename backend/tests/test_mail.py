from database.model import MailSender

from .mock_mail_provider import MockMailManager
from mail.model import Email
from mail import mail_module


def test_email_failure(
    test_server,
    mock_get_session,
    mock_mail_manager: MockMailManager,
    mock_mail_provider,
):
    """Test that a failed email gets recorded in the database"""
    mock_mail_manager.fail_next_n_mail(1)

    with mock_get_session() as session:
        provider = session.get(MailSender, mock_mail_provider)
        mail_module.send_mail(
            session,
            Email(
                recipients=["A", "B"],
                subject="Subject",
                content="Content",
            ),
            provider,
        )

        assert len(mock_mail_manager.sent_mail()) == 0
        assert mail_module.get_failed_emails(session)[0].email.content == "Content"
        # Content gets redacted when exposed publicly
        assert "content" not in test_server.get("/mail/failed").json()[0]["email"]
