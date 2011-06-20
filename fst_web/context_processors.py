# -*- coding: UTF-8 -*-
from django.conf import settings


def add_request_vars(request):
    return {
        'organization': dict(
                name=settings.FST_ORG_NAME,
                name_possessive=settings.FST_ORG_NAME_POSSESSIVE),
        'site': dict(
                url=settings.FST_SITE_URL,
                instance_url=settings.FST_INSTANCE_URL
        )
    }
