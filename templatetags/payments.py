from django import template
from django.conf import settings
from django.urls import reverse
from django.template.context import Context
from payments.settings import PLUGIN_NAME
import braintree
register = template.Library()

class Data:
  is_loaded = False
  counter = 0

@register.filter()
def normalize_amount(amount: float):
  if hasattr(amount, "imag"):
    imag = int(amount.imag)
    if imag > 99: # Thjs shouldnt be
      raise ValueError("Amount decimal part must'nt be higher than 99, actual: %s"%imag)
    amount = int(amount.real)
    return "{0}.{1}".format(amount, imag if imag >= 10 else "{}0".format(imag))
  else:
    imag = str(amount).replace(",", ".").split(".")
    if len(imag) > 2:
      raise ValueError("Amount decimal part must'nt be higher than 99, actual: %s"%imag)
    elif len(imag) == 1:
      amount = imag[0] + ".00"
    elif len(imag) == 2:
      amount = "%s.%s"%(imag[0], imag[1] if len(imag[1]) == 2 else imag[1] + "0")
    return amount

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
  except Exception as ex:
    print(ex)
    pass
  # print("real auth_token: ", client_token)
  return client_token

@register.simple_tag()
def is_being_used():
    # Data.is_loaded = True
    return Data.is_loaded


@register.simple_tag()
def get_container_uid():
  Data.counter += 1
  Data.is_loaded = True
  return Data.counter 

@register.simple_tag()
def add(a, b):
  return str(a) + str(b)

@register.simple_tag()
def create_dict(**kwargs):
  return dict(**kwargs)

@register.simple_tag()
def set_val(dict_var: dict, *args, **kwargs):
  #print(dict_var)
  for index in range(0, len(args), 2):
    dict_var[args[index]] = args[index + 1]
  #print(dict_var)
  dict_var.update(**kwargs)
  return ""

@register.filter()
def get(dict_var: dict, key):
  return dict_var.get(key)
