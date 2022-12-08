import braintree
from payments.settings import PLUGIN_NAME
from django.conf import settings
from django.http.request import HttpRequest

class Plan:
    
    def __init__(self, request: HttpRequest=None, *args, **kwargs):
        plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
        self.gateway = braintree.BraintreeGateway(
            config=plugin_conf.get("configuration"),
            access_token=plugin_conf.get("access_token")(request, *args, **kwargs),
        )


    def all(self, *args, **kwargs):
        return self.gateway.plan.all()

    def update(self, id: str, *args, **kwargs):
        return self.gateway.plan.update(id, params={**kwargs})

    def create(self, id: str, 
        name: str, 
        billing_frequency: str, 
        currency_iso_code: str,
        price: str, *args, **kwargs):
        return self.gateway.plan.create({
            "id": id,
            "name": name,
            "billing_frequency": str(billing_frequency),
            "currency_iso_code": currency_iso_code,
            "price": str(price),
            **kwargs
        })

    def get(self, id: str, *args, **kwargs):
        return self.gateway.plan.find(id)

    def get_or_create(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return self.create(*args, **kwargs)
