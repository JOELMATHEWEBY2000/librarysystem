from django.contrib import admin
from .models import Loan
# Register your models here.



@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "member",
        "borrow_date",
        "due_date",
        "return_date",
    )

    search_fields = (
        "book__title",
        "member__fullname",
    )

    list_filter = ("borrow_date", "due_date")