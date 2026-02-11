from .models import Bill, BillPayment
from .serializers import BillSerializer, BillPaymentSerializer, PayBillSerializer
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db import transaction
from django.utils import timezone


@extend_schema(tags=["Bills"], description="List all active bills for the authenticated user or create a new bill.")
class BillView(generics.ListCreateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.bills.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Bills"], description="Retrieve all payment records for the authenticated user's bills.")
class BillPaymentView(generics.ListAPIView):
    serializer_class = BillPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BillPayment.objects.filter(bill__user=self.request.user)


@extend_schema(
    tags=["Bills"],
    request=PayBillSerializer,
    description="Pay a bill for the authenticated user.",
)
class PayBillView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PayBillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bill_id = serializer.validated_data["bill_id"]

        try:
            bill = Bill.objects.get(id=bill_id, user=request.user)
        except Bill.DoesNotExist:
            return Response(
                {"detail": "Bill not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if bill.is_active is False:
            return Response(
                {"detail": "Bill is not active"}, status=status.HTTP_400_BAD_REQUEST
            )
        today = timezone.now().date()

        if bill.last_paid_at and (
            bill.last_paid_at.year == today.year
            and bill.last_paid_at.month == today.month
        ):
            return Response(
                {"detail": "Bill has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account = request.user.bank_account

        if account.balance < bill.amount:
            return Response(
                {"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            account.balance -= bill.amount
            account.save()

            bill.last_paid_at = timezone.now().date()
            bill.save()

            BillPayment.objects.create(bill=bill, amount=bill.amount)

            return Response(
                {"detail": "Bill paid successfully"}, status=status.HTTP_200_OK
            )

@extend_schema(
    tags=["Bills"],
    description="Soft delete a bill by setting it as inactive.",
)
class DeleteBillView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request,pk):
        try:
            bill = Bill.objects.get(id=pk, user=request.user)
        except Bill.DoesNotExist:
            return Response(
                {"detail": "Bill not found"}, status=status.HTTP_404_NOT_FOUND
            )

        bill.is_active = False
        bill.save()

        return Response(
            {"detail": "Bill deleted successfully"}, status=status.HTTP_200_OK
        )
