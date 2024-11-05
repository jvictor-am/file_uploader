import logging

logger = logging.getLogger(__name__)


class EmailSending:
    def send_email(self, debt, invoice):
        logger.info(f"Sending email to {debt.email} with invoice: {invoice}")
        debt.email_sent = True
        debt.save(update_fields=["email_sent"])
        return f"Email sent to {debt.email} with invoice: {invoice}"
