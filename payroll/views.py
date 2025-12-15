from __future__ import annotations

from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView

from accounts.decorators import hr_required
from employees.models import Employee, EmployeeStatus
from timeentry.models import TimeEntry
from .models import PayrollRun, Paycheck
from .services import compute_payroll_for_employee

class PayrollRunListView(ListView):
    model = PayrollRun
    template_name = "payroll/run_list.html"
    context_object_name = "runs"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

class PayrollRunDetailView(DetailView):
    model = PayrollRun
    template_name = "payroll/run_detail.html"
    context_object_name = "run"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

@hr_required
def create_payroll_run(request):
    """Create a payroll run and lock time entry for the period.

    For simplicity, this UI defaults to a 7-day pay period, but you can extend it
    to bi-weekly/monthly later.
    """
    if request.method == "POST":
        period_start = date.fromisoformat(request.POST["period_start"])
        period_end = date.fromisoformat(request.POST["period_end"])

        run = PayrollRun.objects.create(
            period_start=period_start,
            period_end=period_end,
            calculated_by=request.user,
            locked=True,
        )

        # Lock time entries so they can't be edited after calculation.
        TimeEntry.objects.filter(work_date__gte=period_start, work_date__lte=period_end).update(locked=True)

        employees = Employee.objects.filter(status=EmployeeStatus.ACTIVE).select_related("salary_profile")
        created = 0
        for emp in employees:
            try:
                b = compute_payroll_for_employee(emp, period_start, period_end)
            except Exception as ex:
                messages.error(request, f"Skipped {emp.employee_id}: {ex}")
                continue

            Paycheck.objects.create(
                payroll_run=run,
                employee=emp,
                gross_pay=b.gross,
                pretax_deductions=b.pretax,
                taxable_wages=b.taxable,
                state_tax_employee=b.state_emp,
                federal_tax_employee=b.federal_emp,
                social_security_employee=b.ss_emp,
                medicare_employee=b.med_emp,
                federal_tax_employer=b.federal_er,
                social_security_employer=b.ss_er,
                medicare_employer=b.med_er,
                net_pay=b.net,
            )
            created += 1

        messages.success(request, f"Payroll calculated. Paychecks created: {created}.")
        return redirect("payroll_run_detail", pk=run.pk)

    return render(request, "payroll/run_new.html")

@hr_required
def export_payroll_csv(request, pk: int):
    run = get_object_or_404(PayrollRun, pk=pk)
    rows = run.paychecks.select_related("employee").all()

    import csv
    from io import StringIO
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow([
        "employee_id","name","gross_pay","pretax_deductions","taxable_wages",
        "state_tax_employee","federal_tax_employee","social_security_employee","medicare_employee",
        "net_pay",
        "federal_tax_employer","social_security_employer","medicare_employer"
    ])
    for p in rows:
        w.writerow([
            p.employee.employee_id,
            f"{p.employee.last_name}, {p.employee.first_name}",
            p.gross_pay, p.pretax_deductions, p.taxable_wages,
            p.state_tax_employee, p.federal_tax_employee, p.social_security_employee, p.medicare_employee,
            p.net_pay,
            p.federal_tax_employer, p.social_security_employer, p.medicare_employer
        ])

    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="payroll_{run.period_start}_{run.period_end}.csv"'
    return resp
