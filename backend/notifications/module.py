from datetime import datetime
from sqlalchemy import select

import database
from database import model
from mail.module import MailModule
from mail.model import Email
from settings import SETTINGS


class NotificationsModule:

    def _get_sender(self) -> str:
        """Returns the configured sender email address"""
        return SETTINGS.google_username or "noreply@ckh.asc-cybernetics.org"

    def notify_managers_new_application(self, applicant_email: str, applicant_name: str):
        """
        Notifies all managers when a new membership application is submitted by a non-member.
        """
        session = database.get_session()

        # Find all members with manager role
        managers = session.execute(
            select(model.AuthUser).where(model.AuthUser.role == "manager")
        ).scalars().all()

        manager_emails = [m.email for m in managers if m.email]

        if not manager_emails:
            return

        mail = Email(
            sender=self._get_sender(),
            recipients=manager_emails,
            subject="New Membership Application Received",
            content=f"""A new membership application has been submitted.

Applicant: {applicant_name}
Email: {applicant_email}

Please log in to the ASC CKH to review and action this application.

Best regards,
The ASC CKH System"""
        )
        MailModule().send_mail(mail)

    def notify_applicant_approved(self, email: str, name: str):
        """
        Notifies an applicant that their membership application has been approved.
        """
        mail = Email(
            sender=self._get_sender(),
            recipients=[email],
            subject="Your ASC Membership Application Has Been Approved",
            content=f"""Dear {name},

We are pleased to inform you that your membership application to the American Society for Cybernetics has been approved.

You now have access to the ASC Collaborative Knowledge Hub.
Please log in to complete your membership setup.

Best regards,
The ASC CKH Team"""
        )
        MailModule().send_mail(mail)

    def notify_applicant_denied(self, email: str, name: str):
        """
        Notifies an applicant that their membership application has been denied.
        """
        mail = Email(
            sender=self._get_sender(),
            recipients=[email],
            subject="Update on Your ASC Membership Application",
            content=f"""Dear {name},

Thank you for your interest in the American Society for Cybernetics.

Unfortunately, we are unable to approve your membership application at this time. Please contact your administrator for more information.

Best regards,
The ASC CKH Team"""
        )
        MailModule().send_mail(mail)

    def notify_applicant_revision_requested(self, email: str, name: str, notes: str):
        """
        Notifies an applicant that a revision has been requested on their application.
        """
        mail = Email(
            sender=self._get_sender(),
            recipients=[email],
            subject="Revision Requested for Your ASC Membership Application",
            content=f"""Dear {name},

Thank you for your membership application to the American Society for Cybernetics.

Our team has reviewed your application and requires some revisions before we can proceed. Please log in to the ASC CKH to review the feedback and update your application.

Reviewer notes:
{notes}

Best regards,
The ASC CKH Team"""
        )
        MailModule().send_mail(mail)

    def notify_membership_status(self, email: str, name: str, status: str):
        """
        Sends a membership status notification email to a member.
        """
        mail = Email(
            sender=self._get_sender(),
            recipients=[email],
            subject="Your ASC Membership Status Update",
            content=f"""Dear {name},

This is a notification regarding your ASC membership status.

Your current membership status is: {status}

If you have any questions about your membership status, please contact your administrator.

Best regards,
The ASC CKH Team"""
        )
        MailModule().send_mail(mail)

    def send_welcome_email(self, email: str, name: str):
        """
        Sends a welcome email to a newly registered user.
        """
        mail = Email(
            sender=self._get_sender(),
            recipients=[email],
            subject="Welcome to the ASC Collaborative Knowledge Hub",
            content=f"""Dear {name},

Welcome to the American Society for Cybernetics Collaborative Knowledge Hub!

Your account has been successfully created. You can now log in and explore the knowledge hub, connect with other members, and contribute to the ASC community.

If you have any questions, please contact your administrator.

Best regards,
The ASC CKH Team"""
        )
        MailModule().send_mail(mail)

    def send_email_to_all_members(self, subject: str, content: str):
        """
        Sends an email to all membersfor bulk communications.
        """
        session = database.get_session()

        members = session.execute(select(model.Member)).scalars().all()

        recipients = []
        for member in members:
            if member.auth_user and member.auth_user.email:
                recipients.append(member.auth_user.email)

        if not recipients:
            return

        mail = Email(
            sender=self._get_sender(),
            recipients=recipients,
            subject=subject,
            content=content
        )
        MailModule().send_mail(mail)