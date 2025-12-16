from django import forms

class PasswordHashDemoForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        max_length=128,
        help_text="For screenshot/demo only. Do not reuse real passwords."
    )
