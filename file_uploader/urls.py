from django.urls import path

from billing.admin_views import custom_admin_site

urlpatterns = [
    path("admin/", custom_admin_site.urls),
]
