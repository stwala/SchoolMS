from django.db import models
from apps.accounts.models import User

class Notice(models.Model):
    """Notice Board Announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Target Audiences
    to_admins = models.BooleanField(default=True, verbose_name="Show to Admins")
    to_teachers = models.BooleanField(default=True, verbose_name="Show to Teachers")
    to_students = models.BooleanField(default=True, verbose_name="Show to Students")
    to_parents = models.BooleanField(default=True, verbose_name="Show to Parents")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SchoolSettings(models.Model):
    school_name    = models.CharField(max_length=200, default='SchoolMS')
    logo           = models.ImageField(upload_to='school/logo/', blank=True, null=True)
    favicon        = models.ImageField(upload_to='school/favicon/', blank=True, null=True)
    primary_color  = models.CharField(max_length=7, default='#5a67d8', help_text='Hex color e.g. #5a67d8')
    secondary_color= models.CharField(max_length=7, default='#4c51bf')
    sidebar_color  = models.CharField(max_length=7, default='#ffffff')
    navbar_color   = models.CharField(max_length=7, default='#1a202c')
    address        = models.TextField(blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    website        = models.URLField(blank=True)

    class Meta:
        verbose_name = 'School Settings'

    def __str__(self):
        return self.school_name

    @classmethod
    def get(cls):
        """Always returns the single settings instance."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj