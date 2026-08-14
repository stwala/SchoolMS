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


class ClassNamingRule(models.Model):
    CATEGORIES = [
        ('grade', 'Grade'),
        ('standard', 'Standard'),
        ('form', 'Form'),
        ('custom', 'Custom'),
    ]

    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary'),
        ('junior', 'Junior Secondary'),
        ('secondary', 'Senior Secondary'),
    ]

    RANKING_CHOICES = [
        ('marks', 'Total Marks'),
        ('points', 'Points'),
    ]

    school_settings = models.ForeignKey(SchoolSettings,on_delete=models.CASCADE, related_name='class_naming_rules')
    from_grade = models.PositiveSmallIntegerField()
    to_grade = models.PositiveSmallIntegerField()
    naming_convention = models.CharField(max_length=20,choices=CATEGORIES,default='grade' )
    custom_name = models.CharField(max_length=50,blank=True)
    education_level = models.CharField(max_length=20,choices=EDUCATION_LEVEL_CHOICES)
    ranking_method = models.CharField(max_length=20,choices=RANKING_CHOICES,default='marks')

    class Meta:
        ordering = ['from_grade']

    def __str__(self):
        return f"{self.from_grade}-{self.to_grade}: {self.get_naming_convention_display()}/{self.get_education_level_display()}"

    @classmethod
    def for_grade(cls, grade_level):
        school_settings = SchoolSettings.get()

        return cls.objects.filter(
            school_settings=school_settings,
            from_grade__lte=grade_level,
            to_grade__gte=grade_level
        ).first()
