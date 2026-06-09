from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .serializers import CreateCheckoutSessionSerializer

import stripe

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status

import logging

logger = logging.getLogger(__name__)

from .services import create_checkout_session, handle_successful_checkout, handle_expired_checkout


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateCheckoutSessionSerializer)
    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        checkout_url = create_checkout_session(
            user=request.user,
            payment_type=serializer.validated_data["payment_type"],
            booking_id=serializer.validated_data.get("booking_id"),
            lounge_access_id=serializer.validated_data.get("lounge_access_id"),
        )

        return Response({"checkout_url": checkout_url})
    
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(exclude=True)
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )

        except ValueError as e:
            logger.error("Stripe webhook invalid payload: %s", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except stripe.error.SignatureVerificationError as e:
            logger.error("Stripe webhook invalid signature: %s", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "Stripe webhook received. Event type: %s",
            event["type"],
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            payment = handle_successful_checkout(session)

            logger.info(
                "Stripe checkout completed. Payment %s marked as paid.",
                payment.id,
            )

        if event["type"] == "checkout.session.expired":
            session = event["data"]["object"]

            payment = handle_expired_checkout(session)

            logger.info(
                "Stripe checkout expired. Payment %s marked as expired.",
                payment.id,
            )


        return Response({"status": "success"})