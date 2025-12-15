from django.urls import path
from . import views

urlpatterns = [
    path("", views.PayrollRunListView.as_view(), name="payroll_runs"),
    path("new/", views.create_payroll_run, name="payroll_run_new"),
    path("<int:pk>/", views.PayrollRunDetailView.as_view(), name="payroll_run_detail"),
    path("<int:pk>/export.csv", views.export_payroll_csv, name="payroll_export_csv"),
]
