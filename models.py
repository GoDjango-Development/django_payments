from django.db import models

# Create your models here.
class Pay(models.Model):
    #test = models.CharField(max_length=10, default="holas")
    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payments Methods"