from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .models import Book
from .forms import BookForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url="member_login")
def book_list(request):
    search = request.GET.get("search", "").strip()

    books = Book.objects.all().order_by("title")

    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(author__icontains=search)
            | Q(isbn__icontains=search)
        )

    return render(request, "books/book_list.html", {
        "books": books,
        "search": search,
    })

@login_required(login_url="member_login")
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully.")
            return redirect("book_list")
    else:
        form = BookForm()

    return render(request, "books/book_form.html", {
        "form": form,
        "title": "Add Book",
    })

@login_required(login_url="member_login")
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully.")
            return redirect("book_list")
    else:
        form = BookForm(instance=book)

    return render(request, "books/book_form.html", {
        "form": form,
        "title": "Edit Book",
    })

@login_required(login_url="member_login")
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully.")
        return redirect("book_list")

    return render(request, "books/book_confirm_delete.html", {
        "book": book,
    })