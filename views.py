from django.shortcuts import render
from django.conf import settings
from django.urls import re_path, path
from django.http import Http404
from django.http.request import HttpRequest
from django.utils.module_loading import import_string, import_module
from .models import *
#from solo.admin import SingletonModelAdmin
from .settings import PLUGIN_NAME

# Create your views here.
def require_view_payed(func, amount=0, *args, **kwargs):
    """
    Make a view only accessible if the current user has payed a certain amount of money and that payment is validated
        Any payment method supported by this module will allow be supported by this function:
        
        :amount: Indicates the amount of money that you wants to set to protect a view, if 0 is given means any amount is
            enough to bypass this protection
    """
    def wrapped_function(request, *args, **kwargs):
        # TODO Implements this to protect function to be payed before executing them
        return func(request, *args, **kwargs)
    return wrapped_function

def payment_view(request: HttpRequest, *args, **kwargs):
    admin_site = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME).get("context", {}).get("payment_sites", None)
    if admin_site is not None:
        if not request.user.is_authenticated:
            raise Http404()
        admin_site = import_string(admin_site)
    payment_item  = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME).get("admin_pay")
    #context["total"] = 10.0
    #context["name"] = "Hola mundo"
    #context["description"] = "Content"
    context = admin_site.each_context(request) if admin_site else {}
    context.update(payment_item(request, *args, **kwargs))
    return render(request, "admin/payment.html", context=context)
