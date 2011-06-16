"""
The following is a quick little template filter that can be used in the Django admin site to change the app_labels to whatever you like. Override the content/breadcrumb blocks of templates such as admin/index.html, admin/app_index.html, admin/change_form.html, and admin/change_list.html and apply the filter to wherever {{ app.name }} is used.
"""

### myapp/templatetags/adminfilters.py ###

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='custom_app_label')
@stringfilter
def custom_app_label(value):
    custom_app_labels = {
        'fs_doc': 'FFFS', # key is default app_label, value is new app_label
        # Rinse, repeat 
    }
    return custom_app_labels.get(value, value)
