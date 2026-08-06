import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from apps.accounts.decorators import admin_required
from apps.academics.models import StudentClass, AcademicSession, AcademicTerm
from apps.people.models import Student
from .models import FeeType, Invoice, InvoiceItem, Payment, Expense
from .forms import FeeTypeForm, InvoiceForm, InvoiceItemForm, PaymentForm, ExpenseForm

# ── Fee Types CRUD ────────────────────────────────────────
@login_required
@admin_required
def fee_type_list(request):
    fee_types = FeeType.objects.all()
    form = FeeTypeForm()
    return render(request, 'finance/fee_type_list.html', {'fee_types': fee_types, 'form': form})

@login_required
@admin_required
def fee_type_create(request):
    form = FeeTypeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fee type created successfully.')
        return redirect('finance:fee_type_list')
    return render(request, 'finance/form.html', {'form': form, 'title': 'Create Fee Type'})

@login_required
@admin_required
def fee_type_update(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    form = FeeTypeForm(request.POST or None, instance=fee_type)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fee type updated.')
        return redirect('finance:fee_type_list')
    return render(request, 'finance/form.html', {'form': form, 'title': 'Edit Fee Type'})

@login_required
@admin_required
def fee_type_delete(request, pk):
    if request.method == 'POST':
        fee_type = get_object_or_404(FeeType, pk=pk)
        fee_type.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Invoices CRUD ─────────────────────────────────────────
@login_required
def invoice_list(request):
    # Admins see all; parents/students see only their own invoices
    if request.user.is_admin:
        invoices = Invoice.objects.select_related('student__user', 'student_class', 'term').all()
    elif request.user.is_student:
        student = get_object_or_404(Student, user=request.user)
        invoices = Invoice.objects.filter(student=student).select_related('student_class', 'term')
    elif request.user.is_parent:
        parent = request.user.parent_profile
        invoices = Invoice.objects.filter(student__in=parent.students.all()).select_related('student__user', 'student_class', 'term')
    else:
        invoices = Invoice.objects.none()

    return render(request, 'finance/invoice_list.html', {'invoices': invoices})


@login_required
@admin_required
def invoice_create(request):
    form = InvoiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        invoice = form.save()
        # Add selected fee types as invoice line items
        fee_types = form.cleaned_data.get('fee_types', [])
        for fee in fee_types:
            InvoiceItem.objects.create(
                invoice=invoice,
                fee_type=fee,
                description=fee.name,
                amount=fee.amount
            )
        invoice.update_status()
        messages.success(request, 'Invoice generated successfully.')
        return redirect('finance:invoice_detail', pk=invoice.pk)
    return render(request, 'finance/form.html', {'form': form, 'title': 'Create Invoice'})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related('student__user', 'student_class', 'session', 'term'), pk=pk)
    
    # Check permissions
    if not request.user.is_admin:
        if request.user.is_student and request.user.student_profile != invoice.student:
            messages.error(request, 'Access denied.')
            return redirect('/')
        elif request.user.is_parent and invoice.student not in request.user.parent_profile.students.all():
            messages.error(request, 'Access denied.')
            return redirect('/')

    items = invoice.items.all()
    payments = invoice.payments.all()
    
    # Item Form
    item_form = InvoiceItemForm()
    # Payment Form
    payment_form = PaymentForm()

    if request.method == 'POST' and request.user.is_admin:
        # Check which form was submitted
        if 'add_item' in request.POST:
            item_form = InvoiceItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.invoice = invoice
                # If fee type is selected, override description/amount if empty
                if item.fee_type:
                    if not item.description:
                        item.description = item.fee_type.name
                    if not item.amount:
                        item.amount = item.fee_type.amount
                item.save()
                invoice.update_status()
                messages.success(request, 'Invoice item added.')
                return redirect('finance:invoice_detail', pk=invoice.pk)
        
        elif 'record_payment' in request.POST:
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                pay = payment_form.save(commit=False)
                pay.invoice = invoice
                pay.receipt_no = f"REC-{random.randint(100000, 999999)}"
                pay.save()
                invoice.update_status()

                if invoice.status == 'paid':
                    student = invoice.student
                    if not student.grades_visible:
                        student.grades_visible = True
                        student.save(update_fields=['grades_visible'])
                        messages.info(request, f'Grades are now visible to {student.user.get_full_name()}\'s parent.')
                        
                messages.success(request, f'Payment of ${pay.amount_paid} recorded successfully. Receipt #{pay.receipt_no}')
                return redirect('finance:invoice_detail', pk=invoice.pk)

    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'item_form': item_form,
        'payment_form': payment_form,
    }
    return render(request, 'finance/invoice_detail.html', context)


@login_required
@admin_required
def invoice_delete(request, pk):
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@admin_required
def invoice_item_delete(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(InvoiceItem, pk=pk)
        invoice = item.invoice
        item.delete()
        invoice.update_status()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@admin_required
def bulk_invoice(request):
    classes = StudentClass.objects.all()
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    fee_types = FeeType.objects.all()

    if request.method == 'POST':
        class_id = request.POST.get('student_class')
        session_id = request.POST.get('session')
        term_id = request.POST.get('term')
        selected_fees = request.POST.getlist('fee_types')

        if not class_id or not session_id or not term_id:
            messages.error(request, 'Please select a Class, Session, and Term.')
            return redirect('finance:bulk_invoice')

        student_class = get_object_or_404(StudentClass, pk=class_id)
        session = get_object_or_404(AcademicSession, pk=session_id)
        term = get_object_or_404(AcademicTerm, pk=term_id)
        
        students = Student.objects.filter(student_class=student_class, is_active=True)
        
        if not students.exists():
            messages.warning(request, f'No active students found in class {student_class.name}.')
            return redirect('finance:bulk_invoice')

        generated_count = 0
        for student in students:
            # Check if invoice already exists for this term
            exists = Invoice.objects.filter(
                student=student,
                session=session,
                term=term
            ).exists()
            
            if not exists:
                previous_invoices = Invoice.objects.filter(student=student)
                prev_balance = sum((inv.balance() for inv in previous_invoices), Decimal('0.00'))

                invoice = Invoice.objects.create(
                    student=student,
                    session=session,
                    term=term,
                    student_class=student_class,
                    balance_from_previous_term=prev_balance
                )
                
                # Add selected fee items
                for fee_id in selected_fees:
                    fee = FeeType.objects.get(pk=fee_id)
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        fee_type=fee,
                        description=fee.name,
                        amount=fee.amount
                    )
                invoice.update_status()
                generated_count += 1

        messages.success(request, f'Bulk generation complete! Successfully generated {generated_count} invoices.')
        return redirect('finance:invoice_list')

    context = {
        'classes': classes,
        'sessions': sessions,
        'terms': terms,
        'fee_types': fee_types,
    }
    return render(request, 'finance/bulk_invoice.html', context)


@login_required
@admin_required
def financial_dashboard(request):
    invoices = Invoice.objects.all()
    payments = Payment.objects.all()
    expenses = Expense.objects.all()
    
    total_billed = sum(inv.total_payable() for inv in invoices)
    total_collected = sum(pay.amount_paid for pay in payments)
    outstanding = total_billed - total_collected
    total_expenses = sum(exp.amount for exp in expenses)
    net_cashflow = total_collected - total_expenses

    # Monthly revenue collections and expenses grouping
    monthly_collections = Payment.objects.annotate(month=TruncMonth('date_paid'))\
                                         .values('month')\
                                         .annotate(total=Sum('amount_paid'))\
                                         .order_by('month')
                                         
    monthly_expenses_qs = Expense.objects.annotate(month=TruncMonth('date_spent'))\
                                         .values('month')\
                                         .annotate(total=Sum('amount'))\
                                         .order_by('month')

    chart_data = {}
    for mc in monthly_collections:
        m_str = mc['month'].strftime('%b %Y') if mc['month'] else 'Unknown'
        if m_str not in chart_data:
            chart_data[m_str] = {'revenue': 0.0, 'expense': 0.0}
        chart_data[m_str]['revenue'] = float(mc['total'] or 0.0)

    for me in monthly_expenses_qs:
        m_str = me['month'].strftime('%b %Y') if me['month'] else 'Unknown'
        if m_str not in chart_data:
            chart_data[m_str] = {'revenue': 0.0, 'expense': 0.0}
        chart_data[m_str]['expense'] = float(me['total'] or 0.0)

    sorted_months = list(chart_data.keys())
    revenue_list = [chart_data[m]['revenue'] for m in sorted_months]
    expense_list = [chart_data[m]['expense'] for m in sorted_months]

    # Expense categories breakdown
    category_totals = Expense.objects.values('category').annotate(total=Sum('amount'))
    category_labels = []
    category_data = []
    cat_map = dict(Expense.CATEGORY_CHOICES)
    for ct in category_totals:
        category_labels.append(cat_map.get(ct['category'], ct['category']))
        category_data.append(float(ct['total'] or 0.0))

    # Recent list
    recent_payments = Payment.objects.select_related('invoice__student__user').order_by('-date_paid')[:5]
    recent_expenses = Expense.objects.select_related('recorded_by').order_by('-date_spent')[:5]

    context = {
        'total_billed': total_billed,
        'total_collected': total_collected,
        'outstanding': outstanding,
        'total_expenses': total_expenses,
        'net_cashflow': net_cashflow,
        'sorted_months': sorted_months,
        'revenue_list': revenue_list,
        'expense_list': expense_list,
        'category_labels': category_labels,
        'category_data': category_data,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'finance/financial_dashboard.html', context)


@login_required
@admin_required
def expense_list(request):
    expenses = Expense.objects.select_related('recorded_by').all()
    q = request.GET.get('q', '')
    if q:
        expenses = expenses.filter(title__icontains=q)
    return render(request, 'finance/expense_list.html', {'expenses': expenses, 'q': q})


@login_required
@admin_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.recorded_by = request.user
        expense.save()
        messages.success(request, 'Expense logged successfully.')
        return redirect('finance:expense_list')
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'Log Expense'})


@login_required
@admin_required
def expense_delete(request, pk):
    if request.method == 'POST':
        expense = get_object_or_404(Expense, pk=pk)
        expense.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@admin_required
def student_billing_info(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    invoices = Invoice.objects.filter(student=student)
    previous_balance = sum((inv.balance() for inv in invoices), Decimal('0.00'))
    return JsonResponse({
        'class_id': student.student_class.id if student.student_class else None,
        'previous_balance': str(previous_balance)
    })

