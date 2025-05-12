from django.db import models
from users.models import BaseModel
from django.contrib.auth.models import User




STATUSES = [
    ('pending', 'Pending'),         
    ('running', 'Running'),      
    ('completed', 'Completed'),    
    ('failed', 'Failed'),           
    ('cancelled', 'Cancelled'),     
]



LABELS = [
        ('new', 'NEW'),
        ('available' , 'AVAILABLE')
    ]


class AssetWatcher(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE , null=True , blank=True)
    notify = models.BooleanField(default=False)


    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 


    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Asset Watcher'
        verbose_name_plural = 'Asset Watchers'





class Tool(models.Model):
    TOOLS_NAME = [
        ('amass' , 'Amass'),
        ('subfinder' , 'Subfinder'),
        ('dns_bruteforce' , 'DNS Bruteforce')
    ]
    tool_name = models.CharField(max_length=120, choices=TOOLS_NAME , default='subfinder')

    def __str__(self):
        return self.tool_name

    class Meta:
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'





class WatchedWildcard(BaseModel):
    watcher = models.ForeignKey(AssetWatcher , on_delete=models.CASCADE , related_name= 'wildcards')
    wildcard = models.CharField(max_length=150 , blank=True , null=True)
    tools = models.ManyToManyField(Tool)

    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 

    def __str__(self):
        return f"{self.wildcard} - {self.watcher.user.username}"
    
    class Meta:
        verbose_name = 'Watched Wildcard'
        verbose_name_plural = 'Watcher Wildcards'




class DiscoverSubdomain(BaseModel):
    wildcard = models.ForeignKey(WatchedWildcard, on_delete=models.CASCADE, related_name='subdomain')
    subdomain = models.CharField(max_length=150, blank=True, null=True)
    tool = models.ForeignKey(Tool, on_delete=models.SET_NULL, null=True, blank=True)

    label = models.CharField(choices=LABELS, max_length=50, default='new')

    def __str__(self):
        return f"{self.subdomain} - {self.wildcard.watcher.user.username}"

    class Meta:
        verbose_name = 'Discovered Subdomain'
        verbose_name_plural = 'Discovered Subdomains'






class SubdomainHttpx(BaseModel):
    discovered_subdomain = models.OneToOneField(DiscoverSubdomain , on_delete=models.CASCADE)
    status_code = models.IntegerField()
    title = models.CharField(null=True , blank=True , max_length=500)
    server = models.CharField(max_length=150 , null=True , blank=True)
    technologies = models.JSONField(default=list)
    has_ssl = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=120 , null=True , blank=True)
    port = models.IntegerField()


    def __str__(self):
        return f"{self.discovered_subdomain.subdomain} - {self.status_code}"

    
    class Meta :
        verbose_name = 'Subdomain Httpx'
        verbose_name_plural = 'Subdomain Httpxes'






class JSFileWatcher (BaseModel):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    last_checked = models.DateTimeField(blank=True , null=True)
    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 
    notify = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {self.status}"

    
    class Meta :
        verbose_name = 'JSFileWatcher'
        verbose_name_plural = 'JSFileWatchers'






class JSFileWatchList(BaseModel):
    jsfilewatcher = models.ForeignKey(JSFileWatcher , on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    
    def __str__(self):
        return f"{self.jsfilewatcher.user.username} - {self.name}"

    
    class Meta :
        verbose_name = 'JSFileWatchList'
        verbose_name_plural = 'JSFileWatchLists'





class WatchedJSFile(BaseModel):
    jsfilewatchlist = models.ForeignKey(JSFileWatchList , on_delete=models.CASCADE)
    file_url = models.URLField(max_length=150)
    current_hash = models.CharField(max_length=150 , blank=True , null=True)
    last_checked = models.DateTimeField(blank=True , null=True)
    has_changed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.jsfilewatchlist.name} - {self.last_checked}"

    
    class Meta :
        verbose_name = 'WatchedJSFile'
        verbose_name_plural = 'WatchedJSFiles'




class WatchedJSFileChanged(BaseModel):
    watchedjsfile = models.ForeignKey(WatchedJSFile , on_delete=models.CASCADE)
    old_hash = models.CharField(max_length=150 , blank=False , null=True)
    new_hash = models.CharField(max_length=150 , blank=False , null=True)
    diff_snipped = models.CharField(max_length=150 , blank=False , null=True)
    changed_at = models.DateTimeField(blank=True , null=True)


    def __str__(self):
        return f"{self.watchedjsfile.jsfilewatchlist.name} - {self.changed_at}"

    
    class Meta :
        verbose_name = 'WatchedJSFileChanged'
        verbose_name_plural = 'WatchedJSFileChangeds'


