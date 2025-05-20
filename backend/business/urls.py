from django.urls import path
from .views import get_all_vehicles, get_vehicle_details

urlpatterns = [
    path('vehicles/', get_all_vehicles, name='get_all_vehicles'),
    path('vehicle_details/', get_vehicle_details, name="get_vehicle_details")
]
