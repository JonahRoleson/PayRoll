import re
from django.core.exceptions import ValidationError

SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9 _.-]{1,80}$")

def validate_safe_name(value: str) -> None:
    if not SAFE_NAME_RE.match(value or ""):
        raise ValidationError("Invalid characters. Use letters, numbers, space, _ . -")
