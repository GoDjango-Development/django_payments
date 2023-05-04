from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.db.models import Model
from django.core.exceptions import ImproperlyConfigured
from payments.modules.paypal.signals import *
from payments.settings import PLUGIN_NAME
from payments.modules.paypal.models.plan import Plan
from django_plugins import import_string
from functools import lru_cache
from asgiref.sync import async_to_sync
import braintree
import json

@lru_cache
def get_configuration():
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  configuration = plugin_conf.get("configuration")
  if type(configuration) is str:
    configuration:Model = import_string(configuration)
    if issubclass(configuration, Model):
      configuration = braintree.Configuration(
        braintree.Environment.Sandbox if settings.DEBUG else braintree.Environment.Production,
        merchant_id=getattr(configuration.objects.first(), "merchant_id", None),
        public_key=getattr(configuration.objects.first(), "public_key"),
        private_key=getattr(configuration.objects.first(), "private_key"),
      )
    else:
      raise ImproperlyConfigured("configuration must be either a braintree.Configuration object or a model containing public and private key and optionally merchant id")
  return configuration

def make_payment(request: HttpRequest, *args, **kwargs):
  payload = json.loads(request.body)
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  
  gateway = braintree.BraintreeGateway(
    config=get_configuration(),
    access_token=plugin_conf.get("access_token")(request, *args, **kwargs)
  )
  result = None
  try:
    result = gateway.transaction.sale({
      "amount": plugin_conf.get("amount", lambda request, *args, **kwargs: 0)(request, *args, **kwargs),
      # FIXME Also set the currency here as if not this site is vulnerable to fake currency payment
      "payment_method_nonce": payload["nonce"]
    })
  except:
    pass

  if result is not None and result.is_success:
    payment_accepted.send(result, **{
      "request": request,
      "args": args,
      "kwargs": kwargs
    })
    return HttpResponseRedirect("/")
    # return Success Page
  else:
    payment_rejected.send(result, **{
      "request": request,
      "args": args,
      "kwargs": kwargs
    })
    return HttpResponseRedirect("/")

def make_subscription(request: HttpRequest, plan_id: str, *args, **kwargs):
  payload = json.loads(request.body)
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  gateway = braintree.BraintreeGateway(
    config=get_configuration(),
    access_token=plugin_conf.get("access_token")(request, *args, **kwargs),
  )
  result = None
  details = payload.get("details", {})
  customer_result = gateway.customer.create({
    "first_name": details.get("firstName", None),
    "last_name": details.get("lastName", None),
    "email": details.get("paypal", None),
    "phone": details.get("phone", None),
    "fax": details.get("fax", None),
    "website": details.get("website", None),
  })
  pm_result = gateway.payment_method.create({
      "customer_id": customer_result.customer.id,
      "payment_method_nonce": payload["nonce"]
    }
  )
  plan = Plan.objects.get(plan_id)
  try:
    if pm_result.is_success:
      result = gateway.subscription.create({
        "payment_method_token": pm_result.payment_method.token,
        "plan_id": plan.id,
      })
    print(gateway.subscription)
  except Exception as ex:
    print("Launched an error")
    print(ex)
  if result is not None and result.is_success:
    print("Is succeess")
  else:
    print("Not success")
  return HttpResponse()

def cancel_subscription(request: HttpRequest, subscription_id: int, *args, **kwargs):
  payload = json.loads(request.body)
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  gateway = braintree.BraintreeGateway(
    config=get_configuration(),
    access_token=plugin_conf.get("access_token")(request, *args, **kwargs)
  )
  #print(payload)
  result = None
  try:
    result = gateway.subscription.cancel(subscription_id=subscription_id)
  except:
    pass

  if result is not None and result.is_success:
    subscription_canceled.send(result, **{
      "request": request,
      "args": args,
      "kwargs": kwargs
    })
    return HttpResponseRedirect("/")
    # return Success Page
  return HttpResponseNotModified()
