from django.urls import path
from . import views

urlpatterns = [
    path("", views.EmployeeListView.as_view(), name="employee_list"),
    path("new/", views.EmployeeCreateView.as_view(), name="employee_new"),
    path("<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee_edit"),
    path("<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee_delete"),

    path("<int:employee_pk>/salary/", views.SalaryProfileUpsertView.as_view(), name="salary_upsert"),
]
