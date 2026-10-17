from django.db import models
from django.utils import timezone
from books.models import Book
from members.models import Member


class Loan(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="loans"
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="loans"
    )

    borrow_date = models.DateField(
        default=timezone.localdate
    )

    due_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.book.title} - {self.member.fullname}"

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def is_overdue(self):
        return (
            self.return_date is None
            and self.due_date < timezone.localdate()
        )