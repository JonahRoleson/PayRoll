from __future__ import annotations

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from employees.models import Employee, SalaryProfile, EmployeeStatus, Gender, PayType, MedicalCoverage

User = get_user_model()

FIRST = ["Ava","Noah","Mia","Liam","Emma","Olivia","Elijah","Sophia","Amelia","James","Lucas","Isabella"]
LAST = ["Johnson","Smith","Miller","Davis","Brown","Wilson","Moore","Taylor","Anderson","Thomas","Jackson","White"]
DEPTS = ["HR","Accounting","Operations","Engineering","Sales"]
JOBS = ["Coordinator","Analyst","Technician","Specialist","Manager"]

def dob_for_age(age: int) -> date:
    today = date.today()
    return date(today.year - age, 6, 15)

class Command(BaseCommand):
    help = "Seed demo data: HR admin + 12 fabricated employees + salary profiles."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete existing demo employees before seeding.")

    def handle(self, *args, **opts):
        force = opts["force"]

        # Create HR admin account: HR0001 / password from env or default
        hr_username = "HR0001"
        hr_password = "HR0001-ChangeMe!"
        hr, created = User.objects.get_or_create(username=hr_username, defaults={
            "is_staff": True,
            "is_superuser": True,
            "email": "hr@abc-company.local",
        })
        if created:
            hr.set_password(hr_password)
            hr.save()
            self.stdout.write(self.style.SUCCESS(f"Created HR admin {hr_username} with password: {hr_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"HR admin {hr_username} already exists (password unchanged)."))

        if force:
            Employee.objects.filter(employee_id__startswith="E").delete()

        # Seed 12 employees
        for i in range(12):
            emp_id = f"E{i+1:04d}"
            email = f"employee{i+1:02d}@abc-company.local"

            # Ages 22-55
            dob = dob_for_age(random.randint(22, 55))
            pwd = dob.strftime("%Y%m%d")  # matches "email + DOB" credential idea

            user, u_created = User.objects.get_or_create(username=email, defaults={"email": email, "is_active": True})
            if u_created:
                user.set_password(pwd)
                user.save()

            gender = random.choice([Gender.MALE, Gender.FEMALE])
            pay_type = random.choice([PayType.HOURLY, PayType.SALARY])

            emp, e_created = Employee.objects.get_or_create(employee_id=emp_id, defaults={
                "user": user,
                "department": random.choice(DEPTS),
                "job_title": random.choice(JOBS),
                "first_name": FIRST[i % len(FIRST)],
                "last_name": LAST[i % len(LAST)],
                "sur_name": "",
                "status": EmployeeStatus.ACTIVE,
                "date_of_birth": dob,
                "gender": gender,
                "pay_type": pay_type,
                "company_email": email,
                "address_line_1": f"{100+i} Main St",
                "address_line_2": "",
                "city": "Indianapolis",
                "state": "IN",
                "zip_code": "46204",
            })

            # Create salary profile
            if not hasattr(emp, "salary_profile"):
                if pay_type == PayType.SALARY:
                    base_pay = random.choice([52000, 64000, 78000, 91000])
                else:
                    base_pay = random.choice([18.50, 21.75, 24.00, 28.50])

                SalaryProfile.objects.create(
                    employee=emp,
                    date_hire=date.today() - timedelta(days=random.randint(90, 2000)),
                    salary_type=pay_type,
                    base_pay=base_pay,
                    medical=random.choice([MedicalCoverage.SINGLE, MedicalCoverage.FAMILY]),
                    dependents=random.randint(0, 3),
                )

            self.stdout.write(f"Seeded {emp_id} / {email} (pwd={pwd})")

        self.stdout.write(self.style.SUCCESS("Done."))
