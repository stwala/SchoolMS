from django.db import models

# Create your models here.
from django.db import models
from apps.accounts.models import User


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_no = models.CharField(max_length=20, unique=True)
    date_of_birth= models.DateField()
    gender       = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group  = models.CharField(max_length=5, blank=True, null=True)
    student_class= models.ForeignKey('academics.StudentClass', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    address      = models.TextField(blank=True)
    enroll_date  = models.DateField(auto_now_add=True)
    is_active    = models.BooleanField(default=True)
    grades_visible = models.BooleanField(default=False, help_text='Show grades to parent when fees are paid.')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_no})"

    class Meta:
        ordering = ['admission_no']


class Teacher(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    staff_id      = models.CharField(max_length=20, unique=True, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True)
    specialization= models.CharField(max_length=100, blank=True)
    assigned_classes = models.ManyToManyField('academics.StudentClass', related_name='teachers', blank=True)
    join_date     = models.DateField(auto_now_add=True)
    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"

    class Meta:
        ordering = ['staff_id']


class Parent(models.Model):
    RELATION_CHOICES = [('father','Father'),('mother','Mother'),('guardian','Guardian')]

    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    relation  = models.CharField(max_length=20, choices=RELATION_CHOICES)
    occupation= models.CharField(max_length=100, blank=True)
    students  = models.ManyToManyField(Student, related_name='parents', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.relation})"