from django.db import models
from django.utils.translation import gettext as _


def get_currencies():
    return (
        ("AUD", "Australian dollar"),
        ("BRL", "Brazilian real 2"),
        ("CAD", "Canadian dollar"),
        ("CNY", "Chinese Renmenbi 3"),
        ("CZK", "Czech koruna"),
        ("DKK", "Danish krone"),
        ("EUR", "Euro"),
        ("HKD", "Hong Kong dollar"),
        ("HUF", "Hungarian forint 1"),
        ("ILS", "Israeli new shekel"),
        ("JPY", "Japanese yen 1"),
        ("MYR", "Malaysian ringgit 3"),
        ("MXN", "Mexican peso"),
        ("TWD", "New Taiwan dollar 1"),
        ("NZD", "New Zealand dollar"),
        ("NOK", "Norwegian krone"),
        ("PHP", "Philippine peso"),
        ("PLN", "Polish złoty"),
        ("GBP", "Pound sterling"),
        ("RUB", "Russian ruble"),
        ("SGD", "Singapore dollar"),
        ("SEK", "Swedish krona"),
        ("CHF", "Swiss franc"),
        ("THB", "Thai baht"),
        ("USD", "United States dollar"),
    )

# Create your models here.
#class Pay(models.Model):
    #include_in_migrations = False
    #test = models.CharField(max_length=10, default="holas")
#    class Meta:
#        verbose_name = "Payment Method"
#        verbose_name_plural = "Payments Methods"

class Currency(models.Model):
    name = models.CharField(_("Currency representation"), max_length=3, choices=get_currencies(), default="")
    
    @classmethod
    def get_default(cls, ):
        return cls.objects.first()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")