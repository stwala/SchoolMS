from django.db import models
from django.urls import reverse
from decimal import Decimal

class FeeType(models.Model):
    """Fee type definitions (e.g. Tuition Fee, Exam Fee)"""
    name = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (${self.amount})"


class Invoice(models.Model):
    """Student Fee Invoices"""
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    )
    student = models.ForeignKey('people.Student', on_delete=models.CASCADE, related_name='invoices')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.AcademicTerm', on_delete=models.CASCADE)
    student_class = models.ForeignKey('academics.StudentClass', on_delete=models.CASCADE)
    balance_from_previous_term = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice for {self.student.user.get_full_name()} - {self.term}"

    def total_payable(self):
        items_total = sum((item.amount for item in self.items.all()),Decimal('0.00'))
        return max(Decimal('0.00'), self.balance_from_previous_term + items_total - self.discount)

    def total_paid(self):
        return sum((payment.amount_paid for payment in self.payments.all()),Decimal('0.00'))

    def balance(self):
        return self.total_payable() - self.total_paid()

    def update_status(self):
        paid = self.total_paid()
        payable = self.total_payable()
        if paid >= payable:
            self.status = 'paid'
        elif paid > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        self.save()


class InvoiceItem(models.Model):
    """Line items inside a fee invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    fee_type = models.ForeignKey(FeeType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Payment(models.Model):
    """Receipt payments for fee invoices"""
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
    )
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    receipt_no = models.CharField(max_length=50, unique=True)
    note = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-date_paid']

    def __str__(self):
        return f"Receipt #{self.receipt_no} - Paid {self.amount_paid} for {self.invoice.student}"


class Expense(models.Model):
    """School Operational Expenses"""
    CATEGORY_CHOICES = (
        ('salaries', 'Salaries & Wages'),
        ('utilities', 'Utilities & Bills'),
        ('maintenance', 'Repairs & Maintenance'),
        ('supplies', 'Educational Supplies'),
        ('food', 'Cafeteria & Catering'),
        ('other', 'Other Expenses'),
    )
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_spent = models.DateField()
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_spent']

    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.date_spent})"
