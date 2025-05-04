from django.db import models
from django.contrib.auth.models import User




class BaseModel (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True




class Profile(BaseModel):
    # General
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    is_available_for_collab = models.BooleanField(default=False)

    # Skills and Focus
    skills = models.JSONField(default=list)  # e.g. ['xss', 'rce', 'recon']
    experience_level = models.CharField(
        max_length=30,
        choices=[
            ("newbie", "Newbie"),                  # کاملاً تازه‌کار
            ("junior", "Junior Hacker"),           # تازه‌کار ولی با کمی تجربه
            ("intermediate", "Intermediate"),      # سطح متوسط
            ("advanced", "Advanced"),              # مسلط و حرفه‌ای
            ("pro", "Pro Hacker"),                 # در حد متخصص واقعی
            ("elite", "Elite"),                    # برتر و باتجربه زیاد
            ("legend", "Legendary"),               # افسانه‌ای، سطح خیلی بالا
            ("ghost", "Ghost (Stealth Expert)"),   # مخفی‌کار و پیشرفته
        ],
        default="newbie"
    )

    # Links
    website = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    # Social
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    # Activity
    score = models.IntegerField(default=0)  # کل امتیاز
    rank = models.CharField(max_length=50, default="rookie")  # rookie, elite, master, legend...


    def __str__(self):
        return f"{self.display_name}'s profile"
