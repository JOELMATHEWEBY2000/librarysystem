from django.contrib import admin
from .models import Book

# Register your models here.



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "category",
        "availability_status",
    )

    search_fields = ("title", "author", "isbn")
    list_filter = ("category", "availability_status")