"""
..  module:: sort_ssde_methods
    :synoposis: Returns a ssde queryset based on method (order defined in local_settings.py)

"""

from django import template
from django.db import models
from openremproject.settings import PREFERRED_ORDER_CT_SSDE_METHOD

register = template.Library()

@register.filter
def sort_ssde(qs):
    whens = []
    for sort_index, value in enumerate(PREFERRED_ORDER_CT_SSDE_METHOD):
        whens.append(
            models.When(measurement_method__code_value=value, then=sort_index)
        )
    qs.order_by(models.Case(*whens, output_field=models.IntegerField()))
    return qs
