from payments.settings import PLUGIN_NAME
from django.conf import settings
from django.http.request import HttpRequest

class Plan:
    
    def __init__(self, request: HttpRequest=None, *args, **kwargs):
        plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})


    def all(self, *args, **kwargs):
        pass

    def update(self, id: str, *args, **kwargs):
        pass

    def create(self, id: str, 
        name: str, 
        billing_frequency: str, 
        currency_iso_code: str,
        price: str, *args, **kwargs):
        pass

    def get(self, id: str, *args, **kwargs):
        return self.gateway.plan.find(id)

    def get_or_create(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return self.create(*args, **kwargs)
