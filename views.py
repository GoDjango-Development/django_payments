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
