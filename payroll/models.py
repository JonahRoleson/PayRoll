"""Payroll calculation data.

PayrollRun represents a single payroll calculation for a pay period.
Paycheck stores the results for an employee for that run.

The assignment also requires showing taxes/deductions for both employee and employer.
Those are stored separately to support reporting.

"""
from __future__ import annotations
from django.db import models
from django.contrib.auth import get_user_model
from employees.models import Employee

User = get_user_model()

class PayrollRun(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    locked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-calculated_at"]

    def __str__(self) -> str:
        return f"PayrollRun({self.period_start}..{self.period_end})"

class Paycheck(models.Model):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="paychecks")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)

    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    pretax_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxable_wages = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Employee-side taxes
    state_tax_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    federal_tax_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    social_security_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medicare_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Employer-side taxes
    federal_tax_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    social_security_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medicare_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Paycheck({self.employee.employee_id} {self.payroll_run_id})"
