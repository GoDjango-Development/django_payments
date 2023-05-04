
from django import template
from ..settings import get_client_token as _get_client_token


register = template.Library()

@register.simple_tag(takes_context=True)
def get_client_token(context):
  try:
    return _get_client_token()
  except:
    return ""
