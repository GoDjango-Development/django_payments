from django.urls import path, include, re_path
from .controllers.payment import *

urlpatterns = [
    path("v-paypal/",  make_payment, name="v_paypal_make_payment"),
    path("v-paypal/subscribe/",  make_subscription, name="v_paypal_make_subscription"),
]
