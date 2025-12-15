from django.contrib import admin
from .models import Employee, SalaryProfile

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "last_name", "first_name", "department", "job_title", "status", "pay_type")
    search_fields = ("employee_id", "first_name", "last_name", "company_email")
    list_filter = ("status", "department", "pay_type")

@admin.register(SalaryProfile)
class SalaryProfileAdmin(admin.ModelAdmin):
    list_display = ("employee", "date_hire", "salary_type", "base_pay", "medical", "dependents")
    list_filter = ("salary_type", "medical")
