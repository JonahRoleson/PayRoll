"""Time entry (Employee Time Entry Screen requirement).

Core rules implemented:
- Salary employees: only PTO entry; otherwise they are automatically paid 8 hours Mon-Fri.
- Hourly employees: can enter hours for each day; anything over 8/day is overtime at 1.5x.
- Saturday hours are overtime at 1.5x.

The locking requirement ("no updates after payroll is calculated") is handled by:
- PayrollRun.locked flag (see payroll app)
- TimeEntry.locked flag, set when a PayrollRun is created

"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from employees.models import Employee, PayType

class TimeEntry(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="time_entries")
    work_date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pto_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    submitted = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("employee", "work_date")
        ordering = ["-work_date"]

    def clean(self):
        if self.locked:
            raise ValidationError("This time entry is locked (payroll already calculated).")

        if self.hours_worked < 0 or self.pto_hours < 0:
            raise ValidationError("Hours cannot be negative.")

        # Basic sanity check as suggested in the prompt (e.g. 80 hours in a week looks unusual).
        if self.hours_worked > 24:
            raise ValidationError("Hours for a single day cannot exceed 24.")

        # Enforce salary/hourly rules.
        if self.employee.pay_type == PayType.SALARY:
            if self.hours_worked != 0:
                raise ValidationError("Salary employees should not enter daily hours. Only PTO is allowed.")
            if self.pto_hours > 8:
                raise ValidationError("PTO hours per day should not exceed 8.")
        else:
            # Hourly: PTO allowed, but total should still be reasonable.
            if self.hours_worked + self.pto_hours > 24:
                raise ValidationError("Total hours (worked + PTO) cannot exceed 24 in a day.")

    def __str__(self) -> str:
        return f"{self.employee.employee_id} {self.work_date}"
