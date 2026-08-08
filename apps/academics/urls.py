from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Sessions
    path('sessions/',                    views.session_list,   name='session_list'),
    path('sessions/add/',                views.session_create, name='session_create'),
    path('sessions/<int:pk>/edit/',      views.session_update, name='session_update'),
    path('sessions/<int:pk>/delete/',    views.session_delete, name='session_delete'),

    # Terms
    path('terms/',                       views.term_list,   name='term_list'),
    path('terms/add/',                   views.term_create, name='term_create'),
    path('terms/<int:pk>/edit/',         views.term_update, name='term_update'),
    path('terms/<int:pk>/delete/',       views.term_delete, name='term_delete'),

    # Subjects
    path('subjects/',                    views.subject_list,   name='subject_list'),
    path('subjects/add/',                views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/',      views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/',    views.subject_delete, name='subject_delete'),

    # Classes
    path('classes/',                     views.class_list,   name='class_list'),
    path('classes/add/',                 views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/',       views.class_update, name='class_update'),
    path('classes/<int:pk>/delete/',     views.class_delete, name='class_delete'),

    # Grades & Performance
    path('grades/',                        views.grade_entry,           name='grade_entry'),
    path('grades/save-student/',           views.save_student_grades,   name='save_student_grades'),
    path('report-card/<int:student_id>/',  views.student_report_card,   name='student_report_card'),
    path("rankings/", views.class_rankings,  name="class_rankings"), 
    path("rankings/export/excel/",views.export_ranking_excel,name="export_ranking_excel"),
    path("rankings/export/pdf/",views.export_ranking_pdf,name="export_ranking_pdf"),   
    path('students/<int:student_id>/term-report/', views.save_term_report, name='save_term_report'),
]
