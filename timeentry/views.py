from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView

from employees.models import Employee
from .models import TimeEntry

class TimeEntryForm(ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["work_date", "hours_worked", "pto_hours"]

class MyTimeEntryListView(LoginRequiredMixin, ListView):
    model = TimeEntry
    template_name = "timeentry/my_timeentry_list.html"
    context_object_name = "entries"
    paginate_by = 31

    def get_queryset(self):
        if self.request.user.is_staff:
            # HR can view all time entries (adjust as needed).
            return TimeEntry.objects.select_related("employee").all()
        emp = Employee.objects.filter(user=self.request.user).first()
        if not emp:
            return TimeEntry.objects.none()
        return TimeEntry.objects.filter(employee=emp)

class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = "timeentry/timeentry_form.html"

    def form_valid(self, form):
        if self.request.user.is_staff:
            raise PermissionDenied("HR should use admin tools for adjustments (or extend this view).")
        emp = Employee.objects.filter(user=self.request.user).first()
        if not emp:
            raise PermissionDenied("No employee profile is linked to this account.")
        form.instance.employee = emp
        return super().form_valid(form)

    def get_success_url(self):
        return redirect("my_time_entries").url

class TimeEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = "timeentry/timeentry_form.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        emp = Employee.objects.filter(user=self.request.user).first()
        return qs.filter(employee=emp)

    def get_success_url(self):
        return redirect("my_time_entries").url

def submit_timeentry(request, pk: int):
    entry = get_object_or_404(TimeEntry, pk=pk)
    if not request.user.is_staff and entry.employee.user_id != request.user.id:
        raise PermissionDenied()
    if entry.locked:
        messages.error(request, "This entry is locked; payroll has already been calculated.")
        return redirect("my_time_entries")
    entry.submitted = True
    entry.save()
    messages.success(request, "Submitted.")
    return redirect("my_time_entries")
