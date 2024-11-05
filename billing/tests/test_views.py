from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from billing.models import Debt, ProcessingCheckpoint


class UploadCSVTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse("admin:upload_csv")
        self.user = User.objects.create_superuser(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def tearDown(self):
        Debt.objects.all().delete()
        ProcessingCheckpoint.objects.all().delete()
        User.objects.all().delete()

    def test_upload_csv(self):
        csv_content = (
            b"name,governmentId,email,debtAmount,debtDueDate,debtId\n"
            b"John Doe,1234,johndoe@example.com,1000,2023-01-01,"
            b"123e4567-e89b-12d3-a456-426614174000"
        )
        uploaded_file = SimpleUploadedFile(
            "test.csv", csv_content, content_type="text/csv"
        )

        response = self.client.post(self.upload_url, {"file": uploaded_file})
        self.assertEqual(response.status_code, 302)

        processing_checkpoint = ProcessingCheckpoint.objects.get(file_name="test.csv")
        processing_checkpoint.refresh_from_db()
        self.assertTrue(
            ProcessingCheckpoint.objects.filter(file_name="test.csv").exists()
        )

        self.assertEqual(Debt.objects.count(), 1)
        debt = Debt.objects.first()
        debt.refresh_from_db()
        self.assertEqual(debt.name, "John Doe")
        self.assertEqual(debt.government_id, "1234")
        self.assertEqual(debt.email, "johndoe@example.com")
        self.assertEqual(debt.debt_amount, 1000)
        self.assertFalse(debt.invoice_generated)
        self.assertFalse(debt.email_sent)

    def test_upload_csv_no_debt_duplicated(self):
        csv_content_1 = (
            b"name,governmentId,email,debtAmount,debtDueDate,debtId\n"
            b"John Doe,1234,johndoe@example.com,1000,2023-01-01,"
            b"123e4567-e89b-12d3-a456-426614174000"
        )
        uploaded_file_1 = SimpleUploadedFile(
            "test.csv", csv_content_1, content_type="text/csv"
        )
        response_1 = self.client.post(self.upload_url, {"file": uploaded_file_1})
        self.assertEqual(response_1.status_code, 302)

        csv_content_2 = (
            b"name,governmentId,email,debtAmount,debtDueDate,debtId\n"
            b"Jane Doe,5678,janedoe@example.com,2000,2023-02-01,"
            b"223e4567-e89b-12d3-a456-426614174001\n"
            b"John Doe,1234,johndoe@example.com,1000,2023-01-01,"
            b"123e4567-e89b-12d3-a456-426614174000"
        )
        uploaded_file_2 = SimpleUploadedFile(
            "test.csv", csv_content_2, content_type="text/csv"
        )
        response_2 = self.client.post(self.upload_url, {"file": uploaded_file_2})
        self.assertEqual(response_2.status_code, 302)

        self.assertEqual(ProcessingCheckpoint.objects.count(), 2)
        self.assertEqual(Debt.objects.count(), 2)

    def test_upload_non_csv_file(self):
        non_csv_content = b"This is not a CSV file."
        uploaded_file = SimpleUploadedFile(
            "test.txt", non_csv_content, content_type="text/plain"
        )

        response = self.client.post(self.upload_url, {"file": uploaded_file})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "This is not a CSV file"})
