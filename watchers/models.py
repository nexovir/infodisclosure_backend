from django.db import models
from users.models import BaseModel
from django.contrib.auth.models import User



class ProgramWatcher(BaseModel):
    platform_name = models.CharField(max_length=150 , blank=False , null=False)
    platform_url = models.URLField(blank=False , null=False)
    check_time = models.IntegerField(default=12)
    logo = models.ImageField(upload_to='watchers/programwatcher/logo/' , blank = True , null = True)
    last_checked = models.DateTimeField(blank=True , null=True)
    STATUSES = [
        ('pending', 'Pending'),
        ('running' , 'Running'),    
        ('completed', 'Completed'),  
        ('fail', 'Faild'),    
        ('cancelled', 'Cancelled'),     
    ]
    
    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 
    notify = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.platform_name} - {self.status}"
    
    class Meta :
        verbose_name = 'Program Watcher'
        verbose_name_plural = 'Program Watchers'




class DiscoverdProgram(BaseModel):
    watcher = models.ForeignKey(ProgramWatcher , on_delete=models.PROTECT)
    name = models.CharField(max_length=150 , unique=True)
    url = models.URLField()
    TYPES = [
        ('vdp' , 'VDP'),
        ('rdp' , 'RDP'),
        ('others', 'OTHERS')
    ]
    type = models.CharField(max_length=100 , choices=TYPES , blank=False , null=False)
    discovered_at = models.DateTimeField(auto_now=True)
    LABEL = [
        ('new', 'NEW'),
        ('available' , 'AVAILABLE')
    ]
    label = models.CharField(
        max_length=100,
        choices=LABEL,     
        default="available"
    )

    def __str__(self):
        return f"{self.watcher} : {self.name} -> {self.label}"
    
    class Meta:
        verbose_name = 'Discoverd Program'
        verbose_name_plural = 'Discoverd Programs'






class DiscoverdScope (BaseModel):
    discovered_program = models.ForeignKey(DiscoverdProgram , on_delete=models.CASCADE , )
    name = models.CharField(max_length=150)
    SCOPE_TYPES = [
        ("web", "Web Application"),
        ("wildcard", "Wildcard Domain (*.example.com)"),
        ("mobile", "Mobile Application (iOS / Android)"),
        ("api", "API (REST / GraphQL)"),
        ("web3", "Web3 / Smart Contract / dApp"),
        ("desktop", "Desktop / Thick Client"),
        ("iot", "IoT / Hardware Device"),
        ("cloud", "Cloud Infrastructure (AWS, GCP, etc.)"),
        ("code", "Source Code / Repository"),
        ("infrastructure", "External Infrastructure (IP / DNS / Mail Servers)"),
        ("physical", "Physical Security"),
        ("third_party", "Third-Party Hosted Apps"),
        ("others" , "Others")
    ]

    type = models.CharField(max_length=150 , choices=SCOPE_TYPES)
    in_scope = models.BooleanField(default=True)





class Tool(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'




class AssetWatcher(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tools = models.ManyToManyField(Tool, related_name='watchers')
    last_checked = models.DateTimeField()
    notify = models.BooleanField(default=False)
    
    STATUSES = [
        ('pending', 'Pending'),
        ('running' , 'Running'),    
        ('completed', 'Completed'),  
        ('fail', 'Faild'),    
        ('cancelled', 'Cancelled'),     
    ]

    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 


    def __str__(self):
        return f"{self.user.username} - Tools: {', '.join(tool.name for tool in self.tools.all())}"

    class Meta:
        verbose_name = 'Asset Watcher'
        verbose_name_plural = 'Asset Watchers'





class WatchedWildcard(BaseModel):
    watcher = models.ForeignKey(AssetWatcher , on_delete=models.CASCADE)
    wildcard = models.CharField(max_length=150 , blank=True , null=True)
    last_checked = models.DateTimeField()

    def __str__(self):
        return f"{self.wildcard} - {self.last_checked}"
    
    class Meta:
        verbose_name = 'Watched Wildcard'
        verbose_name_plural = 'Watcher Wildcards'




class DiscoverSubdomain(BaseModel):
    wildcard = models.ForeignKey(WatchedWildcard , on_delete=models.CASCADE)
    subdomain = models.CharField(max_length=150 , blank=True , null=True)
    tool = models.OneToOneField(Tool , on_delete=models.SET_NULL , null=True , blank= True)
    

    def __str__(self):
        return f"{self.subdomain} - {self.tool}"
    
    class Meta :
        verbose_name = 'Discoverd Subdomain'
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
    last_checked = models.DateTimeField()
    STATUSES = [
        ('pending', 'Pending'),
        ('running' , 'Running'),    
        ('completed', 'Completed'),  
        ('fail', 'Faild'),    
        ('cancelled', 'Cancelled'),     
    ]

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
    last_checked = models.DateTimeField()
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
    changed_at = models.DateTimeField()


    def __str__(self):
        return f"{self.watchedjsfile.jsfilewatchlist.name} - {self.changed_at}"

    
    class Meta :
        verbose_name = 'WatchedJSFileChanged'
        verbose_name_plural = 'WatchedJSFileChangeds'


