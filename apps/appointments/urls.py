from django.urls import path

from appointments import views

urlpatterns = [
    path("", views.appointment_create_api_view, name="create"),
    path("<int:appointment_id>/", views.appointment_detail_api_view, name="detail"),
]
