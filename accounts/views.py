from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .forms import LoginForm
from employees.models import Employee

class TokyoNightLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Check your User ID and password.")
        return super().form_invalid(form)

login_view = TokyoNightLoginView.as_view()

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    """Simple post-login landing page.

    HR users (is_staff) get quick links to admin actions.
    Employees get quick links to time entry + paycheck preview.
    """
    employee = None
    if not request.user.is_staff:
        employee = Employee.objects.filter(user=request.user).first()
    return render(request, "accounts/dashboard.html", {"employee": employee})
