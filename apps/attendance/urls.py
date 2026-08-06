from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('record/', views.attendance_record, name='attendance_record'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('mark/',   views.ajax_mark_attendance, name='ajax_mark_attendance'),
]
