import database
from database import model
from .model import EmailTemplateData, EmailTemplateUpdate


# Default templates
TEMPLATES: list[EmailTemplateData] = [
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
]


class EmailTemplatesModule:
    def seed_defaults(self):
        """Seed the default templates if they do not exist."""
        with database.get_session() as session:
            for template in TEMPLATES:
                existing = session.get(model.EmailTemplate, template.name)
                if not existing:
                    session.add(
                        model.EmailTemplate(
                            name=template.name,
                            subject=template.subject,
                            body=template.body,
                            variables=template.variables,
                        )
                    )
            session.commit()

    def get_templates(self) -> list[EmailTemplateData]:
        """Get all email templates."""
        with database.get_session() as session:
            templates = session.query(model.EmailTemplate).all()
            return [
                EmailTemplateData(
                    name=t.name,
                    subject=t.subject,
                    body=t.body,
                    variables=t.variables,
                )
                for t in templates
            ]

    def get_template(self, name: str) -> EmailTemplateData | None:
        """Get a specific email template by name."""
        with database.get_session() as session:
            template = session.get(model.EmailTemplate, name)
            if not template:
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

    def render_template(self, name: str, variables: dict[str, str]) -> tuple[str, str] | None:
        """
        Render a template by replacing variables with actual values. Returns tuple or None if template not found.
        """
        template = self.get_template(name)
        if not template:
            return None

        subject = template.subject
        body = template.body

        # TODO: Fix minor attack vector of unintended substitution with users naming themselves {{date}} or other template variables.
        for key, value in variables.items():
            subject = subject.replace(f"{{{{{key}}}}}", value)
            body = body.replace(f"{{{{{key}}}}}", value)

        return subject, body