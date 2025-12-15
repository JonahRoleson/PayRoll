"""Employee and payroll-related master data.

This module covers the *Employee Screen* and *Salary Screen* requirements:
- Employee demographic fields + validation
- Salary / benefit configuration used by payroll calculations

Notes:
- The "Employee ID" in the assignment is represented by `employee_id` and is unique.
- Employees are linked to Django auth users via OneToOne so login can be enforced.
"""
from __future__ import annotations

from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from security.validators import validate_safe_name

class EmployeeStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    TERMINATED = "TERMINATED", "Terminated"

class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"

class PayType(models.TextChoices):
    SALARY = "SALARY", "Salary"
    HOURLY = "HOURLY", "Hourly"

class MedicalCoverage(models.TextChoices):
    SINGLE = "SINGLE", "Single"
    FAMILY = "FAMILY", "Family"

def validate_age_18(dob: date) -> None:
    """Ensure the employee is at least 18 years old."""
    today = date.today()
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if years < 18:
        raise ValidationError("Employee must be at least 18 years old.")

class Employee(models.Model):
    """Demographics + identity record for an employee."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Linked login account (optional until created).",
    )

    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=80)
    job_title = models.CharField(max_length=80)

    first_name = models.CharField(max_length=80, validators=[validate_safe_name])
    last_name = models.CharField(max_length=80, validators=[validate_safe_name])
    sur_name = models.CharField(max_length=80, blank=True)

    status = models.CharField(max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    date_of_birth = models.DateField(validators=[validate_age_18])
    gender = models.CharField(max_length=1, choices=Gender.choices)

    pay_type = models.CharField(max_length=10, choices=PayType.choices)
    company_email = models.EmailField(unique=True)

    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    picture = models.ImageField(upload_to="employee_pics/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.last_name}, {self.first_name}"

class SalaryProfile(models.Model):
    """Salary/benefits record. Exactly one per employee."""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="salary_profile")

    date_hire = models.DateField()
    salary_type = models.CharField(max_length=10, choices=PayType.choices)

    # Base salary is used when salary_type=SALARY; hourly rate is used when salary_type=HOURLY.
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, help_text="Annual salary or hourly rate depending on pay type.")

    medical = models.CharField(max_length=10, choices=MedicalCoverage.choices, default=MedicalCoverage.SINGLE)
    dependents = models.PositiveIntegerField(default=0)

    def clean(self):
        # Keep salary_type consistent with Employee pay_type (business rule).
        if self.employee and self.salary_type != self.employee.pay_type:
            raise ValidationError("SalaryProfile salary_type must match Employee pay_type.")

    def medical_deduction_per_pay_period(self) -> int:
        """Assignment requirement: $50 single, $100 family (pretax)."""
        return 50 if self.medical == MedicalCoverage.SINGLE else 100

    def dependent_stipend(self) -> int:
        """Assignment requirement: $45 per dependent (treated as an addition to gross)."""
        return 45 * int(self.dependents)

    def __str__(self) -> str:
        return f"SalaryProfile({self.employee.employee_id})"
