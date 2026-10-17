from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import transaction
from .models import Member
from .forms import MemberRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import secrets

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Member, EmailOTP
from .forms import MemberRegistrationForm
# Create your views here.



def register(request):
    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            otp = f"{secrets.randbelow(1000000):06d}"

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=data["username"],
                        email=data["email"],
                        password=data["password"],
                        is_active=False
                    )

                    Member.objects.create(
                        user=user,
                        fullname=data["fullname"],
                        mobilenumber=data["mobilenumber"]
                    )

                    EmailOTP.objects.update_or_create(
                        user=user,
                        defaults={
                            "otp_hash": make_password(otp),
                            "expires_at": timezone.now()
                            + timedelta(minutes=5),
                            "attempts": 0
                        }
                    )

                send_mail(
                    subject="Your Email Verification OTP",
                    message=(
                        f"Hello {data['fullname']},\n\n"
                        f"Your verification OTP is: {otp}\n\n"
                        "This OTP expires in 5 minutes.\n"
                        "Do not share this code with anyone."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[data["email"]],
                    fail_silently=False
                )

                request.session["pending_verification_user_id"] = user.pk

                return redirect("verify_otp")

            except Exception:
                form.add_error(
                    None,
                    "Registration or email delivery failed. "
                    "Please try again or contact support."
                )

    else:
        form = MemberRegistrationForm()

    return render(
        request,
        "members/register.html",
        {"form": form}
    )



def register_success(request):
    return render(
        request,
        "members/register_success.html"
    )

def verify_otp(request):
    user_id = request.session.get(
        "pending_verification_user_id"
    )

    if not user_id:
        return redirect("register")

    user = User.objects.filter(
        pk=user_id,
        is_active=False
    ).first()

    if user is None:
        request.session.pop(
            "pending_verification_user_id", None
        )
        return redirect("member_login")

    otp_record = EmailOTP.objects.filter(
        user=user
    ).first()

    if otp_record is None:
        return render(request, "members/verify_otp.html", {
            "error": "OTP not found. Please register again."
        })

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()

        if timezone.now() >= otp_record.expires_at:
            otp_record.delete()

            return render(request, "members/verify_otp.html", {
                "error": "OTP expired. Please request a new code."
            })

        if otp_record.attempts >= 5:
            return render(request, "members/verify_otp.html", {
                "error": "Too many attempts. Please request a new code."
            })

        otp_record.attempts += 1
        otp_record.save(update_fields=["attempts"])

        if not (
            len(otp) == 6
            and otp.isascii()
            and otp.isdigit()
            and check_password(otp, otp_record.otp_hash)
        ):
            return render(request, "members/verify_otp.html", {
                "error": "Invalid OTP. Please try again."
            })

        user.is_active = True
        user.save(update_fields=["is_active"])

        otp_record.delete()

        request.session.pop(
            "pending_verification_user_id", None
        )

        return redirect("member_login")

    return render(request, "members/verify_otp.html")

@require_POST
def resend_otp(request):
    user_id = request.session.get(
        "pending_verification_user_id"
    )

    user = User.objects.filter(
        pk=user_id,
        is_active=False
    ).first() if user_id else None

    if user is None:
        return redirect("register")

    otp = f"{secrets.randbelow(1000000):06d}"

    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp_hash": make_password(otp),
            "expires_at": timezone.now() + timedelta(minutes=5),
            "attempts": 0
        }
    )

    try:
        send_mail(
            "Your New Verification OTP",
            f"Your new OTP is {otp}. It expires in 5 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
    except Exception:
        return render(request, "members/verify_otp.html", {
            "error": "Email delivery failed. Please try again."
        })

    return render(request, "members/verify_otp.html", {
        "message": "A new OTP has been sent to your email."
    })


def member_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("book_list")

        return render(request, "members/login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "members/login.html")


@login_required(login_url="member_login")
def member_dashboard(request):
    member = request.user.member

    return render(request, "members/dashboard.html", {
        "member": member
    })


def member_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("member_login")

    return redirect("member_dashboard")