from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "isbn",
            "category",
            "availability_status",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter book title",
            }),
            "author": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter author name",
            }),
            "isbn": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter ISBN",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "availability_status": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }