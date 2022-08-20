from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from payments.modules.paypal.signals import *
from payments.settings import PLUGIN_NAME
import braintree
import json
import http.client

def make_payment(request: HttpRequest, *args, **kwargs):
  payload = json.loads(request.body)
  plugin_conf = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME, {})
  gateway = braintree.BraintreeGateway(access_token=plugin_conf.get("access_token")(request, *args, **kwargs))
  #print(payload)
  result = None
  try:
    result = gateway.transaction.sale({
      "amount": plugin_conf.get("amount", lambda request, *args, **kwargs: 0)(request, *args, **kwargs),
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

def make_subscription(request: HttpRequest):
  # TODO: Create subscription workflow
  payload = json.loads(request.body)
  gateway = braintree.BraintreeGateway(access_token="")
  result = None
  try:
    result = gateway.subscription.create({
      "amount": 25,
      "payment_method_nonce": payload["nonce"]
    })
  except:
    pass

  if result is not None and result.is_success:
    print("Is succeess")
  else:
    print("Not success")
  return HttpResponse()

def enlist_payment(request: HttpRequest):
  return HttpResponse()