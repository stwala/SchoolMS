from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    # Students
    path('students/',                       views.student_list,        name='student_list'),
    path('students/search-ajax/',           views.student_search_ajax, name='student_search_ajax'),
    path('students/add/',                   views.student_create,      name='student_create'),
    path('students/<int:pk>/',              views.student_detail,      name='student_detail'),
    path('students/<int:pk>/edit/',         views.student_update,      name='student_update'),
    path('students/<int:pk>/delete/',       views.student_delete,      name='student_delete'),
    path('students/<int:pk>/grades.json',   views.student_grades_json, name='student_grades_json'),
    path('students/bulk-upload/', views.student_bulk_upload, name='student_bulk_upload'),
    path('students/bulk-template/', views.student_bulk_template, name='student_bulk_template'),
    # Teachers
    path('teachers/',                    views.teacher_list,   name='teacher_list'),
    path('teachers/add/',                views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/edit/',      views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/',    views.teacher_delete, name='teacher_delete'),
    # Parents
    path('parents/',                     views.parent_list,    name='parent_list'),
    path('parents/add/',                 views.parent_create,  name='parent_create'),
    path('parents/<int:pk>/edit/',       views.parent_update,  name='parent_update'),
    path('parents/<int:pk>/delete/',     views.parent_delete,  name='parent_delete'),

    path('students/<int:pk>/toggle-grades/', views.toggle_grades_visibility, name='student_toggle_grades'),
]