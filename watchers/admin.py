from django.contrib import admin
from .models import (
    ProgramWatcher, DiscoverdProgram, DiscoverdScope,
    Tool, AssetWatcher, WatchedWildcard, DiscoverSubdomain,
    SubdomainHttpx, JSFileWatcher, JSFileWatchList,
    WatchedJSFile, WatchedJSFileChanged
)

# Inlines

class DiscoverdScopeInline(admin.TabularInline):
    model = DiscoverdScope
    extra = 0


class DiscoverdProgramInline(admin.TabularInline):
    model = DiscoverdProgram
    extra = 0
    show_change_link = True


class WatchedWildcardInline(admin.TabularInline):
    model = WatchedWildcard
    extra = 0


class DiscoverSubdomainInline(admin.TabularInline):
    model = DiscoverSubdomain
    extra = 0


class JSFileWatchListInline(admin.TabularInline):
    model = JSFileWatchList
    extra = 0
    show_change_link = True


class WatchedJSFileInline(admin.TabularInline):
    model = WatchedJSFile
    extra = 0


class WatchedJSFileChangedInline(admin.TabularInline):
    model = WatchedJSFileChanged
    extra = 0


# Admins

@admin.register(ProgramWatcher)
class ProgramWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform_name', 'status', 'last_checked', 'notify')
    list_filter = ('status', 'notify')
    search_fields = ('platforms',)
    ordering = ('-last_checked',)
    inlines = [DiscoverdProgramInline]
    readonly_fields = ('last_checked','created_at', 'updated_at')


@admin.register(DiscoverdProgram)
class DiscoverdProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'type','lable', 'discovered_at')
    list_filter = ('lable', 'type')
    search_fields = ('name', 'url')
    ordering = ('-discovered_at',)
    list_per_page = 20
    inlines = [DiscoverdScopeInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DiscoverdScope)
class DiscoverdScopeAdmin(admin.ModelAdmin):
    list_display = ('id', 'discovered_program', 'name', 'type', 'in_scope')
    list_filter = ('type', 'in_scope')
    search_fields = ('name',)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(AssetWatcher)
class AssetWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'last_checked', 'notify')
    list_filter = ('status', 'notify')
    search_fields = ('user__username',)
    ordering = ('-last_checked',)
    inlines = [WatchedWildcardInline]


@admin.register(WatchedWildcard)
class WatchedWildcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'watcher', 'wildcard', 'last_checked')
    search_fields = ('wildcard',)
    inlines = [DiscoverSubdomainInline]


@admin.register(DiscoverSubdomain)
class DiscoverSubdomainAdmin(admin.ModelAdmin):
    list_display = ('id', 'wildcard', 'subdomain', 'tool')
    search_fields = ('subdomain',)
    list_filter = ('tool',)


@admin.register(SubdomainHttpx)
class SubdomainHttpxAdmin(admin.ModelAdmin):
    list_display = ('id', 'discovered_subdomain', 'status_code', 'title', 'server', 'has_ssl', 'ip_address', 'port')
    list_filter = ('status_code', 'has_ssl', 'port')
    search_fields = ('discovered_subdomain__subdomain', 'ip_address', 'title')


@admin.register(JSFileWatcher)
class JSFileWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'last_checked', 'notify')
    list_filter = ('status', 'notify')
    search_fields = ('user__username',)
    inlines = [JSFileWatchListInline]


@admin.register(JSFileWatchList)
class JSFileWatchListAdmin(admin.ModelAdmin):
    list_display = ('id', 'jsfilewatcher', 'name')
    search_fields = ('name',)
    inlines = [WatchedJSFileInline]


@admin.register(WatchedJSFile)
class WatchedJSFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'jsfilewatchlist', 'file_url', 'has_changed', 'last_checked')
    search_fields = ('file_url',)
    list_filter = ('has_changed',)
    inlines = [WatchedJSFileChangedInline]


@admin.register(WatchedJSFileChanged)
class WatchedJSFileChangedAdmin(admin.ModelAdmin):
    list_display = ('id', 'watchedjsfile', 'changed_at')
    search_fields = ('watchedjsfile__file_url',)
    readonly_fields = ('old_hash', 'new_hash', 'diff_snipped', 'changed_at')
