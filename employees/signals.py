from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee, SalaryProfile


@receiver(post_save, sender=Employee)
def create_salary_profile_for_employee(sender, instance, created, **kwargs):
    """
    Whenever a new Employee is created, ensure they have a SalaryProfile.
    This works whether the Employee is created via:
    - your CreateView
    - the Django admin
    - fixtures / scripts / shell
    """
    if created:
        SalaryProfile.objects.get_or_create(employee=instance)
