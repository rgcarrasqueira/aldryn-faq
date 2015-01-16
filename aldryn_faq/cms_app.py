# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from .menu import FaqCategoryMenu


class FaqApp(CMSApp):
    name = _('FAQ')
    urls = ['aldryn_faq.urls']
    menus = [FaqCategoryMenu]
    app_name = 'aldryn_faq'

apphook_pool.register(FaqApp)
