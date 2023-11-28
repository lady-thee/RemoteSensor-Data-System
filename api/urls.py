from django.urls import path

from api import views

app_name = "api"

urlpatterns = [
    path("users/", views.ListAllUsersAPIView.as_view(), name="users"),
    path("register/", views.UserRegistrationAPIView.as_view(), name="register"),
    path(
        "register_sensor/",
        views.SensorRegistrationAPIView.as_view(),
        name="register sensor",
    ),
]
