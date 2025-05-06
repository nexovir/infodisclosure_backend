from django.contrib import admin
from django.contrib.admin import register
from .models import *
import nested_admin


class SubCategoryInline(nested_admin.NestedTabularInline):
    model = ToolCategory
    fk_name = 'parent'
    extra = 1
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'is_active',)




@register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category' , 'access_token' , 'price' , 'is_free' , 'is_public' , 'approved' , 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active' , 'approved']



@register(ToolCategory)
class ToolCategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title' , 'slug' , 'parent']
    inlines = [SubCategoryInline]
    prepopulated_fields = {'slug': ('title',)}




@register(ToolImage)
class ToolImageAdmin(admin.ModelAdmin):
    list_display = ['tool' , 'image']
