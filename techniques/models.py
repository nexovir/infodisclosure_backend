from django.db import models
from users.models import BaseModel
from tools.models import Tool
from django.contrib.auth.models import User



class TechniquesCategory(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="subcategories" , null = True , blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"




class Techniques(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="techniques" , null=True , blank=True)
    title = models.CharField(max_length=150, unique=True, help_text="The name or title of the technique.")
    description = models.TextField(help_text="Detailed description of the technique and how it works.")
    category = models.ForeignKey(TechniquesCategory , blank=True , null=True , on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=50, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], help_text="The difficulty level of the technique.")
    related_tools = models.ManyToManyField(Tool , blank=True, related_name='techniques', help_text="Tools commonly used with this technique.")
    proof_of_concept = models.TextField(blank=True, null=True, help_text="Proof of concept or example of the technique in action.")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Technique'
        verbose_name_plural = 'Techniques'