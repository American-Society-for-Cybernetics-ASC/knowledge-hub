import database
from database import model
from .model import EmailTemplateData, EmailTemplateUpdate


# Default templates
DEFAULT_TEMPLATES: list[EmailTemplateData] = [
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