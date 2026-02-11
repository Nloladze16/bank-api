from django.urls import path
from .views import BillView, BillPaymentView, PayBillView,DeleteBillView

urlpatterns = [
    path("pay/", PayBillView.as_view()),
    path("payments/", BillPaymentView.as_view()),
    path("<int:pk>/", DeleteBillView.as_view()),
    path("", BillView.as_view()),
]
