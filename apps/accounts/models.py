from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'), 
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)  
    profile_pic = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin_role(self):
        return self.role in ['superadmin', 'admin'] or self.is_superuser
    
    @property
    def is_admin(self):
        return self.role in ['superadmin', 'admin'] or self.is_superuser

    @property
    def is_admin_staff(self):
        return self.role in ['superadmin', 'admin'] or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_parent(self):
        return self.role == 'parent'

    def get_dashboard_url(self):
        role = self.role
        if not role and self.is_superuser:
            role = 'superadmin'
        mapping = {
            'superadmin': '/dashboard/admin/',
            'admin': '/dashboard/admin/',
            'teacher': '/dashboard/teacher/',
            'student': '/dashboard/student/',
            'parent': '/dashboard/parent/',
        }
        return mapping.get(role, '/accounts/profile/')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
