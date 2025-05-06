from django.db import models
from users.models import BaseModel
from django.contrib.auth.models import User



class ProgramWatcher(BaseModel):
    platforms = models.JSONField(default=list)
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
        return f"{self.platforms} - {self.status}"
    
    class Meta :
        verbose_name = 'Program Watcher'
        verbose_name_plural = 'Program Watchers'




class DiscoverdProgram(BaseModel):
    watcher = models.ForeignKey(ProgramWatcher , on_delete=models.PROTECT)
    name = models.CharField(max_length=150 , )
    url = models.URLField()
    max_payout = models.DecimalField(max_digits=12 , decimal_places=2 , default=0.00)
    min_payout = models.DecimalField(max_digits=12 , decimal_places=2 , default=0.00)
    discovered_at = models.DateTimeField()
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.watcher} : {self.name} -> {self.is_new}"
    
    class Meta:
        verbose_name = 'Program Watcher'
        verbose_name_plural = 'Program Watchers'






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




class JSFileWatchList(BaseModel):
    jsfilewatcher = models.ForeignKey(JSFileWatcher , on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    