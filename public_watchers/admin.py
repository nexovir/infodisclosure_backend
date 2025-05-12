from django.contrib import admin
from .models import *

# Inlines

class DiscoverdScopeInline(admin.TabularInline):
    model = DiscoverdScope
    extra = 0


class DiscoverdProgramInline(admin.TabularInline):
    model = DiscoverdProgram
    extra = 0
    show_change_link = True



# Admins

@admin.register(ProgramWatcher)
class ProgramWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform_name', 'status', 'last_checked','is_active', 'notify')
    list_filter = ('status', 'notify')
    search_fields = ('platforms',)
    ordering = ('-last_checked',)
    list_editable = ['is_active']
    inlines = [DiscoverdProgramInline]
    readonly_fields = ('last_checked','created_at', 'updated_at')


@admin.register(DiscoverdProgram)
class DiscoverdProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'type', 'watcher__platform_name','label', 'discovered_at')
    list_filter = ('label', 'type' , 'watcher__platform_name')
    search_fields = ('name', 'url')
    ordering = ('-discovered_at',)
    list_per_page = 20
    inlines = [DiscoverdScopeInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DiscoverdScope)
class DiscoverdScopeAdmin(admin.ModelAdmin):
    list_display = ('name', 'discovered_program__name','discovered_program__watcher__platform_name','label','type', 'scope_type')
    list_filter = ('type', 'scope_type' , 'discovered_program__watcher__platform_name' , 'label')
    search_fields = ('name',)
