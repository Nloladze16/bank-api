from django.db import models
from django.contrib.auth.models import User


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bills")
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)
    last_paid_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.amount}"


class BillPayment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill.name} - {self.amount} paid on {self.paid_at.strftime('%Y-%m-%d')}"
