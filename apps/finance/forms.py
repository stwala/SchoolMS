from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import FeeType, Invoice, InvoiceItem, Payment, Expense

class FeeTypeForm(forms.ModelForm):
    class Meta:
        model = FeeType
        fields = ['name', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name'), Column('amount')),
            'description',
            Submit('submit', 'Save Fee Type', css_class='btn btn-primary btn-sm mt-2')
        )


class InvoiceForm(forms.ModelForm):
    fee_types = forms.ModelMultipleChoiceField(
        queryset=FeeType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Standard Fees to Apply"
    )

    class Meta:
        model = Invoice
        fields = ['student', 'session', 'term', 'student_class', 'balance_from_previous_term', 'discount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('student'), Column('student_class')),
            Row(Column('session'), Column('term')),
            Row(Column('balance_from_previous_term'), Column('discount')),
            'fee_types',
            Submit('submit', 'Create Invoice', css_class='btn btn-success btn-sm mt-2')
        )


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['fee_type', 'description', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'fee_type',
            'description',
            'amount',
            Submit('submit', 'Add Line Item', css_class='btn btn-primary btn-sm mt-2')
        )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('amount_paid'), Column('payment_method')),
            'note',
            Submit('submit', 'Record Payment', css_class='btn btn-success btn-sm mt-2')
        )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'category', 'amount', 'date_spent', 'note']
        widgets = {
            'date_spent': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('title'), Column('category')),
            Row(Column('amount'), Column('date_spent')),
            'note',
            Submit('submit', 'Log Expense', css_class='btn btn-danger btn-sm mt-2')
        )

