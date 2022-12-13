from django.apps import AppConfig
from .signals import _payment_accepted_stalker, _payment_rejected_stalker

class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    def ready(self, *args, **kwargs):
        from .models import Currency, get_currencies
        try:
            for currency in get_currencies():
                Currency.objects.get_or_create(name=currency[0])
        except:
            pass # Ignore it as it must be possible that this is because database is not created yet
        _payment_accepted_stalker()
        _payment_rejected_stalker()
        #from .settings import get_plugin_conf
        #print(get_plugin_conf("context", "targets", ["email", "merchant"]))
