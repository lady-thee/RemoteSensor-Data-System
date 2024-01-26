from django.urls import path

from api import views

app_name = 'api'

urlpatterns = [
    # User URLs to connect to User API endpoints
    path('users/', views.ListAllUsersAPIView.as_view(), name='users'),
    path('register/', views.UserRegistrationAPIView.as_view(), name='register'), 
    path('register/sensor/', views.SensorRegistrationAPIView.as_view(), name='register-sensor'),
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('profile/', views.RetrieveUpdateDeleteUserAPIView.as_view(), name='profile'),
    
    # Sensor URLS to connect to Sensor API endpoints
    path('sensor/api/', views.SensorDataAPIView.as_view(), name='sensor'),
    path('list/sensors/', views.ListAllSensorsAPIView.as_view(), name='sensors'),
    path('sensors/data/', views.SensorDataDetailAPIView.as_view(), name='data'),
    path('sensors/', views.RetrieveUpdateDeleteSensorAPIView.as_view(), name='sensors'),
    path('sensors/delete/<str:pk>/', views.RetrieveUpdateDeleteSensorAPIView.as_view(), name='sensor-delete'),
    path('sensors/edit/<str:pk>/', views.RetrieveUpdateDeleteSensorAPIView.as_view(), name='sensor-update'),
    path('sensor/<str:pk>/', views.RetrieveSensorAPIView.as_view(), name='sensor')
]

