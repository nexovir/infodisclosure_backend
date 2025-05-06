from django.db import models
from django.contrib.auth.models import User # type: ignore
from users.models import BaseModel
from techniques.models import *
from tools.models import *


class WriteupCategory(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="subcategories" , null = True , blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"




class WriteUp(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writeups")
    title = models.CharField(max_length=255)
    category = models.ForeignKey(WriteupCategory , on_delete=models.CASCADE , related_name='writeup' , blank=False, null=True , default=None)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    content = models.TextField() 
    

    vulnerability_type = models.CharField(max_length=50)
    target_type = models.CharField(max_length=100)  
    tools_used = models.ManyToManyField(Tool , related_name='writeup_tools',  blank = True , null=True)
    techniques = models.ManyToManyField(Techniques, related_name='writeup_techniques', blank=True , null=True) 
    
    # فروش
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    preview_text = models.TextField(blank=True, help_text="Teaser for non-buyers")
    purchase_count = models.PositiveIntegerField(default=0)

    # تنظیمات
    is_public = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta :
        verbose_name = 'WriteUp'
        verbose_name_plural = 'WriteUps'


