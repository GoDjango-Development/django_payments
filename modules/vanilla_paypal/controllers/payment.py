from logging import info
from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from payments.modules.vanilla_paypal.signals import *
from payments.settings import get_plugin_conf, get_plugin
from payments.modules.vanilla_paypal.models.plan import Plan
from payments.modules.vanilla_paypal.settings import get_api_url, get_access_token, get_uuid
from django_plugins.utils import Wrapper
import http.client, json, uuid

def get_order_detail(order_id):
  conn = http.client.HTTPSConnection(get_api_url())
  payload = ''
  headers = {
    'Authorization': 'Bearer %s'%get_access_token()
  }
  conn.request("GET", "/v2/checkout/orders/%s"%order_id, payload, headers)
  res = conn.getresponse()
  data = res.read()
  return json.loads(data.decode("utf-8"))

def get_authorization_details(capture_id):
  conn = http.client.HTTPSConnection("api-m.sandbox.paypal.com")
  payload = ''
  headers = {
    'Authorization': 'Bearer %s'%get_access_token()
  }
  conn.request("GET", "/v2/payments/captures/%s"%capture_id, payload, headers)
  res = conn.getresponse()
  data = json.loads(res.read().decode("utf-8"))
  return data


def ensure_payment_to(order_id, payee_email=None, merchant_id=None, only_once=False):
  """
    If only_once is set to False (the default) search for only once in a purchase unit
    
  """
  if not (payee_email or merchant_id): # means False and False 
    return True # as there is nothing to evaluate
  order_details = get_order_detail(order_id)
  if not order_details:
    return False # cause not order details were given
  purchase_units = order_details.get("purchase_units", None)
  if not purchase_units:
    return False

  for purchase_unit in purchase_units:
    if (
      ((payee_email and purchase_unit["payee"]["email_address"] == payee_email) or not payee_email) and # if payee_email is declared and does match evaluate next also evaluate if is not defined and its True value is False 
      ((merchant_id and purchase_unit["payee"]["merchant_id"] == merchant_id) or not merchant_id) # if merchant id is declared and it does match or if not defined
    ):
      if only_once: # if you only want 1 match 
        return True
    elif not only_once: # if you do not want only 1 and one doesnt match return False as the whole purchase units doesnt match
      return False
  if only_once: # meaning never it reach the condition of return True inside the loop
    return False
  return True # meaning never it reach the condition of return False inside the loop

def make_payment(request: HttpRequest, *args, **kwargs):
  # Non critical section
  data = json.loads(request.body)
  amount = get_plugin().get("amount", lambda request, *args, **kwargs: 0)(request, *args, **kwargs)
  if hasattr(amount, "__iter__"): # if its iterable
    currency = amount[1]
    amount = amount[0]
  else:
    currency = "USD"
  email, merchant = None, None # get_plugin_conf("context", "targets", ["email", "merchant"], default={})
  wrapper = Wrapper()
  signal_named = {
    "order_id": None,
    "authorization_id": data.get("authorization_id"),
    "request": request,
    "args": args,
    "kwargs": kwargs,
    "amount": amount,
    "currency": currency,
    "email": email,
    "merchant_id": merchant,
    "paypal_response": data,
    "response": wrapper # allows to be modified inside the connected signals
  }
  # Start critical zone
  try:
    conn = http.client.HTTPSConnection(get_api_url())
    payload = json.dumps({
      "amount": {
        "value": amount,
        "currency_code": currency
      },
      "final_capture": True,
      # below can be understand like Ice Box possible feature, if this module becomes popular or we do need this at some point we will add the features
      # "invoice_id": "1670017495",
      # "note_to_payer": "If the ordered color is not available, we will substitute with a different color free of charge.",
      # "soft_descriptor": "Bob's Custom Sweaters"
    })
    headers = {
      'Content-Type': 'application/json',
      'PayPal-Request-Id': '%s'%get_uuid(request.session.session_key), # gets a different uuid for each session, this fields allows paypal not to recompute twice the same request, read more here https://developer.paypal.com/reference/guidelines/idempotency/ 
      'Prefer': 'return=representation',
      'Authorization': 'Bearer %s'%get_access_token() # gets the access token to communicate with API 
    }
    conn.request("POST", "/v2/payments/authorizations/%s/capture"%(data.get("authorization_id")), 
      payload, 
      headers
    )
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8")) # this overrides current data and now when ensuring payment we are ensuring with the real order id associated to the autorization id
    info("RES %s %s"%(data, res.status))
    order_id = get_authorization_details(data.get("id")).get("supplementary_data", {}).get("related_ids", {}).get("order_id")
    wrapper.anon_push(HttpResponse(status=res.status))
    signal_named = {
      "order_id": order_id,
      "authorization_id": data.get("authorization_id"),
      "request": request,
      "args": args, 
      "kwargs": kwargs,
      "amount": amount,
      "currency": currency,
      "email": email,
      "merchant_id": merchant,
      "paypal_response": data,
      "response": wrapper # allows to be modified inside the connected signals
    }
    if (200 <= res.status < 300 and
      ensure_payment_to(order_id, payee_email=email, merchant_id=merchant)
    ):
      if data.get("status", None) == "COMPLETED":
        payment_accepted.send(make_payment, **signal_named)
        return wrapper.reference_stack["anonymous"][0]
  except:
    pass # Ignore errors and instead call later to rejection logic 
  payment_rejected.send(make_payment, **signal_named)
  return wrapper.reference_stack["anonymous"][0]

def make_subscription(request: HttpRequest, plan_id: str, *args, **kwargs):
  pass

def cancel_subscription(request: HttpRequest, subscription_id: int, *args, **kwargs):
  pass
