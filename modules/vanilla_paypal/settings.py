"""
    Especific configurations for module VANILLA PayPal
    PAYPAL: {
        "enforce_production": False, # defaults to false, this enforce the production environment even if debug is set to True
        "client_id": "the developer client id", # this is used for the communication with the api exactly when generating the access token
        "client_secret": "the developer client secret", # same as above used for accessing the API
    }
"""
from logging import info
from django.conf import settings
from functools import lru_cache
from uuid import uuid4
import time
from django.core.exceptions import ImproperlyConfigured
import base64

import requests
from payments.settings import get_plugin
from django_plugins import autoresolve

def get_access_token():
    info("Trying to obtain the Access Token")
    client_id = autoresolve(get_plugin().get("client_id", None))
    client_secret = autoresolve(get_plugin().get("client_secret", None))
    info("Obtained client id and Client Secret")
    return _get_access_token(client_id, client_secret)

def _get_access_token(client_id, client_secret):
    """
        Generates the access token to communicate with the API, the generated Access Token will be then cached and reused without
        doing cache requests... AS settings must'n change during runtime we cache the result of this function...
    """

    if not (client_id and client_secret):
        raise ImproperlyConfigured("Vanilla PayPal requires both client id and client secret but seems like one of those are missing")

    base_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    info("BASE_AUTH: %s"%base_auth)
    for retry in range(5):
        resp = requests.post(
            get_api_url()+"/v1/oauth2/token", 
            data={'grant_type':'client_credentials',
                # 'ignoreCache':'true',
                # 'return_authn_schemes':'true',
                # 'return_client_metadata':'true',
                # 'return_unconsented_scopes':'true'
            },
            headers = {
                'Authorization': f'Basic {base_auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        if resp.ok:
            break
        else:
            info(resp.status_code, resp.content)
            time.sleep(3)
    else:
        raise ValueError("Couldnt retrieve the access_token due to an unkown reason")
    data = resp.json()
    info("Response Data: %s %s"%(resp.status_code, data))
    access_token = data.get("access_token")
    if not access_token:
        info(f"No access token? ERROR: {access_token}")
    return access_token
def get_client_token():
    resp = requests.post(
        get_api_url()+"/v1/identity/generate-token", 
        data={"customer_id": "%s"%(time.time_ns())},
        headers={
            'Authorization': 'Bearer %s'%(get_access_token()),
            'Content-Type': 'application/json'
        }
    )
    return resp.json().get("client_token")

@lru_cache(1024)
def get_uuid(*cacheable_args):
    return uuid4()

def get_api_url():
    if settings.DEBUG and not get_plugin().get("enforce_production", False):
        return "https://%s"%PAYPAL_API_URLS["sandbox"]
    return "https://%s"%PAYPAL_API_URLS["production"]

PAYPAL_API_URLS = {
    "production": "api-m.paypal.com",
    "sandbox": "api-m.sandbox.paypal.com"
} 