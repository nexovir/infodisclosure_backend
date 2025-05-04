from django.contrib import admin
from .models import *
from django.contrib.admin import register


# Register your models here.

@register(Workplace)
class WorkplaceAdmin (admin.ModelAdmin):

    list_display = ['id', 'user', 'title', 'created_at' , 'updated_at']
    list_filter = ('created_at', 'updated_at')
    list_per_page = 20
    ordering = ('-id',)
    list_select_related = ['user']
