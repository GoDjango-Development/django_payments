from django.urls import path, include, re_path
from .controllers.payment import *

urlpatterns = [
    path("paypal/",  make_payment, name="paypal_make_payment"),
    path("paypal/subscribe/",  make_subscription, name="paypal_make_subscription"),
]
