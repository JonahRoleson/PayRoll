from django.urls import path
from . import views

urlpatterns = [
    path("hash-demo/", views.password_hash_demo, name="password_hash_demo"),
]
