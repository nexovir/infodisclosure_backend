from django.contrib import admin
from .models import ProgramWatcher, DiscoverdProgram, DiscoverdScope


class DiscoverdScopeInline(admin.TabularInline):
    model = DiscoverdScope
    extra = 0
    fields = ('name', 'type', 'in_scope')
    readonly_fields = ('name', 'type', 'in_scope')
    can_delete = False
    show_change_link = False


class DiscoverdProgramInline(admin.StackedInline):
    model = DiscoverdProgram
    extra = 0
    fields = ('name', 'url', 'min_payout', 'max_payout', 'discovered_at', 'is_new')
    readonly_fields = ('name', 'url', 'min_payout', 'max_payout', 'discovered_at', 'is_new')
    can_delete = False
    show_change_link = True


@admin.register(ProgramWatcher)
class ProgramWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'notify', 'last_checked', 'platforms_display')
    list_filter = ('status', 'notify')
    search_fields = ('platforms',)
    ordering = ('-last_checked',)
    inlines = [DiscoverdProgramInline]

    def platforms_display(self, obj):
        return ", ".join(obj.platforms)
    platforms_display.short_description = "Platforms"


@admin.register(DiscoverdProgram)
class DiscoverdProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'watcher', 'min_payout', 'max_payout', 'discovered_at', 'is_new')
    list_filter = ('is_new', 'discovered_at')
    search_fields = ('name', 'url')
    ordering = ('-discovered_at',)
    inlines = [DiscoverdScopeInline]


@admin.register(DiscoverdScope)
class DiscoverdScopeAdmin(admin.ModelAdmin):
    list_display = ('name', 'discovered_program', 'type', 'in_scope')
    list_filter = ('type', 'in_scope')
    search_fields = ('name',)
    ordering = ('discovered_program', 'type')
