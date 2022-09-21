from django.apps import AppConfig

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
