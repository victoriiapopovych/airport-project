from django.db import models
from django.conf import settings

from ticket.models import Booking
from lounge.models import LoungeAccess


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    class TypeChoices(models.TextChoices):
        BOOKING = "BOOKING", "Booking Payment"
        LOUNGE = "LOUNGE", "Lounge Access Payment"

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    payment_type = models.CharField(max_length=20, choices=TypeChoices.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")

    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    lounge_access = models.ForeignKey(LoungeAccess, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")

    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} ({self.payment_type}) - {self.status}"