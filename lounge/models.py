from django.conf import settings
from django.db import models
from location.models import Airport
from ticket.models import Ticket


class Lounge(models.Model):
    name = models.CharField(max_length=100)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="lounges")
    location_description = models.CharField(max_length=150, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    access_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.airport}"


class LoungeAccess(models.Model):
    class AccessType(models.TextChoices):
        BUSINESS_CLASS = "business_class", "Business Class"
        LOYALTY_PROGRAM = "loyalty_program", "Loyalty Program"
        BANK_CARD = "bank_card", "Bank Card"
        PAID_ACCESS = "paid_access", "Paid Access"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lounge_accesses")
    lounge = models.ForeignKey(Lounge, on_delete=models.CASCADE, related_name="accesses")
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name="lounge_accesses")

    access_type = models.CharField(max_length=30, choices=AccessType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.user} - {self.lounge} ({self.get_access_type_display()})"
