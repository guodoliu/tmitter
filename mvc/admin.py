# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import User, UserAdmin, Area, AreaAdmin, Category, CategoryAdmin, Note, NoteAdmin


admin.site.register(User, UserAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Note, NoteAdmin)
