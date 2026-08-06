from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Notice,SchoolSettings

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
