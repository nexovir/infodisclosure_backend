from django.contrib import admin
from .models import *
from django.contrib.admin import register


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]
