from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Notice,SchoolSettings,ClassNamingRule

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'to_admins', 'to_teachers', 'to_students', 'to_parents', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            Row(
                Column('to_admins'),
                Column('to_teachers'),
                Column('to_students'),
                Column('to_parents'),
            ),
            'is_active',
            Submit('submit', 'Publish Announcement', css_class='btn btn-primary btn-sm mt-2')
        )



class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model  = SchoolSettings
        fields = ['school_name', 'logo', 'favicon', 'primary_color',
                  'secondary_color', 'sidebar_color', 'navbar_color',
                  'address', 'phone', 'email', 'website']
        widgets = {
            'primary_color'  : forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'sidebar_color'  : forms.TextInput(attrs={'type': 'color'}),
            'navbar_color'   : forms.TextInput(attrs={'type': 'color'}),
        }

class ClassNamingRuleForm(forms.ModelForm):
    class Meta:
        model = ClassNamingRule
        fields = ['from_grade','to_grade','naming_convention','custom_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('from_grade', css_class='form-group col-md-6 mb-0'),
                Column('to_grade', css_class='form-group col-md-6 mb-0'),
            ),
            'naming_convention',
            'custom_name',
            Submit('submit', 'Save Rule', css_class='btn btn-primary btn-sm mt-2')
        )

    def clean(self):
        cleaned_data = super().clean()

        from_grade = cleaned_data.get('from_grade')
        to_grade = cleaned_data.get('to_grade')
        school_settings = SchoolSettings.get()

        if from_grade and to_grade:
            if from_grade > to_grade:
                raise forms.ValidationError(
                    "The starting grade cannot be higher than the ending grade."
                )

            overlapping = ClassNamingRule.objects.filter(
                school_settings=school_settings,
                from_grade__lte=to_grade,
                to_grade__gte=from_grade,
            )

            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise forms.ValidationError(
                    "This grade range overlaps with an existing naming rule."
                )

        return cleaned_data
