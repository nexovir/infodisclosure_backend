from django.db import models
from django.contrib.auth.models import User
from users.models import BaseModel
# Create your models here.


class Category(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="subcategories" , null = True , blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"




class WriteUp(BaseModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name='writeup' , blank=False, null=True , default=None)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    content = models.TextField()  # Only visible after purchase or if free
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writeups")

    # امنیتی
    vulnerability_type = models.CharField(max_length=50)
    target_type = models.CharField(max_length=100)  # e.g., WebApp, API, Mobile, IoT
    tools_used = models.TextField(help_text="Comma-separated list of tools" , blank = True , null=True)
    techniques = models.TextField(help_text="Comma-separated list of hacking techniques" , blank=True , null=True)
    
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




class Comment(models.Model):
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.writeup.title}"
    


class Rating(models.Model):
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user.username} on {self.writeup.title}"
    



class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Purchase by {self.user.username} for {self.writeup.title}"
    



class Report(models.Model):
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on {self.writeup.title}"
    



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    writeups = models.ManyToManyField(WriteUp, related_name="tags")

    def __str__(self):
        return self.name
    



class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    writeup = models.ForeignKey(WriteUp, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username} for {self.writeup.title}"
    
