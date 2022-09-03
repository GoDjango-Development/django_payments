from django.contrib import admin
from django.utils.module_loading import import_string
from django.conf import settings
from django.urls import re_path
from .models import *
#from solo.admin import SingletonModelAdmin
from .settings import PLUGIN_NAME

    
class SingletonModelAdmin(admin.ModelAdmin):
    change_form_template = "admin/solo/change_form.html"
    object_history_template = "admin/solo/object_history.html"

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def get_urls(self):
        urls = super().get_urls()
        # _meta.model_name only exists on Django>=1.6 -
        # on earlier versions, use module_name.lower()
        try:
            model_name = self.model._meta.model_name
        except AttributeError:
            model_name = self.model._meta.module_name.lower()

        self.model._meta.verbose_name_plural = self.model._meta.verbose_name
        url_name_prefix = '%(app_name)s_%(model_name)s' % {
            'app_name': self.model._meta.app_label,
            'model_name': model_name,
        }
        custom_urls = [
            re_path(r'^history/$',
                    self.admin_site.admin_view(self.history_view),
                    {"model": self.model},
                    name='%s_history' % url_name_prefix),
            re_path(r'^$',
                    self.admin_site.admin_view(self.change_view),
                    {"model": self.model},
                    name='%s_change' % url_name_prefix)
        ]

        # By inserting the custom URLs first, we overwrite the standard URLs.
        return custom_urls + urls

    def response_change(self, request, obj):
        msg = _('%(obj)s was changed successfully.') % {
            'obj': force_str(obj)}
        if '_continue' in request.POST:
            self.message_user(request, msg + ' ' +
                              _('You may edit it again below.'))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../../")

    def change_view(self, request=None, object_id=None, *args, **kwargs):
        #assert False, "Hola mundo"
        return super().change_view(request, object_id, *args, **kwargs)

    @property
    def singleton_instance_id(self):
        return self.model.objects.first().id


# Register your models here.
class PaymentAdmin(SingletonModelAdmin):
    change_form_template = "admin/payment.html"
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        #print(self.urls)

    def render_change_form(self, request, context:dict, *args, **kwargs):
        #print(context)
        payment_item  = settings.INSTALLED_PLUGINS.get(PLUGIN_NAME).get("admin_pay")
        payment_context = payment_item(self, request, context, *args, **kwargs)
        if type(payment_context) is dict:
            context.update(**payment_context)
        else: 
            return payment_context
        #context["total"] = 10.0
        #context["name"] = "Hola mundo"
        #context["description"] = "Content"
        return super().render_change_form(request, context, *args, **kwargs)
    

for admin_site in settings.INSTALLED_PLUGINS.get(PLUGIN_NAME).get("admin_sites", []):
    if type(admin_site) is str:
        admin_site: admin.AdminSite = import_string(admin_site)
    elif callable(admin_site):
        admin_site: admin.AdminSite = admin_site()
    #print(isinstance(admin_site, admin.AdminSite))
    if not isinstance(admin_site, admin.AdminSite):
        raise ImportError("The admin site must be an instance of type django.admin.AdminSite, current:  %s"%admin_site)
    #admin_site: admin.AdminSite
    #admin.site.register(BlankModel, PaymentAdmin)
    admin_site.register(Pay, PaymentAdmin)
    # print(admin_site)
    # print(admin_site.is_registered(BlankModel))