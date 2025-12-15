"""Top-level URL routes."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import login_view, logout_view, dashboard

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth + landing
    path("", dashboard, name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # App routes
    path("employees/", include("employees.urls")),
    path("time/", include("timeentry.urls")),
    path("payroll/", include("payroll.urls")),
    path("reports/", include("reports_app.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "security.views.error_404"
handler500 = "security.views.error_500"
handler403 = "security.views.error_403"
handler400 = "security.views.error_400"
