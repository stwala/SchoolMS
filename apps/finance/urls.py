from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Fee Types
    path('feetypes/',                    views.fee_type_list,   name='fee_type_list'),
    path('feetypes/add/',                views.fee_type_create, name='fee_type_create'),
    path('feetypes/<int:pk>/edit/',      views.fee_type_update, name='fee_type_update'),
    path('feetypes/<int:pk>/delete/',    views.fee_type_delete, name='fee_type_delete'),

    # Invoices
    path('invoices/',                    views.invoice_list,    name='invoice_list'),
    path('invoices/add/',                views.invoice_create,  name='invoice_create'),
    path('students/<int:student_id>/billing-info/', views.student_billing_info, name='student_billing_info'),
    path('invoices/<int:pk>/',           views.invoice_detail,  name='invoice_detail'),
    path('invoices/<int:pk>/delete/',    views.invoice_delete,  name='invoice_delete'),
    
    # Invoice items
    path('invoice-items/<int:pk>/delete/', views.invoice_item_delete, name='invoice_item_delete'),

    # Bulk Generation
    path('bulk/',                        views.bulk_invoice,    name='bulk_invoice'),

    # Financial Analytics Dashboard & Expenses
    path('analytics/',                   views.financial_dashboard, name='financial_dashboard'),
    path('expenses/',                    views.expense_list,        name='expense_list'),
    path('expenses/add/',                views.expense_create,      name='expense_create'),
    path('expenses/<int:pk>/delete/',    views.expense_delete,      name='expense_delete'),
]
