from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "payment_type",
        "status",
        "amount",
        "currency",
        "booking",
        "lounge_access",
        "stripe_session_id",
        "created_at",
    )

    list_filter = (
        "payment_type",
        "status",
        "currency",
        "created_at",
    )

    search_fields = (
        "user__email",
        "stripe_session_id",
        "booking__id",
        "lounge_access__id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )