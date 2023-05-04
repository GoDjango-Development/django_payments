from django.urls import path
from .views import payment_view

urlpatterns = [
    path("pay/", payment_view, name="payments_pay"),
]