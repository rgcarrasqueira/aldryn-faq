# -*- coding: utf-8 -*-
from adminsortable.admin import SortableAdmin
from cms.admin.placeholderadmin import PlaceholderAdmin
from django.contrib import admin
from distutils.version import LooseVersion
from hvad.admin import TranslatableAdmin

import cms

from . import models


class CategoryAdmin(TranslatableAdmin):

    list_display = ['__unicode__', 'all_translations']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': ['name']}),
        ]
        return fieldsets


class QuestionAdmin(PlaceholderAdmin, SortableAdmin):

    render_placeholder_language_tabs = False
    list_display = ['title', 'language', 'category']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ['title', 'language', 'category']
            })
        ]

        # show placeholder field if not CMS 3.0
        if LooseVersion(cms.__version__) < LooseVersion('3.0'):
            fieldsets.append(
                ('Answer', {
                    'classes': ['plugin-holder', 'plugin-holder-nopage'],
                    'fields': ['answer']
                }))

        return fieldsets

admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Category, CategoryAdmin)
