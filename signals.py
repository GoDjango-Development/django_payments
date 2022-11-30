from django.core.signals import Signal
from payments.modules.ethereum.signals import (
    payment_accepted as eth_pay_accepted, 
    payment_rejected as eth_pay_rejected
)

from payments.modules.paypal.signals import (
    subscription_accepted as paypal_sub_accepted,
    subscription_rejected as paypal_sub_rejected,
    subscription_canceled as paypal_sub_canceled
)

def _payment_accepted_stalker():
    def inform_global(*args, **kwargs):
        payment_accepted.send(*args, **kwargs)
    eth_pay_accepted.connect(inform_global)
    paypal_sub_accepted.connect(inform_global)


payment_accepted = Signal()
payment_rejected = Signal()

subscription_accepted = Signal()
subscription_rejected = Signal()
subscription_canceled = Signal()
