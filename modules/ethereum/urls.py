from django.urls import path, include, re_path
from .controllers.payment import *

urlpatterns = [
    path("ethereum_pay",  make_payment, name="ethereum_pay")
]
