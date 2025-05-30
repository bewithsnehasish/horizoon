from django.urls import path

from authentication.views import (
    add_client_details,
    get_client_details,
    google_login,
    login,
    register,
    get_renter_details
)

urlpatterns = [
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("google-login/", google_login, name="google_login"),
    path("add-details/", add_client_details, name="add_client_details"),
    path("get-client-details/", get_client_details, name="get_client_details"),
    path('get_renter_details/', get_renter_details, name="get_renter_details")
]
