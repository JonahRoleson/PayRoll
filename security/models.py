from django.db import models
from employees.models import Employee
from .crypto import encrypt_str, decrypt_str

class EncryptedEmployeeNote(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="secure_note")
    note_encrypted = models.TextField(blank=True, default="")

    def set_note(self, plaintext: str) -> None:
        self.note_encrypted = encrypt_str(plaintext)

    def get_note(self) -> str:
        return decrypt_str(self.note_encrypted)
