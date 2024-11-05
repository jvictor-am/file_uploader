from django.contrib import admin

from .admin_views import custom_admin_site
from .models import Debt, ProcessingCheckpoint


class DebtAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "government_id",
        "email",
        "debt_amount",
        "debt_due_date",
        "debt_id",
        "invoice_generated",
        "email_sent",
    )
    list_filter = ("invoice_generated", "email_sent")


class ProcessingCheckpointAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "upload_id",
        "last_processed_row",
        "status",
        "processing_duration_seconds",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("file_name", "upload_id", "user_id")
    readonly_fields = ("processing_duration", "created_at", "updated_at")

    def processing_duration_seconds(self, obj):
        if obj.processing_duration:
            return obj.processing_duration.total_seconds()
        return None

    processing_duration_seconds.short_description = "Processing Duration (seconds)"


custom_admin_site.register(Debt, DebtAdmin)
custom_admin_site.register(ProcessingCheckpoint, ProcessingCheckpointAdmin)
