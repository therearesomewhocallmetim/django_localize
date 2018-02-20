# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_localize.urls import urlpatterns as django_localize_urls

urlpatterns = [
    url(r'^', include(django_localize_urls, namespace='django_localize')),
]
