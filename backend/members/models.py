from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
# Create your models here.



class Member(models.Model):
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    mobilenumber = models.CharField(max_length=15)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "argon2$", "bcrypt$")
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class EmailOTP(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    otp_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"OTP for {self.user.username}"