from django.contrib import admin
from django.contrib.admin import register
from .models import *

@register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Like._meta.fields ]
    list_per_page = 20
    search_fields = ['user' , 'content_type']


@register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.fields]
    list_per_page = 20
    search_fields = ['user' , 'content_type', 'text']