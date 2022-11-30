from django.core.signals import Signal

payment_accepted = Signal()
payment_rejected = Signal()