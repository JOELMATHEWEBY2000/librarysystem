from django.db import models

# Create your models here.


class Book(models.Model):

    CATEGORY_CHOICES = [
        ("fiction", "Fiction"),
        ("nonfiction", "Non-Fiction"),
        ("science", "Science"),
        ("technology", "Technology"),
        ("history", "History"),
        ("education", "Education"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=20, unique=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    availability_status = models.BooleanField(default=True)

    def __str__(self):
        return self.title