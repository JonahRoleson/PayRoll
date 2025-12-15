"""Forms related to authentication and simple profile behaviors."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    """Standard login form, with small UI tweaks handled in templates."""
    username = forms.CharField(label="User ID / Email")
