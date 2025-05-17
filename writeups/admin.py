from django.contrib import admin
from django.contrib.admin import register
import nested_admin
from .models import *


class SubCategoryInline(nested_admin.NestedTabularInline):
    model = WriteupCategory
    fk_name = 'parent'
    extra = 1
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'is_active',)



@register(WriteupCategory)
class CategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'slug', 'parent' , 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SubCategoryInline]
    ordering = ('title',)
    list_per_page = 20
    list_editable = ('is_active',)


@register(WriteUp)
class WriteUpAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WriteUp._meta.fields if field.name not in ('slug','short_description' , 'content' , 'preview_text')] + ['like_count', 'comment_count']
    list_editable = ['approved' , 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('id',)
    list_per_page = 20
