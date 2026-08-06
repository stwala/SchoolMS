from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import admin_required, teacher_required
from .models import AcademicSession, AcademicTerm, Subject, StudentClass, Grade
from .forms import AcademicSessionForm, AcademicTermForm, SubjectForm, StudentClassForm
from apps.people.models import Student

# ── Academic Sessions ─────────────────────────────────────
@login_required
@admin_required
def session_list(request):
    sessions = AcademicSession.objects.all()
    form = AcademicSessionForm()
    return render(request, 'academics/session_list.html', {'sessions': sessions, 'form': form})

@login_required
@admin_required
def session_create(request):
    form = AcademicSessionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        if session.current:
            AcademicSession.objects.filter(current=True).update(current=False)
        session.save()
        messages.success(request, 'Session added successfully.')
        return redirect('academics:session_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Create Session'})

@login_required
@admin_required
def session_update(request, pk):
    session = get_object_or_404(AcademicSession, pk=pk)
    form = AcademicSessionForm(request.POST or None, instance=session)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        if session.current:
            AcademicSession.objects.filter(current=True).exclude(pk=pk).update(current=False)
        session.save()
        messages.success(request, 'Session updated successfully.')
        return redirect('academics:session_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Edit Session'})

@login_required
@admin_required
def session_delete(request, pk):
    if request.method == 'POST':
        session = get_object_or_404(AcademicSession, pk=pk)
        if session.current:
            return JsonResponse({'status': 'error', 'message': 'Cannot delete active session.'}, status=400)
        session.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Academic Terms ────────────────────────────────────────
@login_required
@admin_required
def term_list(request):
    terms = AcademicTerm.objects.all()
    form = AcademicTermForm()
    return render(request, 'academics/term_list.html', {'terms': terms, 'form': form})

@login_required
@admin_required
def term_create(request):
    form = AcademicTermForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        term = form.save(commit=False)
        if term.current:
            AcademicTerm.objects.filter(current=True).update(current=False)
        term.save()
        messages.success(request, 'Term added successfully.')
        return redirect('academics:term_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Create Term'})

@login_required
@admin_required
def term_update(request, pk):
    term = get_object_or_404(AcademicTerm, pk=pk)
    form = AcademicTermForm(request.POST or None, instance=term)
    if request.method == 'POST' and form.is_valid():
        term = form.save(commit=False)
        if term.current:
            AcademicTerm.objects.filter(current=True).exclude(pk=pk).update(current=False)
        term.save()
        messages.success(request, 'Term updated successfully.')
        return redirect('academics:term_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Edit Term'})

@login_required
@admin_required
def term_delete(request, pk):
    if request.method == 'POST':
        term = get_object_or_404(AcademicTerm, pk=pk)
        if term.current:
            return JsonResponse({'status': 'error', 'message': 'Cannot delete active term.'}, status=400)
        term.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Subjects ──────────────────────────────────────────────
@login_required
@admin_required
def subject_list(request):
    subjects = Subject.objects.all()
    form = SubjectForm()
    return render(request, 'academics/subject_list.html', {'subjects': subjects, 'form': form})

@login_required
@admin_required
def subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject created successfully.')
        return redirect('academics:subject_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Create Subject'})

@login_required
@admin_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject updated.')
        return redirect('academics:subject_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Edit Subject'})

@login_required
@admin_required
def subject_delete(request, pk):
    if request.method == 'POST':
        subject = get_object_or_404(Subject, pk=pk)
        subject.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Student Classes ───────────────────────────────────────
@login_required
@admin_required
def class_list(request):
    classes = StudentClass.objects.prefetch_related('subjects').all()
    form = StudentClassForm()
    return render(request, 'academics/class_list.html', {'classes': classes, 'form': form})

@login_required
@admin_required
def class_create(request):
    form = StudentClassForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Class created successfully.')
        return redirect('academics:class_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Create Class'})

@login_required
@admin_required
def class_update(request, pk):
    student_class = get_object_or_404(StudentClass, pk=pk)
    form = StudentClassForm(request.POST or None, instance=student_class)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Class updated successfully.')
        return redirect('academics:class_list')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Edit Class'})

@login_required
@admin_required
def class_delete(request, pk):
    if request.method == 'POST':
        student_class = get_object_or_404(StudentClass, pk=pk)
        student_class.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Grade Entry & Performance ─────────────────────────────
@login_required
@teacher_required
def grade_entry(request):
    from apps.people.models import Teacher as TeacherModel

    if request.user.is_admin:
        classes = StudentClass.objects.all()
    else:
        teacher = get_object_or_404(TeacherModel, user=request.user)
        classes = teacher.assigned_classes.all()

    sessions = AcademicSession.objects.all()
    terms    = AcademicTerm.objects.all()

    # ── Auto-select defaults ──────────────────────────────
    # Class: auto if only one assigned
    if not request.GET.get('student_class') and classes.count() == 1:
        selected_class_id = str(classes.first().pk)
    else:
        selected_class_id = request.GET.get('student_class')

    # Session: use GET or fall back to active
    if not request.GET.get('session'):
        active_session = AcademicSession.objects.filter(current=True).first()
        selected_session_id = str(active_session.pk) if active_session else None
    else:
        selected_session_id = request.GET.get('session')

    # Term: use GET or fall back to active
    if not request.GET.get('term'):
        active_term = AcademicTerm.objects.filter(current=True).first()
        selected_term_id = str(active_term.pk) if active_term else None
    else:
        selected_term_id = request.GET.get('term')

    selected_subject_id = request.GET.get('subject')

    subjects         = []
    students         = []
    page_obj         = None
    grades_dict      = {}
    selected_class   = None
    selected_subject = None
    selected_session = None
    selected_term    = None

    if selected_class_id:
        selected_class = get_object_or_404(StudentClass, pk=selected_class_id)

        if not request.user.is_admin:
            if selected_class not in classes:
                messages.error(request, 'You are not assigned to this class.')
                return redirect('academics:grade_entry')

        subjects = selected_class.subjects.all()

        # Auto-select first subject if none chosen
        if not selected_subject_id and subjects.exists():
            selected_subject_id = str(subjects.first().pk)

        all_students = Student.objects.filter(
            student_class=selected_class, is_active=True
        ).select_related('user')

        if selected_class_id and selected_subject_id and selected_session_id and selected_term_id:
            selected_subject = get_object_or_404(Subject, pk=selected_subject_id)
            selected_session = get_object_or_404(AcademicSession, pk=selected_session_id)
            selected_term    = get_object_or_404(AcademicTerm, pk=selected_term_id)

            existing_grades = Grade.objects.filter(
                student_class=selected_class,
                subject=selected_subject,
                session=selected_session,
                term=selected_term,
            )
            grades_dict = {g.student_id: g for g in existing_grades}

            if request.method == 'POST':
                for s in all_students:
                    test_score = request.POST.get(f'test_{s.pk}', 0)
                    exam_score = request.POST.get(f'exam_{s.pk}', 0)
                    try:
                        test_score = int(test_score) if test_score else 0
                        exam_score = int(exam_score) if exam_score else 0
                    except ValueError:
                        test_score = 0
                        exam_score = 0
                    grade_obj, _ = Grade.objects.get_or_create(
                        student=s,
                        subject=selected_subject,
                        session=selected_session,
                        term=selected_term,
                        defaults={'student_class': selected_class}
                    )
                    grade_obj.student_class = selected_class
                    grade_obj.test_score    = test_score
                    grade_obj.exam_score    = exam_score
                    grade_obj.save()

                messages.success(request, 'Grades saved successfully.')
                return redirect(
                    f"{request.path}?student_class={selected_class_id}"
                    f"&subject={selected_subject_id}"
                    f"&session={selected_session_id}"
                    f"&term={selected_term_id}"
                )

        # Attach grade objects then paginate
        for s in all_students:
            s.grade_obj = grades_dict.get(s.pk)

        from django.core.paginator import Paginator
        paginator = Paginator(list(all_students), 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))
        students  = page_obj

    context = {
        'classes'          : classes,
        'sessions'         : sessions,
        'terms'            : terms,
        'subjects'         : subjects,
        'students'         : students,
        'page_obj'         : page_obj,
        'grades_dict'      : grades_dict,
        'selected_class'   : selected_class,
        'selected_subject' : selected_subject,
        'selected_session' : selected_session,
        'selected_term'    : selected_term,
        'selected_class_id'   : selected_class_id,
        'selected_subject_id' : selected_subject_id,
        'selected_session_id' : selected_session_id,
        'selected_term_id'    : selected_term_id,
    }
    return render(request, 'academics/grade_entry.html', context)


@login_required
@teacher_required
def save_student_grades(request):
    """AJAX POST: save all subjects' grades for a single student from the modal."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    from apps.people.models import Teacher as TeacherModel
    student_id = request.POST.get('student_id')
    session_id = request.POST.get('session_id')
    term_id = request.POST.get('term_id')

    student = get_object_or_404(Student, pk=student_id)

    # Access control
    if not request.user.is_admin:
        teacher = get_object_or_404(TeacherModel, user=request.user)
        if student.student_class not in teacher.assigned_classes.all():
            return JsonResponse({'error': 'Access denied.'}, status=403)

    session = get_object_or_404(AcademicSession, pk=session_id) if session_id else None
    term = get_object_or_404(AcademicTerm, pk=term_id) if term_id else None

    if not session or not term:
        return JsonResponse({'error': 'No active session or term.'}, status=400)

    if not student.student_class:
        return JsonResponse({'error': 'Student has no assigned class.'}, status=400)

    subjects = student.student_class.subjects.all()
    saved_count = 0
    for subj in subjects:
        test_score_raw = request.POST.get(f'test_{subj.pk}', '0')
        exam_score_raw = request.POST.get(f'exam_{subj.pk}', '0')
        try:
            test_score = max(0, min(40, int(test_score_raw or 0)))
            exam_score = max(0, min(60, int(exam_score_raw or 0)))
        except ValueError:
            test_score, exam_score = 0, 0

        grade_obj, _ = Grade.objects.get_or_create(
            student=student,
            subject=subj,
            session=session,
            term=term,
            defaults={'student_class': student.student_class}
        )
        grade_obj.student_class = student.student_class
        grade_obj.test_score = test_score
        grade_obj.exam_score = exam_score
        grade_obj.save()
        saved_count += 1

    return JsonResponse({'status': 'ok', 'saved': saved_count, 'student': student.user.get_full_name()})


# @login_required
# def student_report_card(request, student_id):
#     student = get_object_or_404(Student, pk=student_id)

#     if request.user.is_parent:
#         if not student.grades_visible:
#             messages.error(request, 'Grades are not yet available. Please ensure fees are fully paid.')
#             return redirect('finance:invoice_list')
#     # Check permissions
#     if not request.user.is_admin:
#         if request.user.is_student and request.user.student_profile != student:
#             messages.error(request, 'Access denied.')
#             return redirect('/')
#         elif request.user.is_parent and student not in request.user.parent_profile.students.all():
#             messages.error(request, 'Access denied.')
#             return redirect('/')

#     # Get active session and term
#     active_session = AcademicSession.objects.filter(current=True).first()
#     active_term = AcademicTerm.objects.filter(current=True).first()

#     grades = Grade.objects.filter(student=student)
#     if active_session:
#         grades = grades.filter(session=active_session)
#     if active_term:
#         grades = grades.filter(term=active_term)
        
#     grades = grades.select_related('subject', 'session', 'term')

#     avg_score = 0
#     if grades.exists():
#         avg_score = sum(g.total_score() for g in grades) / grades.count()

#     context = {
#         'student': student,
#         'grades': grades,
#         'active_session': active_session,
#         'active_term': active_term,
#         'avg_score': avg_score,
#     }
#     return render(request, 'academics/report_card.html', context)


@login_required
def student_report_card(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.user.is_parent:
        if not student.grades_visible:
            messages.error(request, 'Grades not yet available. Please ensure fees are fully paid.')
            return redirect('finance:invoice_list')

    if not request.user.is_admin:
        if request.user.is_student and request.user.student_profile != student:
            messages.error(request, 'Access denied.')
            return redirect('/')
        elif request.user.is_parent and student not in request.user.parent_profile.students.all():
            messages.error(request, 'Access denied.')
            return redirect('/')

    active_session = AcademicSession.objects.filter(current=True).first()
    all_terms      = AcademicTerm.objects.all().order_by('name')
    subjects       = student.student_class.subjects.all() if student.student_class else []
    active_term = AcademicTerm.objects.filter(current=True).first()


    # Build grade matrix: {subject_id: {term_id: grade_obj}}
    all_grades = Grade.objects.filter(
        student=student, session=active_session
    ).select_related('subject', 'term') if active_session else []

    grade_matrix = {}
    for g in all_grades:
        grade_matrix.setdefault(g.subject_id, {})[g.term_id] = g

    # Compute averages per term
    term_averages = {}
    for term in all_terms:
        scores = [
            grade_matrix.get(s.pk, {}).get(term.pk).total_score()
            for s in subjects
            if grade_matrix.get(s.pk, {}).get(term.pk)
        ]
        term_averages[term.pk] = round(sum(scores) / len(scores), 1) if scores else None

    # Fetch term reports
    term_reports = StudentTermReport.objects.filter(
        student=student, session=active_session
    ).select_related('term') if active_session else []
    term_report_map = {tr.term_id: tr for tr in term_reports}


    work_habits = [
        ('follows_directions',   'Follows directions'),
        ('works_independently',  'Works well independently'),
        ('attentive_in_class',   'Is attentive in class'),
        ('does_work_neatly',     'Does work neatly'),
        ('completes_daily_work', 'Completes daily work'),
        ('completes_homework',   'Completes homework'),
    ]
    social_habits = [
        ('is_courteous',            'Is courteous'),
        ('gets_along_with_others',  'Gets along with others'),
        ('exhibits_self_control',   'Exhibits self-control'),
        ('does_not_disturb_others', 'Does not disturb others'),
        ('shows_respect',           'Shows respect for authority'),
        ('responds_to_correction',  'Responds well to correction'),
    ]
    context = {
        'student'        : student,
        'active_session' : active_session,
        'active_term'       : active_term,                          # ← add
        'active_term_id'    : active_term.pk if active_term else None, 
        'all_terms'      : all_terms,
        'subjects'       : subjects,
        'grade_matrix'   : grade_matrix,
        'term_averages'  : term_averages,
        'term_report_map': term_report_map,
        'work_habits'  : work_habits,
        'social_habits': social_habits,
    }
    return render(request, 'academics/report_card.html', context)


from .models import StudentTermReport
from .forms import StudentTermReportForm

@login_required
@teacher_required
def save_term_report(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if not request.user.is_admin:
        from apps.people.models import Teacher as TeacherModel
        teacher = get_object_or_404(TeacherModel, user=request.user)
        if student.student_class not in teacher.assigned_classes.all():
            messages.error(request, 'Access denied.')
            return redirect('academics:grade_entry')

    active_session = get_object_or_404(AcademicSession, current=True)
    active_term    = get_object_or_404(AcademicTerm, current=True)

    report, _ = StudentTermReport.objects.get_or_create(
        student=student, session=active_session, term=active_term,
        defaults={'student_class': student.student_class}
    )
    form = StudentTermReportForm(request.POST or None, instance=report)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Term report saved.')
        return redirect('academics:student_report_card', student_id=student.pk)

    return render(request, 'academics/term_report_form.html', {
        'form': form, 'student': student,
        'active_session': active_session, 'active_term': active_term,
    })
