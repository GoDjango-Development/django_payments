from django import template
from django.conf import settings
from django.urls import reverse
from django.template.context import Context
from payments.settings import PLUGIN_NAME
import braintree
register = template.Library()

@register.filter()
def normalize_amount(amount: float):
  imag = int(amount.imag)
  if imag > 99: # Thjs shouldnt be
    raise ValueError("Amount decimal part mustn be higher than 99, actual: %s"%imag)
  amount = int(amount.real)
  return "{0}.{1}".format(amount, imag if imag >= 10 else "{}0".format(imag))

# 'paypal_make_payment'
@register.simple_tag(takes_context=True)
def on_approve_url(context: Context, context_id=None, *args, **kwargs):
  url = reverse("paypal_make_payment", 
    kwargs=settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {}).get("context", {}).get("urls_kwargs", {}).get(context_id, lambda t: None)(
      context
    )
  )
  return url

@register.simple_tag()
def get_payment_settings(setting_name=None, *args, **kwargs):
    resp = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, None)
    if setting_name:
      resp = resp.get(setting_name)
    return resp

@register.simple_tag()
def get_auth_token(access_token: str, *args, **kwargs):
  client_token = ""
  try:
    gateway = braintree.BraintreeGateway(access_token=access_token)
    client_token = gateway.client_token.generate()
  except:
    pass
  return client_token
