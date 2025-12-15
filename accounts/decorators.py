"""Role helpers.

The SDEV268 requirements call out two user types:
- Admin (HR) users
- Employee users

In Django terms:
- Admin/HR users are `is_staff=True` (and may also be `is_superuser=True`).
- Employees are normal active users linked to an Employee record.

"""
from __future__ import annotations
from functools import wraps
from typing import Callable, Any
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import user_passes_test

def is_hr(user) -> bool:
    return user.is_authenticated and user.is_active and user.is_staff

def hr_required(view_func: Callable[..., HttpResponse]):
    """Decorator that restricts a view to HR/admin users."""
    return user_passes_test(is_hr)(view_func)
