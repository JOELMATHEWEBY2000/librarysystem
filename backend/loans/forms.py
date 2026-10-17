
from django import forms
from django.utils import timezone

from .models import Loan
from books.models import Book
from members.models import Member


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["book", "member", "due_date"]

        widgets = {
            "book": forms.Select(attrs={
                "class": "form-select"
            }),
            "member": forms.Select(attrs={
                "class": "form-select"
            }),
            "due_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["book"].queryset = Book.objects.filter(
            availability_status=True
        )

        self.fields["member"].queryset = Member.objects.all().order_by(
            "fullname"
        )

        self.fields["member"].label_from_instance = (
            lambda member: f"{member.fullname} ({member.username})"
        )

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        if due_date < timezone.localdate():
            raise forms.ValidationError(
                "Due date cannot be in the past."
            )

        return due_date

