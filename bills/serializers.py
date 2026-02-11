from rest_framework import serializers
from .models import Bill, BillPayment


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            "id",
            "user",
            "name",
            "amount",
            "is_active",
            "last_paid_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "is_active","last_paid_at", "created_at"]


class BillPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPayment
        fields = ["id", "bill", "amount", "paid_at"]
        read_only_fields = ["id", "bill", "amount", "paid_at"]


class PayBillSerializer(serializers.Serializer):
    bill_id = serializers.IntegerField()
