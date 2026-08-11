from django.db import models

class AcademicSession(models.Model):
    """Academic Session (e.g. 2025/2026)"""
    name = models.CharField(max_length=100, unique=True)
    current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic Term (e.g. 1st Term, 2nd Term, 3rd Term)"""
    name = models.CharField(max_length=50, unique=True)
    current = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Academic Subject (e.g. Mathematics, English)"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    LEVEL_CHOICES = [
        ('primary', "Primary"),
        ('junior', "Junior Secondary"),
        ('secondary', "Senior Secondary"),
    ]

    # RANKING_METHODS =[
    #     ('marks',"Total Marks"),
    #     ('points',"Points"),
    # ]
    """Class or Room (e.g. Grade 10-A, JSS 1)"""
    name = models.CharField(max_length=20, unique=True)
    grade_level = models.PositiveSmallIntegerField()
    stream = models.CharField(max_length=50, blank=True, null=True)
    education_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='primary')
    subjects = models.ManyToManyField(Subject, related_name='classes', blank=True)
    # ranking_method = models.CharField(max_length=20, choices=RANKING_METHODS, default='marks')

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {self.grade_level}{self.stream or ''}"

    @property
    def ranking_method(self):
        return 'marks' if self.grade_level <= 9 else 'points'


class Grade(models.Model):
    """Student exam and test marks / results"""
    student = models.ForeignKey('people.Student', on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='grades')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, related_name='grades')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='grades')
    
    test_score = models.PositiveIntegerField(default=0)
    exam_score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'subject', 'session', 'term')
        ordering = ['subject']

    def total_score(self):
        return self.test_score + self.exam_score

    def grade_letter(self):
        score = self.total_score()
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'

    def remark(self):
        gl = self.grade_letter()
        mapping = {
            'A': 'Excellent',
            'B': 'Good',
            'C': 'Fair',
            'D': 'Unsatisfactory',
            'F': 'Failing',
        }
        return mapping.get(gl, 'No score')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject} - {self.grade_letter()}"

TRAIT_CHOICES = [
    (1, '1 - Excellent'),
    (2, '2 - Good'),
    (3, '3 - Fair'),
    (4, '4 - Needs Improvement'),
    (5, '5 - Unsatisfactory'),
]


class StudentTermReport(models.Model):
    """Per-student per-term report: habits, comments, attendance, promotion."""
    PROMOTION_CHOICES = [
        ('promoted',  'Promoted'),
        ('probation', 'Promoted on Probation'),
        ('not',       'Not Promoted'),
        ('pending',   'Pending'),
    ]

    student       = models.ForeignKey('people.Student', on_delete=models.CASCADE, related_name='term_reports')
    session       = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term          = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)

    # Attendance
    days_late   = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)

    # Work habits
    follows_directions      = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    works_independently     = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    attentive_in_class      = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    does_work_neatly        = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    completes_daily_work    = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    completes_homework      = models.IntegerField(choices=TRAIT_CHOICES, default=2)

    # Social habits
    is_courteous            = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    gets_along_with_others  = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    exhibits_self_control   = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    does_not_disturb_others = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    shows_respect           = models.IntegerField(choices=TRAIT_CHOICES, default=2)
    responds_to_correction  = models.IntegerField(choices=TRAIT_CHOICES, default=2)

    # Teacher comment
    teacher_comment = models.TextField(blank=True)
    head_teacher_comment = models.TextField(blank=True)

    # Promotion (only meaningful on 3rd term)
    promotion_status = models.CharField(
        max_length=20, choices=PROMOTION_CHOICES, default='pending'
    )

    class Meta:
        unique_together = ('student', 'session', 'term')

    def __str__(self):
        return f"{self.student} — {self.term} {self.session}"