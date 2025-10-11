from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from config.responses import register_api_exception_handlers
from users.views import router as user_router

api_v2 = NinjaAPI(
    version="1.0.1",
    title="Inflow API v2",
    description="APIs for Inflow, formally known as Sensorfusion",

)

register_api_exception_handlers(api_v2)

api_v2.add_router('users/', user_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/', api_v2.urls)
]

