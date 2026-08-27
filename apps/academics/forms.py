from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from apps.dashboard.models import ClassNamingRule
from .models import AcademicSession, AcademicTerm, Subject, StudentClass, Grade,StudentTermReport, AcademicEvent

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
        fields = ['grade_level','stream','subjects']
        widgets = {
            'grade_level': forms.NumberInput(attrs={'placeholder': 'e.g. 10'}),
            'stream': forms.TextInput(attrs={'placeholder': 'e.g. A'}),
            'subjects': forms.CheckboxSelectMultiple(attrs={'class': 'subject-checkboxes'}),
        }

    def clean_grade_level(self):
        grade = self.cleaned_data.get('grade_level')

        if not ClassNamingRule.for_grade(grade):
            raise forms.ValidationError(
                f"Grade {grade} cannot be added because no "
                f"class naming rule has been configured for it. "
                f"Please configure the naming rule in School Settings first."
            )

        return grade
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'grade_level',
            'stream',
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





class AcademicEventForm(forms.ModelForm):

    class Meta:
        model = AcademicEvent

        fields = [
            'title',
            'event_type',
            'start_date',
            'end_date',
            'description',
            'session',
            'term',
            'is_active',
        ]

        widgets = {
            'start_date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'end_date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Describe this event...'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(

            'title',

            Row(
                Column(
                    'event_type',
                    css_class='col-md-6'
                ),

                Column(
                    'is_active',
                    css_class='col-md-6'
                ),
            ),

            Row(
                Column(
                    'start_date',
                    css_class='col-md-6'
                ),

                Column(
                    'end_date',
                    css_class='col-md-6'
                ),
            ),

            Row(
                Column(
                    'session',
                    css_class='col-md-6'
                ),

                Column(
                    'term',
                    css_class='col-md-6'
                ),
            ),

            'description',

            Submit(
                'submit',
                'Save Event',
                css_class='btn btn-primary'
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be before the start date."
            )

        return cleaned_data