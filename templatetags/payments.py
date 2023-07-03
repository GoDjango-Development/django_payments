from django.conf import settings
from django.urls import reverse
from django.http import Http404
from django.template.context import Context
from payments.settings import PLUGIN_NAME
from functools import lru_cache
try:
  import braintree
except ImportError:
  pass
from django import template
register = template.Library()


class Data:
  is_loaded = False
  counter = 0

@register.simple_tag(takes_context=True)
def get_nonce(context, nonce_name="paypal_render", nonce_types='script'):
  nonce = ""
  if "django_optimizer" in settings.INSTALLED_APPS and "django_optimizer.middleware.CSPMiddleware" in settings.MIDDLEWARE:
    from django_optimizer.templatetags.assets import generate_nonce
    nonce = generate_nonce(nonce_name, nonce_types)
  return nonce

@register.filter()
def normalize_amount(amount: float):
  return format(amount, ".2f") if amount else "0.00"

# 'paypal_make_payment'
@register.simple_tag(takes_context=True)
def on_approve_url(context: Context, context_id=None, payment_type=None, *args, **kwargs):
  payment_type = payment_type or context.get("type", None)
  if payment_type is None or payment_type == "default":
    url = reverse("paypal_make_payment", 
      kwargs=settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {}).get("context", {}).get("urls_kwargs", {}).get(context_id, lambda t: None)(
        context
      )
    )
  elif payment_type == "subscribe":
    url = reverse("paypal_make_subscription", 
      kwargs=settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {}).get("context", {}).get("urls_kwargs", {}).get(context_id, lambda t: None)(
        context
      )
    )
  elif payment_type == "vanilla_default":
    url = reverse("v_paypal_make_payment", 
      kwargs=settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {}).get("context", {}).get("urls_kwargs", {}).get(context_id, lambda t: None)(
        context
      )
    )
  else: 
    raise Http404("Payment Type not found")
  return url

@register.simple_tag()
def get_payment_settings(setting_name=None, *args, **kwargs):
    resp = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, None)
    if setting_name and resp:
      resp = resp.get(setting_name)
    return resp if resp is not None else ""

@register.simple_tag()
def get_auth_token(access_token: str, *args, **kwargs):
  client_token = ""
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  try:
    gateway = braintree.BraintreeGateway(
      config=plugin_conf.get("configuration"),
      access_token=access_token
    )
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
def get_container_uid(index:int=None):
  if index is None:
    Data.counter += 1
  else:
    Data.counter = index
  Data.is_loaded = True
  return "paypalsdk_%s"%Data.counter 

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
