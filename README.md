# ABC Payroll (Django + TokyoNight)

This repository is a **Python/Django** implementation of the **SDEV268 Payroll Program Development Design and Planning** requirements. 

It includes:
- Login + role separation (**HR Admin** vs **Employee**) 
- Employee demographics screen (admin-only) 
- Salary/benefits screen (admin-only) 
- Employee time entry + PTO (employee) with validations and payroll locking 
- Payroll calculation (admin-only) producing gross/net, deductions pretax, and taxes for both employee and employer 
- CSV export for payroll department printing + HR sign-off workflow placeholder 
- TokyoNight-inspired UI theme (dark blue background, purple/orange accents)

---

## Tech stack

- Python 3.11+ (3.10 works too)
- Django 5.x
- SQLite (default for class project portability)

---

## Project structure

- `payroll_site/` — Django project settings + top-level routes
- `accounts/` — login/logout/dashboard + role helpers
- `employees/` — Employee + SalaryProfile (admin screens)
- `timeentry/` — TimeEntry (employee screen) + locking rules
- `payroll/` — PayrollRun + Paycheck models and calculation services
- `reports_app/` — starter report hub
- `templates/` — TokyoNight UI templates
- `static/css/tokyonight.css` — the theme stylesheet
- `docs/actors_roles.puml` — PlantUML actors & roles diagram

---

## Setup: virtual environment named `.env`

> The **virtual environment folder** is `.env/` (per your requirement).

### Windows (PowerShell)

```powershell
cd payroll_django_tokyonight

py -m venv .env
.env\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

py manage.py makemigrations
py manage.py migrate

# Create demo HR + 12 fabricated employees
py manage.py seed_demo_data

py manage.py runserver
```

### Linux / macOS (bash/zsh)

```bash
cd payroll_django_tokyonight

python3 -m venv .env
source .env/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

# Create demo HR + 12 fabricated employees
python manage.py seed_demo_data

python manage.py runserver
```

Open:
- `http://127.0.0.1:8000/login/`

---

## Demo logins

### HR Admin (required by prompt)

- **User ID:** `HR0001`   
- **Password:** `HR0001-ChangeMe!`

This user is created by:

```bash
python manage.py seed_demo_data
```

### Employees (auto credentials based on email + DOB)

The seed script creates:
- username = `employeeXX@abc-company.local`
- password = `YYYYMMDD` (their DOB)

This follows the project prompt requirement that employee credentials are based on email and date of birth. 

---

## Payroll rules implemented

From the prompt: 

### Time entry rules
- **Salary employees**
  - paid automatically **8 hours Mon–Fri**
  - can only enter **PTO** (no daily work-hour entry)
- **Hourly employees**
  - enter hours per day
  - overtime is **time-and-a-half**
    - **> 8 hours in a day**
    - **any Saturday hours**

### Benefits and taxes
- Medical deduction (pretax):
  - Single: **$50**
  - Family: **$100**
- Dependent stipend:
  - **$45** per dependent (added to gross)

Taxes are calculated on **taxable wages = gross - pretax deductions**:
- State (IN): **3.15%**
- Federal: **7.65%**
- Social Security: **6.2%**
- Medicare: **1.45%**
…and the system stores both **employee** and **employer** portions (as requested).

> Note: This is a **class-project simplification**, not a real-world tax engine.

---

## Security measures (mapped to prompt)

- Mandatory login (Django auth).
- Password hashing (Django built-in).
- Role gating:
  - HR/Admin = `is_staff=True`
  - Employees = normal users linked to an `Employee` record
- CSRF protection for POST forms (Django default).
- After payroll is calculated for a period, time entries in that date range are **locked** (no editing). 

---

## Testing log (suggested workflow)

The prompt requires an initial and completed testing log with validations and screenshots.   
Suggested place to store it:

- `docs/testing_log_initial.md`
- `docs/testing_log_completed.md`

(These files are not generated automatically so your group can tailor them to your own scenarios.)

---

## PlantUML diagram

- File: `docs/actors_roles.puml`

Render it using any PlantUML plugin (VS Code, IntelliJ) or CLI.

Example (if you have PlantUML installed):

```bash
plantuml docs/actors_roles.puml
```

---

## Next extensions (if you want extra credit polish)

- Add an employee search page + filters (department/status/pay type).
- Add a “sign-off” checkbox and audit trail on PayrollRun.
- Export a PDF pay-stub / HR sign-off report.
- Add unit tests for `payroll/services.py` (especially overtime edge cases).
