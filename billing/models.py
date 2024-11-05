import uuid

from django.db import models


class Debt(models.Model):
    name = models.CharField(max_length=255)
    government_id = models.CharField(max_length=20)
    email = models.EmailField()
    debt_amount = models.DecimalField(max_digits=15, decimal_places=2)
    debt_due_date = models.DateField()
    debt_id = models.UUIDField(primary_key=True, unique=True)
    invoice_generated = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProcessingCheckpoint(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    upload_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    total_rows = models.PositiveIntegerField(default=0)
    last_processed_row = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    processing_duration = models.DurationField(null=True, blank=True)
    user_id = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("file_name", "upload_id")

    def __str__(self):
        description = f"{self.file_name} ({self.upload_id}) uploaded on"
        description += f" {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        return description
