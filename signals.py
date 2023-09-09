from django.core.signals import Signal
from payments.modules.ethereum.signals import (
    payment_accepted as eth_pay_accepted, 
    payment_rejected as eth_pay_rejected
)

from payments.modules.paypal.signals import (
    payment_accepted as paypal_pay_accepted,
    payment_rejected as paypal_pay_rejected,
    subscription_accepted as paypal_sub_accepted,
    subscription_rejected as paypal_sub_rejected,
    subscription_canceled as paypal_sub_canceled
)

from payments.modules.vanilla_paypal.signals import (
    payment_accepted as vpaypal_pay_accepted,
    payment_rejected as vpaypal_pay_rejected,
    subscription_accepted as vpaypal_sub_accepted,
    subscription_canceled as vpaypal_sub_canceled,
    subscription_rejected as vpaypal_sub_rejected   
)

def _payment_accepted_stalker():
    def inform_global(*args, **kwargs): # informs global signal of children signal is received
        del kwargs["signal"] # strip out previous signal 
        payment_accepted.send(*args, **kwargs)
    eth_pay_accepted.connect(inform_global)
    paypal_pay_accepted.connect(inform_global)
    vpaypal_pay_accepted.connect(inform_global)


def _payment_rejected_stalker():
    def inform_global(*args, **kwargs): # informs global signal of children signal is received
        del kwargs["signal"] # strip out previous signal 
        payment_rejected.send(*args, **kwargs)
    eth_pay_rejected.connect(inform_global)
    paypal_pay_rejected.connect(inform_global)
    vpaypal_pay_rejected.connect(inform_global)


payment_accepted = Signal()
payment_rejected = Signal()

subscription_accepted = Signal()
subscription_rejected = Signal()
subscription_canceled = Signal()
