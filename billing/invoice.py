import logging

logger = logging.getLogger(__name__)


class InvoiceGeneration:
    def generate_invoice(self, debt):
        logger.info(f"Generating invoice for {debt.name} with debt ID {debt.debt_id}")
        debt.invoice_generated = True
        debt.save(update_fields=["invoice_generated"])
        return f"Invoice for {debt.name} with debt ID {debt.debt_id} generated."
