from django.urls import path
from . import views

urlpatterns = [
    path("api/upload/", views.process_file, name="upload-api"),
    path("api/submit-order/", views.submit_order, name="submit-order"),
    path("", views.upload_form_view, name="upload-form"),
]
