from django_plugins import get_plugin as _get_plugin, get_pulgin_conf as _get_plugin_conf
from functools import partial

PLUGIN_NAME = "PAYMENTS"

get_plugin = partial(_get_plugin, PLUGIN_NAME)
get_plugin_conf = partial(_get_plugin_conf, PLUGIN_NAME)

from django.http.request import HttpRequest
def amount_generator_example(request: HttpRequest, *caller_view_args, **caller_view_kwargs):
    return [request.session.get("cart_object", {}).get("total", 0), "USD"]
    
def access_token_generator_example(request: HttpRequest, *caller_view_args, **caller_view_kwargs):
    return caller_view_kwargs.get("user").get("access_token", "testaccess")

INSTALLED_PLUGINS = {
    PLUGIN_NAME: {
        "version": "1.0.0",
        "agreement": "Agreement from settings",
        "amount": amount_generator_example,
        "access_token": access_token_generator_example,
        "context": {
            "urls_kwargs": {
                "var_identifier": lambda context: {
                    "url_var_for_reverser": "any data you want"
                }
            },
            "targets": {
                "email": "",
                "merchant": ""
            },
            "payment_sites": "example.admin.site" 
        }
    }
}