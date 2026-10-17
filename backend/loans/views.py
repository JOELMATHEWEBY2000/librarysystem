from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Loan
from .forms import LoanForm
from books.models import Book

# Create your views here.


def loan_list(request):
    loans = Loan.objects.select_related(
        "book", "member"
    ).order_by("-borrow_date", "-id")

    status = request.GET.get("status", "")

    if status == "borrowed":
        loans = loans.filter(return_date__isnull=True)
    elif status == "returned":
        loans = loans.filter(return_date__isnull=False)
    elif status == "overdue":
        loans = loans.filter(
            return_date__isnull=True,
            due_date__lt=timezone.localdate()
        )

    search = request.GET.get("search", "").strip()

    if search:
        loans = loans.filter(
            Q(book__title__icontains=search)
            | Q(member__fullname__icontains=search)
            | Q(member__user__username__icontains=search)
        )

    return render(request, "loans/loan_list.html", {
        "loans": loans,
        "status": status,
        "search": search,
    })


@transaction.atomic
def borrow_book(request):
    if request.method == "POST":
        form = LoanForm(request.POST)

        if form.is_valid():
            book_id = form.cleaned_data["book"].pk

            # Lock the selected book while borrowing.
            book = get_object_or_404(
                Book.objects.select_for_update(),
                pk=book_id
            )

            if not book.availability_status:
                form.add_error(
                    "book",
                    "This book is no longer available."
                )
            else:
                active_loan = Loan.objects.filter(
                    book=book,
                    return_date__isnull=True
                ).exists()

                if active_loan:
                    form.add_error(
                        "book",
                        "This book already has an active loan."
                    )
                else:
                    loan = form.save(commit=False)
                    loan.book = book
                    loan.borrow_date = timezone.localdate()
                    loan.save()

                    book.availability_status = False
                    book.save(update_fields=["availability_status"])

                    messages.success(
                        request,
                        "Book borrowed successfully."
                    )
                    return redirect("loan_list")
    else:
        form = LoanForm()

    return render(request, "loans/loan_form.html", {
        "form": form,
        "title": "Borrow Book",
    })


@require_POST
@transaction.atomic
def return_book(request, pk):
    loan = get_object_or_404(
        Loan.objects.select_for_update().select_related("book"),
        pk=pk
    )

    if loan.return_date is not None:
        messages.info(request, "This book has already been returned.")
        return redirect("loan_list")

    loan.return_date = timezone.localdate()
    loan.save(update_fields=["return_date"])

    book = Book.objects.select_for_update().get(pk=loan.book_id)
    book.availability_status = True
    book.save(update_fields=["availability_status"])

    messages.success(request, "Book returned successfully.")
    return redirect("loan_list")
