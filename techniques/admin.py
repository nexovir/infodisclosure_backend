from django.contrib import admin
from django.contrib.admin import register
from .models import *
import nested_admin



class SubCategoryInline(nested_admin.NestedTabularInline):
    model = TechniquesCategory
    fk_name = 'parent'
    extra = 1
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'is_active',)




@register(TechniquesCategory)
class CategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'slug', 'parent' , 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SubCategoryInline]
    ordering = ('title',)
    list_per_page = 20
    list_editable = ('is_active',)




@register(Techniques)
class TechniquesAdmin(admin.ModelAdmin):
    list_display = ['id' , 'author' , 'title' , 'category' , 'difficulty'  , 'is_active']
    list_display_links = ['id', 'author',]
    list_editable = ['is_active']
