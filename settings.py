PLUGIN_NAME = "PAYMENTS"

# 
from django.http.request import HttpRequest
def amount_generator_example(request: HttpRequest, *caller_view_args, **caller_view_kwargs):
    return request.session.get("cart_object", {}).get("total", 0)
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
            }
        }
    }
}