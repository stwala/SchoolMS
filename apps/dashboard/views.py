from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from apps.accounts.decorators import admin_required
from apps.academics.models import StudentClass, AcademicSession, AcademicTerm, Grade, Subject
from apps.people.models import Student, Teacher, Parent
from apps.finance.models import Invoice, Payment
from apps.attendance.models import Attendance
from .models import Notice, SchoolSettings, ClassNamingRule
from .forms import NoticeForm, SchoolSettingsForm, ClassNamingRuleForm

# ── Entry Redirector ──────────────────────────────────────
def index(request):
    if request.user.is_authenticated:
        dash_url = request.user.get_dashboard_url()
        if dash_url == '/':
            if request.user.is_superuser or request.user.is_admin:
                return redirect('dashboard:admin_dashboard')
            # If they are just a student or parent with missing profile, redirect to profile or logout
            return redirect('accounts:profile')
        return redirect(dash_url)
    return redirect('accounts:login')

# ── Admin Dashboard ──────────────────────────────────────
@login_required
@admin_required
def admin_dashboard(request):
    # Total counts
    students_count = Student.objects.filter(is_active=True).count()
    teachers_count = Teacher.objects.filter(is_active=True).count()
    parents_count = Parent.objects.count()
    classes_count = StudentClass.objects.count()

    # Finance summaries
    invoices = Invoice.objects.all()
    payments = Payment.objects.all()

    total_billed = sum(inv.total_payable() for inv in invoices)
    total_collected = sum(pay.amount_paid for pay in payments)
    outstanding = total_billed - total_collected

    # Notices
    notices = Notice.objects.filter(is_active=True, to_admins=True)[:5]

    # Chart.js Data: Class sizes
    classes = StudentClass.objects.all()
    class_labels = [c.name for c in classes]
    class_sizes = [Student.objects.filter(student_class=c, is_active=True).count() for c in classes]

    # Chart.js Data: Payments by method
    methods = ['cash', 'bank_transfer', 'card']
    method_labels = ['Cash', 'Bank Transfer', 'Card']
    method_data = [Payment.objects.filter(payment_method=m).count() for m in methods]

    context = {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'parents_count': parents_count,
        'classes_count': classes_count,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'outstanding': outstanding,
        'notices': notices,
        'class_labels': class_labels,
        'class_sizes': class_sizes,
        'method_labels': method_labels,
        'method_data': method_data,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ── Teacher Dashboard ─────────────────────────────────────
# @login_required
# def teacher_dashboard(request):
#     from apps.academics.models import AcademicSession, AcademicTerm, Grade, StudentTermReport
#     from apps.academics.models import Subject

#     if not (request.user.is_teacher or request.user.is_admin):
#         return redirect('/')

#     teacher = get_object_or_404(Teacher, user=request.user)
#     notices  = Notice.objects.filter(is_active=True, to_teachers=True)[:5]

#     # Assigned classes (admins see all)
#     if request.user.is_admin:
#         my_classes = StudentClass.objects.prefetch_related('subjects').all()
#     else:
#         my_classes = teacher.assigned_classes.prefetch_related('subjects').all()

#     active_session = AcademicSession.objects.filter(current=True).first()
#     active_term    = AcademicTerm.objects.filter(current=True).first()
#     all_sessions   = AcademicSession.objects.all()
#     all_terms      = AcademicTerm.objects.all()

#     # ── Grade Entry filter params ────────────────────────
#     selected_class_id   = request.GET.get('student_class') or (str(my_classes.first().pk) if my_classes.exists() else None)
#     selected_session_id = request.GET.get('session') or (str(active_session.pk) if active_session else None)
#     selected_term_id    = request.GET.get('term')    or (str(active_term.pk)    if active_term    else None)
#     selected_subject_id = request.GET.get('subject')

#     selected_class   = None
#     selected_session = None
#     selected_term    = None
#     selected_subject = None
#     class_students   = []
#     class_subjects   = []
#     grades_dict      = {}      # {student_id: {subject_id: grade_obj}}
#     term_reports     = {}      # {student_id: StudentTermReport}

#     if selected_class_id:
#         from django.shortcuts import get_object_or_404 as _get
#         selected_class = StudentClass.objects.filter(pk=selected_class_id).first()

#     if selected_session_id:
#         selected_session = AcademicSession.objects.filter(pk=selected_session_id).first()

#     if selected_term_id:
#         selected_term = AcademicTerm.objects.filter(pk=selected_term_id).first()

#     if selected_class:
#         class_subjects = list(selected_class.subjects.all())

#         # Auto-select first subject if none chosen
#         if not selected_subject_id and class_subjects:
#             selected_subject_id = str(class_subjects[0].pk)

#         if selected_subject_id:
#             selected_subject = Subject.objects.filter(pk=selected_subject_id).first()

#         class_students = list(
#             Student.objects.filter(student_class=selected_class, is_active=True)
#                            .select_related('user')
#                            .order_by('user__last_name', 'user__first_name')
#         )

#         # ── Load existing grades (all subjects, this session+term) ──
#         if selected_session and selected_term:
#             existing_grades = Grade.objects.filter(
#                 student_class=selected_class,
#                 session=selected_session,
#                 term=selected_term,
#             ).select_related('student', 'subject')

#             for g in existing_grades:
#                 grades_dict.setdefault(g.student_id, {})[g.subject_id] = g

#             # ── Load existing term reports ──────────────────────
#             tr_qs = StudentTermReport.objects.filter(
#                 student__in=[s.pk for s in class_students],
#                 session=selected_session,
#                 term=selected_term,
#             )
#             term_reports = {tr.student_id: tr for tr in tr_qs}

#     # ── Handle POST: Save grades for one subject ──────────
#     if request.method == 'POST' and selected_class and selected_subject and selected_session and selected_term:
#         for s in class_students:
#             try:
#                 test_score = max(0, min(40, int(request.POST.get(f'test_{s.pk}', 0) or 0)))
#                 exam_score = max(0, min(60, int(request.POST.get(f'exam_{s.pk}', 0) or 0)))
#             except ValueError:
#                 test_score = exam_score = 0

#             g_obj, _ = Grade.objects.get_or_create(
#                 student=s,
#                 subject=selected_subject,
#                 session=selected_session,
#                 term=selected_term,
#                 defaults={'student_class': selected_class}
#             )
#             g_obj.student_class = selected_class
#             g_obj.test_score    = test_score
#             g_obj.exam_score    = exam_score
#             g_obj.save()

#         messages.success(request, f'Grades saved for {selected_subject.name}.')
#         qs = (f'?student_class={selected_class_id}&session={selected_session_id}'
#               f'&term={selected_term_id}&subject={selected_subject_id}')
#         return redirect(f"{request.path}{qs}")

#     # Attach grade objects to students for grade tab rendering
#     selected_subject_pk = int(selected_subject_id) if selected_subject_id else None
#     for s in class_students:
#         s.subj_grades  = grades_dict.get(s.pk, {})   # {subject_id: grade_obj}
#         s.term_report  = term_reports.get(s.pk)
#         # Convenience: the grade for the currently selected subject
#         s.selected_grade = s.subj_grades.get(selected_subject_pk) if selected_subject_pk else None

#     students_count = sum(
#         Student.objects.filter(student_class=c, is_active=True).count()
#         for c in my_classes
#     )

#     context = {
#         'teacher'            : teacher,
#         'notices'            : notices,
#         'my_classes'         : my_classes,
#         'all_sessions'       : all_sessions,
#         'all_terms'          : all_terms,
#         'active_session'     : active_session,
#         'active_term'        : active_term,
#         'selected_class'     : selected_class,
#         'selected_session'   : selected_session,
#         'selected_term'      : selected_term,
#         'selected_subject'   : selected_subject,
#         'selected_class_id'  : str(selected_class_id)   if selected_class_id   else '',
#         'selected_session_id': str(selected_session_id) if selected_session_id else '',
#         'selected_term_id'   : str(selected_term_id)    if selected_term_id    else '',
#         'selected_subject_id': str(selected_subject_id) if selected_subject_id else '',
#         'class_students'     : class_students,
#         'class_subjects'     : class_subjects,
#         'students_count'     : students_count,
#     }
#     return render(request, 'dashboard/teacher_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    """Overview dashboard — stat cards + charts. No grade entry here."""
    from django.db.models import F, Avg, Count
    from apps.academics.models import AcademicSession, AcademicTerm, Grade, StudentTermReport
 
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('/')
 
    teacher = get_object_or_404(Teacher, user=request.user)
    notices = Notice.objects.filter(is_active=True, to_teachers=True)[:5]
 
    if request.user.is_admin:
        my_classes = StudentClass.objects.prefetch_related('subjects').all()
    else:
        my_classes = teacher.assigned_classes.prefetch_related('subjects').all()
 
    active_session = AcademicSession.objects.filter(current=True).first()
    active_term    = AcademicTerm.objects.filter(current=True).first()
 
    class_stats   = []                                   # per-class summary rows
    subject_stats = []                                    # per-subject avg (chart)
    grade_buckets = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    total_reports_due  = 0
    total_reports_done = 0
 
    student_counts = {
        c.pk: Student.objects.filter(student_class=c, is_active=True).count()
        for c in my_classes
    }
    total_students = sum(student_counts.values())
 
    class_avgs        = {}
    reports_by_class  = {}
 
    if active_session and active_term and my_classes:
        # Compute total = test_score + exam_score in the DB, not via the
        # Grade.total_score() method (that only works on Python instances).
        grade_qs = Grade.objects.filter(
            student_class__in=my_classes,
            session=active_session,
            term=active_term,
        ).annotate(total=F('test_score') + F('exam_score'))
 
        # Grade distribution buckets
        for total in grade_qs.values_list('total', flat=True):
            if total is None:
                continue
            if total >= 90:   grade_buckets['A'] += 1
            elif total >= 80: grade_buckets['B'] += 1
            elif total >= 70: grade_buckets['C'] += 1
            elif total >= 60: grade_buckets['D'] += 1
            else:             grade_buckets['F'] += 1
 
        # Per-class averages (used in the classes table)
        class_avgs = {
            row['student_class']: row['avg']
            for row in grade_qs.values('student_class').annotate(avg=Avg('total'))
        }
 
        # Per-subject averages — the detailed chart. Aggregates across ALL of
        # the teacher's classes, so a subject taught in 3 classes gets one bar.
        subject_rows = (
            grade_qs.values('subject__id', 'subject__name')
                    .annotate(avg=Avg('total'), entries=Count('id'))
                    .order_by('subject__name')
        )
        subject_stats = [
            {
                'subject_name': row['subject__name'],
                'avg_score'   : round(row['avg'], 1) if row['avg'] is not None else None,
                'entries'     : row['entries'],
            }
            for row in subject_rows
        ]
 
        # Term reports filed, grouped by class
        reports_qs = StudentTermReport.objects.filter(
            student__student_class__in=my_classes,
            session=active_session,
            term=active_term,
        )
        reports_by_class = {
            row['student__student_class']: row['n']
            for row in reports_qs.values('student__student_class').annotate(n=Count('id'))
        }
 
    for c in my_classes:
        student_count = student_counts.get(c.pk, 0)
        avg_score     = class_avgs.get(c.pk)
        reports_done  = reports_by_class.get(c.pk, 0)
 
        if active_session and active_term:
            total_reports_due  += student_count
            total_reports_done += reports_done
 
        class_stats.append({
            'class_obj'    : c,
            'student_count': student_count,
            'avg_score'    : round(avg_score, 1) if avg_score is not None else None,
            'reports_done' : reports_done,
        })
 
    pending_reports = total_reports_due - total_reports_done
 
    context = {
        'teacher'          : teacher,
        'notices'          : notices,
        'my_classes'       : my_classes,
        'active_session'   : active_session,
        'active_term'      : active_term,
        'students_count'   : total_students,
        'class_stats'      : class_stats,
        'subject_stats'    : subject_stats,
        'grade_buckets'    : grade_buckets,
        'pending_reports'  : pending_reports,
        'reports_done'     : total_reports_done,
        'reports_due'      : total_reports_due,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)
 


# ── Student Dashboard ─────────────────────────────────────
@login_required
def student_dashboard(request):
    if not (request.user.is_student or request.user.is_admin):
        return redirect('/')

    student = get_object_or_404(Student.objects.select_related('student_class'), user=request.user)
    
    # Active session/term grades
    active_session = AcademicSession.objects.filter(current=True).first()
    active_term = AcademicTerm.objects.filter(current=True).first()
    
    grades = Grade.objects.filter(student=student)
    if active_session:
        grades = grades.filter(session=active_session)
    if active_term:
        grades = grades.filter(term=active_term)
    grades = grades.select_related('subject')

    # Chart.js Data
    subject_labels = [g.subject.name for g in grades]
    subject_scores = [g.total_score() for g in grades]

    # Attendance summary
    total_att = Attendance.objects.filter(student=student).count()
    present_att = Attendance.objects.filter(student=student, status__in=['present', 'late']).count()
    att_rate = (present_att / total_att * 100) if total_att > 0 else 100.0

    # Outstanding Invoices
    unpaid_invoices = Invoice.objects.filter(student=student).exclude(status='paid')

    # Target Notices
    notices = Notice.objects.filter(is_active=True, to_students=True)[:5]

    context = {
        'student': student,
        'grades': grades,
        'subject_labels': subject_labels,
        'subject_scores': subject_scores,
        'total_att': total_att,
        'att_rate': att_rate,
        'unpaid_invoices': unpaid_invoices,
        'notices': notices,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


# ── Parent Dashboard ──────────────────────────────────────
@login_required
def parent_dashboard(request):
    if not (request.user.is_parent or request.user.is_admin):
        return redirect('/')

    parent = get_object_or_404(Parent, user=request.user)
    children = parent.students.all().select_related('user', 'student_class')

    selected_child_id = request.GET.get('child_id')
    selected_child = None
    grades = []
    att_rate = 100.0
    unpaid_invoices = []
    grades_locked = False  # ← add this

    if children.exists():
        if selected_child_id:
            selected_child = get_object_or_404(children, pk=selected_child_id)
        else:
            selected_child = children.first()

        active_session = AcademicSession.objects.filter(current=True).first()
        active_term    = AcademicTerm.objects.filter(current=True).first()

        # ── Only show grades if visible ──
        if selected_child.grades_visible:
            grades = Grade.objects.filter(student=selected_child)
            if active_session:
                grades = grades.filter(session=active_session)
            if active_term:
                grades = grades.filter(term=active_term)
            grades = grades.select_related('subject')
        else:
            grades_locked = True  # ← flag for template

        # Attendance
        total_att   = Attendance.objects.filter(student=selected_child).count()
        present_att = Attendance.objects.filter(student=selected_child, status__in=['present', 'late']).count()
        att_rate    = (present_att / total_att * 100) if total_att > 0 else 100.0

        # Invoices
        unpaid_invoices = Invoice.objects.filter(student=selected_child).exclude(status='paid')

    notices = Notice.objects.filter(is_active=True, to_parents=True)[:5]

    context = {
        'parent'          : parent,
        'children'        : children,
        'selected_child'  : selected_child,
        'grades'          : grades,
        'grades_locked'   : grades_locked,
        'att_rate'        : att_rate,
        'unpaid_invoices' : unpaid_invoices,
        'notices'         : notices,
    }
    return render(request, 'dashboard/parent_dashboard.html', context)

# ── Notices Management (Admin only) ────────────────────────
@login_required
@admin_required
def notice_list(request):
    notices = Notice.objects.all().select_related('author')
    return render(request, 'dashboard/notice_list.html', {'notices': notices})

@login_required
@admin_required
def notice_create(request):
    form = NoticeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        notice = form.save(commit=False)
        notice.author = request.user
        notice.save()
        messages.success(request, 'Notice published successfully.')
        return redirect('dashboard:notice_list')
    return render(request, 'dashboard/form.html', {'form': form, 'title': 'Post Notice'})

@login_required
@admin_required
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    form = NoticeForm(request.POST or None, instance=notice)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Notice updated successfully.')
        return redirect('dashboard:notice_list')
    return render(request, 'dashboard/form.html', {'form': form, 'title': 'Edit Notice'})

@login_required
@admin_required
def notice_delete(request, pk):
    if request.method == 'POST':
        notice = get_object_or_404(Notice, pk=pk)
        notice.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


def _school_settings_context(settings, form=None, naming_rule_form=None, active_tab='branding'):
    return {
        'form': form or SchoolSettingsForm(instance=settings),
        'settings': settings,
        'title': 'School Settings',
        'naming_rules': ClassNamingRule.objects.filter(
            school_settings=settings
        ).order_by('from_grade'),
        'naming_rule_form': naming_rule_form or ClassNamingRuleForm(),
        'active_tab': active_tab,
    }


@login_required
@admin_required
def school_settings(request):
    settings = SchoolSettings.get()
    form = SchoolSettingsForm(request.POST or None,
                              request.FILES or None,
                              instance=settings)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'School settings updated successfully.')
        return redirect('dashboard:school_settings')
    return render(
        request,
        'dashboard/school_settings.html',
        _school_settings_context(settings, form=form, active_tab=request.GET.get('tab', 'branding')),
    )


@login_required
@admin_required
def naming_rule_add(request):
    settings = SchoolSettings.get()
    if request.method != 'POST':
        return redirect('dashboard:school_settings')

    form = ClassNamingRuleForm(request.POST)
    if form.is_valid():
        naming_rule = form.save(commit=False)
        naming_rule.school_settings = settings
        naming_rule.save()
        messages.success(request, 'Class naming rule added successfully.')
        return redirect(f"{reverse('dashboard:school_settings')}?tab=naming")

    messages.error(request, 'Please fix the class naming rule details below.')
    return render(
        request,
        'dashboard/school_settings.html',
        _school_settings_context(settings, naming_rule_form=form, active_tab='naming'),
    )


@login_required
@admin_required
def naming_rule_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    settings = SchoolSettings.get()
    naming_rule = get_object_or_404(ClassNamingRule, pk=pk, school_settings=settings)
    naming_rule.delete()
    messages.success(request, 'Class naming rule deleted successfully.')
    return redirect(f"{reverse('dashboard:school_settings')}?tab=naming")
