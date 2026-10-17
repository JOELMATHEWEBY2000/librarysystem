from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "register/success/",
        views.register_success,
        name="register_success"
    ),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("login/", views.member_login, name="member_login"),
    path("dashboard/", views.member_dashboard, name="member_dashboard"),
    path("logout/", views.member_logout, name="member_logout"),
]