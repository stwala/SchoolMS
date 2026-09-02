from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # General redirector
    path('', views.index, name='index'),
    
    # Dashboards
    path('admin/',   views.admin_dashboard,   name='admin_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('parent/',  views.parent_dashboard,  name='parent_dashboard'),

    # Notice Board
    path('notices/',                 views.notice_list,   name='notice_list'),
    path('notices/add/',             views.notice_create, name='notice_create'),
    path('notices/<int:pk>/edit/',   views.notice_update, name='notice_update'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),

    path('settings/', views.school_settings, name='school_settings'),
    path('settings/naming-rule/add/', views.naming_rule_add, name='naming_rule_add'),
    path('settings/naming-rule/<int:pk>/edit/', views.naming_rule_edit, name='naming_rule_edit'),
    path('settings/naming-rule/<int:pk>/delete/', views.naming_rule_delete, name='naming_rule_delete'),
    path('class-performance-data/', views.class_performance_data, name='class_performance_data'),
]
