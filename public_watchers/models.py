from django.db import models
from users.models import BaseModel
from django.contrib.contenttypes.fields import GenericRelation
from interactions.models import Like, Comment


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
        ('failed', 'Failed'),    
    ]
    
    status = models.CharField(max_length=150, choices=STATUSES, default='pending') 
    notify = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.platform_name} - {self.status}"

    class Meta :
        verbose_name = 'Program Watcher'
        verbose_name_plural = 'Program Watchers'




class DiscoverdProgram(BaseModel):
    
    watcher = models.ForeignKey(ProgramWatcher , on_delete=models.PROTECT, related_name='watcher_program' )
    name = models.CharField(max_length=200)
    url = models.URLField()
    TYPES = [
        ('vdp' , 'VDP'),
        ('rdp' , 'RDP'),
        ('others', 'OTHERS')
    ]
    type = models.CharField(max_length=100 , choices=TYPES , blank=False , null=False)
    discovered_at = models.DateTimeField(auto_now=True)
    likes = GenericRelation(Like)

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
    
    def like_count(self):
        return self.likes.count()

    class Meta:
        ordering = ['-discovered_at']
        unique_together = ('watcher', 'name')
        verbose_name = 'Discoverd Program'
        verbose_name_plural = 'Discoverd Programs'




class DiscoverdScope (BaseModel):
    discovered_program = models.ForeignKey(DiscoverdProgram , on_delete=models.CASCADE , )
    name = models.CharField(max_length=500)
    SCOPE_TEC_TYPES = [
        ("ai_model" , "AI Model"),
        ("web", "Web Application"),
        ("wildcard", "Wildcard Domain (*.example.com)"),
        ("mobile", "Mobile Application (iOS / Android)"),
        ("api", "API (REST / GraphQL)"),
        ("web3", "Web3 / Smart Contract / dApp"),
        ("desktop", "Desktop / Thick Client"),
        ("iot", "IoT / Hardware Device"),
        ("cloud", "Cloud Infrastructure (AWS, GCP, etc.)"),
        ("code", "Source Code / Repository"),
        ("infrastructure", "External Infrastructure (CIDR / DNS / Mail Servers)"),
        ("physical", "Physical Security"),
        ("third_party", "Third-Party Hosted Apps"),
        ("others" , "Others")
    ]
    SCOPE_TYPES = [
        ('in_scope' , 'In Scope'),
        ('out_of_scope' , 'Out Of Scope')
    ]
    LABEL = [
        ('new', 'NEW'),
        ('available' , 'AVAILABLE')
    ]
    label = models.CharField(
        max_length=100,
        choices=LABEL,     
        default="available"
    )
    type = models.CharField(max_length=150 , choices=SCOPE_TEC_TYPES)
    scope_type = models.CharField(max_length=100 , choices=SCOPE_TYPES , blank=True , null=True)


    class Meta:
        verbose_name = 'Discoverd Scope'
        verbose_name_plural = 'Discoverd Scopes'


