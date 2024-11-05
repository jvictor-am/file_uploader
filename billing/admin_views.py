import logging
import os
import uuid

from django.conf import settings
from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import path

from .tasks import process_csv

logger = logging.getLogger(__name__)


class CustomAdminSite(AdminSite):
    site_header = "File Uploader Admin"
    site_title = "File Uploader Admin Portal"
    index_title = "Welcome to the File Uploader Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload/", self.admin_view(self.upload_csv), name="upload_csv"),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            uploaded_file = request.FILES["file"]
            if not uploaded_file.name.endswith(".csv"):
                return JsonResponse({"error": "This is not a CSV file"}, status=400)
            file_name = uploaded_file.name
            file_size = uploaded_file.size
            user_id = request.user.id if request.user.is_authenticated else None

            temp_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(temp_file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            upload_id = uuid.uuid4()

            process_csv.delay(file_name, file_size, user_id, str(upload_id))

            return HttpResponseRedirect(request.path_info)

        return render(request, "admin/upload.html")


custom_admin_site = CustomAdminSite(name="custom_admin")
