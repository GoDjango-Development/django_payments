from django.core.signals import Signal

payment_accepted = Signal()
payment_rejected = Signal()
subscription_accepted = Signal()
subscription_rejected = Signal()
subscription_canceled = Signal()