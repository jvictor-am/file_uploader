from __future__ import absolute_import, unicode_literals

import logging
import os
from uuid import UUID

import duckdb
from celery import chord, shared_task
from django.conf import settings
from django.db import IntegrityError, OperationalError
from django.utils import timezone

from .email_sender import EmailSending
from .invoice import InvoiceGeneration
from .models import Debt, ProcessingCheckpoint

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_batch(self, batch, file_name, upload_id):
    debt_objects = []
    for row in batch:
        debt_id = UUID(row[5])
        debt = Debt(
            name=row[0],
            government_id=row[1],
            email=row[2],
            debt_amount=row[3],
            debt_due_date=row[4],
            debt_id=debt_id,
        )
        debt_objects.append(debt)
    try:
        Debt.objects.bulk_create(debt_objects, ignore_conflicts=True)
    except IntegrityError as e:
        logger.error(f"IntegrityError during bulk_create: {e}")

    checkpoint = ProcessingCheckpoint.objects.get(
        file_name=file_name, upload_id=upload_id
    )
    checkpoint.last_processed_row += len(batch)
    checkpoint.save(update_fields=["last_processed_row"])

    return len(debt_objects)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_csv(self, file_name, file_size, user_id, upload_id):
    start_time = timezone.now()
    temp_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    try:
        # Create a DuckDB connection and load the CSV file
        conn = duckdb.connect(database=":memory:")
        conn.execute(
            "CREATE TABLE debts AS SELECT * FROM read_csv_auto(?)", [temp_file_path]
        )

        debts = conn.execute("SELECT * FROM debts").fetchall()
        total_rows = len(debts)
        logger.info(f"Total number of debts in the file: {total_rows}")

        checkpoint, created = ProcessingCheckpoint.objects.get_or_create(
            file_name=file_name,
            upload_id=upload_id,
            defaults={
                "file_size": file_size,
                "total_rows": total_rows,
                "user_id": user_id,
                "status": "processing",
                "last_processed_row": 0,
            },
        )
        last_processed_row = checkpoint.last_processed_row

        batch_size = 10000
        tasks = []
        for i in range(last_processed_row, total_rows, batch_size):
            batch = debts[i : i + batch_size]
            tasks.append(process_batch.s(batch, file_name, upload_id))

        chord(tasks)(
            finalize_csv_processing.s(
                file_name, file_size, user_id, upload_id, start_time
            )
        )

    except OperationalError as exc:
        logger.error(f"OperationalError: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def finalize_csv_processing(
    self, results, file_name, file_size, user_id, upload_id, start_time
):
    temp_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    try:
        checkpoint = ProcessingCheckpoint.objects.get(
            file_name=file_name, upload_id=upload_id
        )
        checkpoint.file_size = file_size
        checkpoint.total_rows = sum(results)
        checkpoint.user_id = user_id
        checkpoint.last_processed_row = checkpoint.total_rows
        checkpoint.status = "completed"
        checkpoint.processing_duration = timezone.now() - start_time
        checkpoint.save()

        os.remove(temp_file_path)

        logger.info("Batch processing completed successfully")

    except OperationalError as exc:
        logger.error(f"OperationalError: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_debt_batch(self):
    try:
        invoice_generator = InvoiceGeneration()
        email_sender = EmailSending()

        debts = Debt.objects.filter(invoice_generated=False, email_sent=False)
        for debt in debts:
            invoice = invoice_generator.generate_invoice(debt)
            email_sender.send_email(debt, invoice)

    except Debt.DoesNotExist:
        logger.error(f"Debt with ID {debt.debt_id} does not exist.")
