"""
    Especific configurations for module VANILLA PayPal
    PAYPAL: {
        "enforce_production": False, # defaults to false, this enforce the production environment even if debug is set to True
        "client_id": "the developer client id", # this is used for the communication with the api exactly when generating the access token
        "client_secret": "the developer client secret", # same as above used for accessing the API
    }
"""
from django.conf import settings
from functools import lru_cache
from uuid import uuid4
import time
from django.core.exceptions import ImproperlyConfigured
import http.client, base64, json
from payments.settings import get_plugin
from django_plugins import autoresolve

def get_access_token():
    client_id = autoresolve(get_plugin().get("client_id", None))
    client_secret = autoresolve(get_plugin().get("client_secret", None))
    return _get_access_token(client_id, client_secret)

@lru_cache
def _get_access_token(client_id, client_secret):
    """
        Generates the access token to communicate with the API, the generated Access Token will be then cached and reused without
        doing cache requests... AS settings must'n change during runtime we cache the result of this function...
    """
    print(client_id, client_secret)
    conn = http.client.HTTPSConnection(get_api_url())
    payload = 'grant_type=client_credentials&ignoreCache=true&return_authn_schemes=true&return_client_metadata=true&return_unconsented_scopes=true'
    
    #print(client_id, client_secret)
    if not (client_id and client_secret):
        raise ImproperlyConfigured("Vanilla PayPal requires both client id and client secret but seems like one of those are missing")

    base_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    headers = {
        'Authorization': f'Basic {base_auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    conn.request("POST", "/v1/oauth2/token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    #print(data)
    return data.get("access_token")

def get_client_token():
    conn = http.client.HTTPSConnection(get_api_url())
    payload = json.dumps({
        "customer_id": "%s"%(time.time_ns())
    })
    headers = {
        'Authorization': 'Bearer %s'%(get_access_token()),
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/identity/generate-token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data.get("client_token")

@lru_cache(1024)
def get_uuid(*cacheable_args):
    return uuid4()

@lru_cache
def get_api_url():
    if settings.DEBUG and not get_plugin().get("enforce_production", False):
        return PAYPAL_API_URLS["sandbox"]
    return PAYPAL_API_URLS["production"]

PAYPAL_API_URLS = {
    "production": "api-m.paypal.com",
    "sandbox": "api-m.sandbox.paypal.com"
} 