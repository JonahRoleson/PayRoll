from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import get_object_or_404, redirect
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render
from .models import Employee, SalaryProfile
from .models import Employee, SalaryProfile
from accounts.decorators import is_hr


class HRRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_hr(self.request.user)


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_id","department","job_title",
            "first_name","last_name","sur_name",
            "status","date_of_birth","gender",
            "pay_type","company_email",
            "address_line_1","address_line_2","city","state","zip_code",
            "picture"
        ]


class SalaryProfileForm(ModelForm):
    class Meta:
        model = SalaryProfile
        fields = ["date_hire", "salary_type", "base_pay", "medical", "dependents"]


class SalaryProfileUpsertView(HRRequiredMixin, FormView):
    template_name = "employees/salary_form.html"
    form_class = SalaryProfileForm

    def dispatch(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee, pk=kwargs["employee_pk"])
        # Create the profile on GET too, so templates never blow up
        self.salary_profile, _ = SalaryProfile.objects.get_or_create(employee=self.employee)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Bind the ModelForm to the existing SalaryProfile instance."""
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.salary_profile
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["employee"] = self.employee
        ctx["salary_profile"] = self.salary_profile
        return ctx

    def form_valid(self, form):
        # Since instance is bound, form.save() updates the existing profile
        form.save()
        return redirect("employee_list")
    
class EmployeeListView(HRRequiredMixin, ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 25
    ordering = ["last_name", "first_name"]

class EmployeeCreateView(HRRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")

class EmployeeUpdateView(HRRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")

class EmployeeDeleteView(HRRequiredMixin, DeleteView):
    model = Employee
    template_name = "employees/employee_confirm_delete.html"
    success_url = reverse_lazy("employee_list")
