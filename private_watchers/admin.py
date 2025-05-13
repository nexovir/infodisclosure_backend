from django.contrib import admin
from .models import *


class WatchedWildcardInline(admin.TabularInline):
    model = WatchedWildcard
    extra = 0
    show_change_link = True



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






@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'tool_name')
    search_fields = ('tool_name',)



@admin.register(AssetWatcher)
class AssetWatcherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status','updated_at', 'notify')
    list_filter = ('status', 'notify')
    search_fields = ('user__username',)
    ordering = ('-updated_at',)
    inlines = [WatchedWildcardInline]



@admin.register(WatchedWildcard)
class WatchedWildcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'watcher', 'wildcard', 'status' ,'get_all_tools', 'updated_at')
    search_fields = ('wildcard',)

    def get_all_tools(self, obj):
        return ", ".join([tool.tool_name for tool in obj.tools.all()])
    get_all_tools.short_description = "Tools"



@admin.register(DiscoverSubdomain)
class DiscoverSubdomainAdmin(admin.ModelAdmin):
    list_display = ('id', 'wildcard', 'subdomain', 'tool' , 'label' , 'created_at' , 'updated_at')
    search_fields = ('subdomain',)
    ordering = ('updated_at',)
    list_filter = ('tool','wildcard__watcher__user__username' , 'label')



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

