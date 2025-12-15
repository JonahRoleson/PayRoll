"""Payroll calculation logic.

This is intentionally kept in a separate module so it can be unit-tested
without needing to render templates or hit the admin.

Business rules are taken directly from the assignment prompt.

Important: This is a simplified payroll model for a class project; it is NOT
a production-grade tax engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from employees.models import Employee, PayType
from timeentry.models import TimeEntry

# Rates from prompt
STATE_TAX_IN = Decimal("0.0315")

FEDERAL_TAX = Decimal("0.0765")  # as specified in prompt
SOCIAL_SECURITY = Decimal("0.062")
MEDICARE = Decimal("0.0145")

OVERTIME_MULTIPLIER = Decimal("1.5")

def money(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class PayrollBreakdown:
    gross: Decimal
    pretax: Decimal
    taxable: Decimal
    state_emp: Decimal
    federal_emp: Decimal
    ss_emp: Decimal
    med_emp: Decimal
    federal_er: Decimal
    ss_er: Decimal
    med_er: Decimal
    net: Decimal

def _is_saturday(d: date) -> bool:
    return d.weekday() == 5  # Mon=0 ... Sat=5

def compute_weekly_hours(employee: Employee, period_start: date, period_end: date):
    """Return (regular_hours, overtime_hours, pto_hours).

    Overtime rules:
    - > 8 hours in a day is overtime
    - any hours on Saturday are overtime
    """
    regular = Decimal("0")
    overtime = Decimal("0")
    pto = Decimal("0")

    entries = TimeEntry.objects.filter(employee=employee, work_date__gte=period_start, work_date__lte=period_end)
    by_day = {e.work_date: e for e in entries}

    # iterate day-by-day to allow salary auto-pay rules
    d = period_start
    while d <= period_end:
        e = by_day.get(d)
        if employee.pay_type == PayType.SALARY:
            # Salary employees are paid 8 hours Mon-Fri automatically (conceptually),
            # and PTO is tracked separately for reporting.
            if d.weekday() < 5:  # Mon-Fri
                regular += Decimal("8")
            if e:
                pto += e.pto_hours
        else:
            if e:
                pto += e.pto_hours
                hrs = e.hours_worked
                if _is_saturday(d):
                    overtime += hrs
                else:
                    if hrs > 8:
                        regular += Decimal("8")
                        overtime += (hrs - Decimal("8"))
                    else:
                        regular += hrs
        d += timedelta(days=1)

    return regular, overtime, pto

def compute_payroll_for_employee(employee: Employee, period_start: date, period_end: date) -> PayrollBreakdown:
    """Compute gross/net/taxes for one employee for the given period."""
    if not hasattr(employee, "salary_profile"):
        raise ValueError(f"Employee {employee.employee_id} is missing a SalaryProfile.")

    sp = employee.salary_profile

    regular_hours, overtime_hours, _pto_hours = compute_weekly_hours(employee, period_start, period_end)

    rate = Decimal(sp.base_pay)

    if employee.pay_type == PayType.SALARY:
        # base_pay is treated as annual salary; weekly pay = annual/52
        gross = Decimal(sp.base_pay) / Decimal("52")
    else:
        gross = (regular_hours * rate) + (overtime_hours * rate * OVERTIME_MULTIPLIER)

    # Add dependent stipend to gross (prompt: $45 per dependent)
    gross += Decimal(sp.dependent_stipend())

    pretax = Decimal(sp.medical_deduction_per_pay_period())

    taxable = gross - pretax
    if taxable < 0:
        taxable = Decimal("0")

    # Employee taxes
    state_emp = taxable * STATE_TAX_IN
    federal_emp = taxable * FEDERAL_TAX
    ss_emp = taxable * SOCIAL_SECURITY
    med_emp = taxable * MEDICARE

    # Employer taxes (mirrors prompt)
    federal_er = taxable * FEDERAL_TAX
    ss_er = taxable * SOCIAL_SECURITY
    med_er = taxable * MEDICARE

    total_emp_taxes = state_emp + federal_emp + ss_emp + med_emp

    net = gross - pretax - total_emp_taxes

    return PayrollBreakdown(
        gross=money(gross),
        pretax=money(pretax),
        taxable=money(taxable),
        state_emp=money(state_emp),
        federal_emp=money(federal_emp),
        ss_emp=money(ss_emp),
        med_emp=money(med_emp),
        federal_er=money(federal_er),
        ss_er=money(ss_er),
        med_er=money(med_er),
        net=money(net),
    )
