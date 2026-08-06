from django.db import models

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    student = models.ForeignKey('people.Student', on_delete=models.CASCADE, related_name='attendances')
    student_class = models.ForeignKey('academics.StudentClass', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='present')
    remarks = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"
