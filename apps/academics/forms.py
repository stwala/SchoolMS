from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import AcademicSession, AcademicTerm, Subject, StudentClass, Grade,StudentTermReport, TRAIT_CHOICES

class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'current']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'current',
            Submit('submit', 'Save Session', css_class='btn btn-primary btn-sm mt-2')
        )


class AcademicTermForm(forms.ModelForm):
    class Meta:
        model = AcademicTerm
        fields = ['name', 'current']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'current',
            Submit('submit', 'Save Term', css_class='btn btn-primary btn-sm mt-2')
        )


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name'), Column('code')),
            Submit('submit', 'Save Subject', css_class='btn btn-primary btn-sm mt-2')
        )


class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'subjects',
            Submit('submit', 'Save Class', css_class='btn btn-primary btn-sm mt-2')
        )


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['test_score', 'exam_score']


class StudentTermReportForm(forms.ModelForm):
    class Meta:
        model  = StudentTermReport
        fields = [
            'days_late', 'days_absent',
            'follows_directions', 'works_independently', 'attentive_in_class',
            'does_work_neatly', 'completes_daily_work', 'completes_homework',
            'is_courteous', 'gets_along_with_others', 'exhibits_self_control',
            'does_not_disturb_others', 'shows_respect', 'responds_to_correction',
            'teacher_comment', 'promotion_status',
        ]
        widgets = {
            'teacher_comment': forms.Textarea(attrs={'rows': 3}),
        }
