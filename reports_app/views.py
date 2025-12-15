from __future__ import annotations
from django.shortcuts import render
from accounts.decorators import hr_required
from payroll.models import PayrollRun

@hr_required
def reports_home(request):
    runs = PayrollRun.objects.all()[:10]
    return render(request, "reports/reports_home.html", {"runs": runs})
