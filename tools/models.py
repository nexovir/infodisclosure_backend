from django.db import models
from users.models import BaseModel
from django.contrib.auth.models import User





class ToolCategory(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self' ,null=True , blank=True , on_delete=models.CASCADE, related_name='subcategories')


    def __str__(self):
        return self.title
    

    class Meta:
        verbose_name = 'Tool Category'
        verbose_name_plural = 'Tool Categories'
        ordering = ['title']





class Tool(BaseModel):
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=False , null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tools")
    category = models.ForeignKey(ToolCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tools')
    slug = models.SlugField(unique=True )

    upload_file = models.FileField(upload_to='tools/files/', blank=True, null=True)

    preview_text = models.TextField(blank=False , null=False)
    demo_video_file = models.FileField(upload_to='tools/demo/videos/', blank=True, null=True)
    demo_video_url = models.URLField(blank=True, null=True)

    github_repo_url = models.URLField(blank=False, null=False)
    access_token = models.CharField(max_length=255, blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    purchase_count = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False)

    is_public = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'
        ordering = ['-created_at']





class ToolImage(BaseModel):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tools/images/' , blank=True , null=False)

    def __str__(self):
        return f"Image for {self.tool.title}"

    class Meta:
        verbose_name = 'Tool Image'
        verbose_name_plural = 'Tool Images'
        ordering = ['-created_at']