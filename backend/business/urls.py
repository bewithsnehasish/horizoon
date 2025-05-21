from django.urls import path

from .views import (
    availability_calendar,
    cancel_order,
    check_availability,
    create_booking,
    get_all_vehicles,
    get_vehicle_details,
    list_user_orders,
)

urlpatterns = [
    path("vehicles/", get_all_vehicles, name="get_all_vehicles"),
    path("vehicle_details/", get_vehicle_details, name="get_vehicle_details"),
    path("user_orders/", list_user_orders, name="list_user_orders"),
    path("booking/", create_booking, name="create_booking"),
    path("booking/availability/", check_availability, name="check_availability"),
    path(
        "booking/availability/calendar/",
        availability_calendar,
        name="availability_calendar",
    ),
    path("booking/cancel/", cancel_order, name="cancel_order"),
]
