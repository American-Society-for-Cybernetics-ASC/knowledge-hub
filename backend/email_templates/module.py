from sqlalchemy.orm import Session

import database
from database import model
from .model import EmailTemplateData, EmailTemplateUpdate


# Default templates
_TEMPLATES: list[EmailTemplateData] = [
    EmailTemplateData(
        name="new_member_joins",
        subject="Welcome to ASC, {{name}}!",
        body="Hi {{name}},\n\nWelcome to the ASC community! We are thrilled to have you as a member.\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{email}}"],
    ),
    EmailTemplateData(
        name="membership_renewed",
        subject="Your ASC membership has been renewed",
        body="Hi {{name}},\n\nYour ASC membership has been successfully renewed. Your new due date is {{new_due_date}}.\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{new_due_date}}"],
    ),
    EmailTemplateData(
        name="application_approved",
        subject="Your ASC membership application has been approved",
        body="Hi {{name}},\n\nCongratulations! Your membership application has been approved. Welcome to ASC!\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{email}}"],
    ),
    EmailTemplateData(
        name="payment_received",
        subject="Payment received - ASC Membership",
        body="Hi {{name}},\n\nWe have received your payment of {{amount}} on {{date}}. Thank you!\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{amount}}", "{{date}}"],
    ),
    EmailTemplateData(
        name="dues_announce",
        subject="Upcoming Membership Dues - ASC Membership",
        body="Hi {{name}},\n\nA reminder that your membership dues are on {{date}}.\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{date}}"],
    ),
    EmailTemplateData(
        name="dues_overdue",
        subject="Membership Dues Overdue - ASC Membership",
        body="Hi {{name}},\n\nA reminder that your membership dues were due on {{date}}.\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{date}}"],
    ),
    EmailTemplateData(
        name="dues_overdue_reminder",
        subject="Membership Dues Overdue - ASC Membership",
        body="Hi {{name}},\n\nA reminder that your membership dues were due on {{date}}.\n\nBest regards,\nThe ASC Team",
        variables=["{{name}}", "{{date}}"],
    ),
]
TEMPLATES: dict[str, EmailTemplateData] = {data.name: data for data in _TEMPLATES}


class EmailTemplatesModule:
    def get_templates(self) -> list[EmailTemplateData]:
        """Get all email templates."""
        with database.with_transaction() as session:
            return [
                template
                for template in (self.get_template(session, key) for key in TEMPLATES)
                if template is not None
            ]

    def get_template(self, session: Session, name: str) -> EmailTemplateData | None:
        """Get a specific email template by name."""
        template = session.get(model.EmailTemplate, name)
        if not template:
            if name in TEMPLATES:
                template = model.EmailTemplate(
                    name=TEMPLATES[name].name,
                    subject=TEMPLATES[name].subject,
                    body=TEMPLATES[name].body,
                    variables=TEMPLATES[name].variables,
                )
                session.add(template)
            else:
                return None
        return EmailTemplateData(
            name=template.name,
            subject=template.subject,
            body=template.body,
            variables=template.variables,
        )

    def update_template(
        self, name: str, update: EmailTemplateUpdate
    ) -> EmailTemplateData | None:
        """Update an email template."""
        with database.get_session() as session:
            template = session.get(model.EmailTemplate, name)
            if not template:
                return None
            if update.subject is not None:
                template.subject = update.subject
            if update.body is not None:
                template.body = update.body
            session.commit()
            return EmailTemplateData(
                name=template.name,
                subject=template.subject,
                body=template.body,
                variables=template.variables,
            )

    def render_template(
        self, name: str, variables: dict[str, str]
    ) -> tuple[str, str] | None:
        """
        Render a template by replacing variables with actual values. Returns tuple or None if template not found.
        """
        with database.with_transaction() as session:
            template = self.get_template(session, name)
        if not template:
            return None

        subject = template.subject
        body = template.body

        # TODO: Fix minor attack vector of unintended substitution with users naming themselves {{date}} or other template variables.
        for key, value in variables.items():
            subject = subject.replace(f"{{{{{key}}}}}", value)
            body = body.replace(f"{{{{{key}}}}}", value)

        return subject, body
