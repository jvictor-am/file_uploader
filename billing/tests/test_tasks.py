import os
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from billing.models import Debt, ProcessingCheckpoint
from billing.tasks import (
    finalize_csv_processing,
    process_batch,
    process_csv,
    process_debt_batch,
)


class TasksTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="testuser", password="testpassword"
        )
        self.upload_id = uuid.uuid4()
        self.file_name = "test.csv"
        self.file_size = 1024
        self.temp_file_path = os.path.join(settings.MEDIA_ROOT, self.file_name)
        self.csv_content = (
            b"name,governmentId,email,debtAmount,debtDueDate,debtId\n"
            b"John Doe,1234,johndoe@example.com,1000,2023-01-01,"
            b"123e4567-e89b-12d3-a456-426614174000"
        )
        with open(self.temp_file_path, "wb") as f:
            f.write(self.csv_content)

    def tearDown(self):
        Debt.objects.all().delete()
        ProcessingCheckpoint.objects.all().delete()
        User.objects.all().delete()
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    @patch("billing.tasks.process_batch.apply_async", new_callable=MagicMock)
    @patch("billing.tasks.finalize_csv_processing.apply_async", new_callable=MagicMock)
    def test_process_csv(
        self, mock_finalize_csv_processing_apply_async, mock_process_batch_apply_async
    ):
        process_csv(self.file_name, self.file_size, self.user.id, str(self.upload_id))

        checkpoint = ProcessingCheckpoint.objects.get(file_name=self.file_name)
        self.assertEqual(checkpoint.file_size, self.file_size)
        self.assertEqual(checkpoint.user_id, self.user.id)
        self.assertEqual(checkpoint.upload_id, self.upload_id)

    def test_process_batch(self):
        ProcessingCheckpoint.objects.create(
            file_name=self.file_name,
            file_size=self.file_size,
            user_id=self.user.id,
            upload_id=str(self.upload_id),
            status="pending",
            last_processed_row=0,
        )

        batch = [
            [
                "John Doe",
                "1234",
                "johndoe@example.com",
                1000,
                "2023-01-01",
                "123e4567-e89b-12d3-a456-426614174000",
            ]
        ]

        process_batch(batch, self.file_name, str(self.upload_id))

        self.assertEqual(Debt.objects.count(), 1)
        debt = Debt.objects.first()
        self.assertEqual(debt.name, "John Doe")
        self.assertEqual(debt.government_id, "1234")
        self.assertEqual(debt.email, "johndoe@example.com")
        self.assertEqual(debt.debt_amount, 1000)
        self.assertEqual(
            debt.debt_due_date, datetime.strptime("2023-01-01", "%Y-%m-%d").date()
        )
        self.assertEqual(
            debt.debt_id, uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        )

        checkpoint = ProcessingCheckpoint.objects.get(file_name=self.file_name)
        self.assertEqual(checkpoint.last_processed_row, len(batch))

    def test_finalize_csv_processing(self):
        start_time = timezone.now()
        checkpoint = ProcessingCheckpoint.objects.create(
            file_name=self.file_name,
            file_size=self.file_size,
            user_id=self.user.id,
            upload_id=str(self.upload_id),
            status="processing",
            last_processed_row=0,
            total_rows=1,
        )

        finalize_csv_processing(
            [],
            self.file_name,
            self.file_size,
            self.user.id,
            str(self.upload_id),
            start_time,
        )

        checkpoint.refresh_from_db()
        self.assertEqual(checkpoint.status, "completed")
        self.assertIsNotNone(checkpoint.updated_at)
        self.assertIsNotNone(checkpoint.processing_duration)
        self.assertTrue(isinstance(checkpoint.processing_duration, timedelta))

    def test_process_debt_batch(self):
        debt = Debt.objects.create(
            name="John Doe",
            government_id="1234",
            email="johndoe@example.com",
            debt_amount=1000,
            debt_due_date=datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
            debt_id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
            invoice_generated=False,
            email_sent=False,
        )

        process_debt_batch()

        debt.refresh_from_db()
        self.assertEqual(debt.government_id, "1234")
        self.assertTrue(debt.invoice_generated)
        self.assertTrue(debt.email_sent)
