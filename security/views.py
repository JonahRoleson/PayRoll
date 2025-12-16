import hashlib
from django.contrib.auth.hashers import make_password
from django.shortcuts import render

from .forms import PasswordHashDemoForm


def password_hash_demo(request):
    """
    Demo view for coursework:
    - Shows plaintext + MD5 hash on-screen for screenshot evidence.
    - Also shows Django's recommended secure hash (PBKDF2 by default).
    IMPORTANT: Do NOT log passwords. Do NOT keep this endpoint in production.
    """
    form = PasswordHashDemoForm(request.POST or None)

    context = {"form": form, "result": None}

    if request.method == "POST" and form.is_valid():
        pw = form.cleaned_data["password"]

        md5_hex = hashlib.md5(pw.encode("utf-8")).hexdigest()  # coursework demo only
        django_hash = make_password(pw)  # secure storage format

        context["result"] = {
            "password": pw,           # for screenshot evidence only
            "md5": md5_hex,           # requested by assignment
            "django_hash": django_hash,
        }

        # DO NOT print(pw) or print(md5_hex). Keep secrets out of logs.

    return render(request, "security/password_hash_demo.html", context)

def error_400(request, exception=None):
    return render(request, "security/400.html", status=400)

def error_403(request, exception=None):
    return render(request, "security/403.html", status=403)

def error_404(request, exception=None):
    return render(request, "security/404.html", status=404)

def error_500(request):
    return render(request, "security/500.html", status=500)
