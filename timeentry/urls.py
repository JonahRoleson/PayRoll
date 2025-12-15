from django.urls import path
from . import views

urlpatterns = [
    path("", views.MyTimeEntryListView.as_view(), name="my_time_entries"),
    path("new/", views.TimeEntryCreateView.as_view(), name="timeentry_new"),
    path("<int:pk>/edit/", views.TimeEntryUpdateView.as_view(), name="timeentry_edit"),
    path("<int:pk>/submit/", views.submit_timeentry, name="timeentry_submit"),
]
