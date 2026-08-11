from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import admin_required, teacher_required
from apps.academics.models import AcademicSession, AcademicTerm, Grade
from .models import Student, Teacher, Parent
from .forms import StudentForm, TeacherForm, ParentForm,StudentBulkUploadForm
from apps.academics.models import StudentTermReport


# ── Students ──────────────────────────────────────────────
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
@teacher_required
def student_list(request):
    if request.user.is_admin:
        students = Student.objects.select_related('user', 'student_class').filter(is_active=True)
        teacher = None
    else:
        teacher = get_object_or_404(Teacher, user=request.user)
        assigned = teacher.assigned_classes.all()
        students = Student.objects.select_related('user', 'student_class').filter(
            is_active=True, student_class__in=assigned
        )

    search = request.GET.get('q', '').strip()
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(admission_no__icontains=search) |
            Q(student_class__name__icontains=search)
        )

    paginator = Paginator(students, 15)
    page_obj = paginator.get_page(request.GET.get('page',1))

    return render(request, 'people/student_list.html', {
        'students': page_obj,   # ← must be page_obj not students
        'page_obj': page_obj,
        'teacher': teacher,
        'search': search,
    })


@login_required
@teacher_required
def student_grades_json(request, pk):
    """AJAX: return a student's subjects + existing grades for the active session/term."""
    student = get_object_or_404(Student.objects.select_related('student_class', 'user'), pk=pk)

    # Access control: teachers can only see students in their classes
    if not request.user.is_admin:
        teacher = get_object_or_404(Teacher, user=request.user)
        if student.student_class not in teacher.assigned_classes.all():
            return JsonResponse({'error': 'Access denied.'}, status=403)

    active_session = AcademicSession.objects.filter(current=True).first()
    active_term = AcademicTerm.objects.filter(current=True).first()

    subjects = []
    if student.student_class:
        subjects = list(student.student_class.subjects.values('id', 'name'))

    grades_qs = Grade.objects.filter(student=student)
    if active_session:
        grades_qs = grades_qs.filter(session=active_session)
    if active_term:
        grades_qs = grades_qs.filter(term=active_term)

    grades_map = {
        g.subject_id: {
            'test': g.test_score,
            'exam': g.exam_score,
            'total': g.total_score(),
            'letter': g.grade_letter(),
            'remark': g.remark()
        } for g in grades_qs
    }

    for subj in subjects:
        g = grades_map.get(subj['id'], {})
        subj['test_score'] = g.get('test', 0)
        subj['exam_score'] = g.get('exam', 0)
        subj['total'] = g.get('total', 0)
        subj['letter'] = g.get('letter', 'F')
        subj['remark'] = g.get('remark', 'Fail')

    term_report = None
    if active_session and active_term:
        term_report = StudentTermReport.objects.filter(
            student=student, session=active_session, term=active_term
        ).first()

    return JsonResponse({
        'student_id': student.pk,
        'student_name': student.user.get_full_name(),
        'admission_no': student.admission_no,
        'class_name': student.student_class.name if student.student_class else '—',
        'session': active_session.name if active_session else '—',
        'term': active_term.name if active_term else '—',
        'session_id': active_session.pk if active_session else None,
        'term_id': active_term.pk if active_term else None,
        'subjects': subjects,
        'teacher_comment': term_report.teacher_comment if term_report else '',
    })


@login_required
@admin_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student created.')
        return redirect('people:student_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Add student'})


@login_required
@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student,
                       user_instance=student.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student updated.')
        return redirect('people:student_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Edit student'})


@login_required
@admin_required
def student_delete(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=pk)
        student.user.delete()   # cascades to student profile
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@teacher_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('user'), pk=pk)
    if not request.user.is_admin:
        teacher = get_object_or_404(Teacher, user=request.user)
        if student.student_class not in teacher.assigned_classes.all():
            messages.error(request, 'Access denied to this student.')
            return redirect('people:student_list')
    return render(request, 'people/student_detail.html', {'student': student})

from django.http import HttpResponse
import csv

@login_required
@admin_required
def student_bulk_upload(request):
    form = StudentBulkUploadForm(request.POST or None, request.FILES or None)
    results = []

    if request.method == 'POST' and form.is_valid():
        results = form.process()
        created = sum(1 for r in results if r['status'] == 'ok')
        skipped = sum(1 for r in results if r['status'] == 'skip')
        errors  = sum(1 for r in results if r['status'] == 'error')
        messages.success(
            request,
            f'Done — {created} created, {skipped} skipped, {errors} errors.'
        )

    return render(request, 'people/student_bulk_upload.html', {
        'form': form,
        'results': results,
    })


@login_required
@admin_required
def student_bulk_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
    writer = csv.writer(response)
    writer.writerow(['first_name', 'last_name', 'username', 'admission_no',
                     'date_of_birth', 'gender', 'blood_group', 'class', 'address', 'password'])
    writer.writerow(['John', 'Doe', 'john.doe', 'ADM001',
                     '2010-05-15', 'M', 'O+', 'Form 1A', '123 Main St', 'changeme123'])
    return response


# ── Teachers ──────────────────────────────────────────────
@login_required
@admin_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').filter(is_active=True)
    return render(request, 'people/teacher_list.html', {'teachers': teachers})


@login_required
@admin_required
def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher created.')
        return redirect('people:teacher_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Add teacher'})


@login_required
@admin_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher,
                       user_instance=teacher.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher updated.')
        return redirect('people:teacher_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Edit teacher'})


@login_required
@admin_required
def teacher_delete(request, pk):
    if request.method == 'POST':
        teacher = get_object_or_404(Teacher, pk=pk)
        teacher.user.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Parents ───────────────────────────────────────────────
@login_required
@admin_required
def parent_list(request):
    parents = Parent.objects.select_related('user').all()
    return render(request, 'people/parent_list.html', {'parents': parents})


@login_required
@admin_required
def parent_create(request):
    form = ParentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parent created.')
        return redirect('people:parent_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Add parent'})


@login_required
@admin_required
def parent_update(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    form = ParentForm(request.POST or None, instance=parent,
                      user_instance=parent.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parent updated.')
        return redirect('people:parent_list')
    return render(request, 'people/person_form.html', {'form': form, 'title': 'Edit parent'})


@login_required
@admin_required
def parent_delete(request, pk):
    if request.method == 'POST':
        parent = get_object_or_404(Parent, pk=pk)
        parent.user.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@admin_required
def toggle_grades_visibility(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=pk)
        student.grades_visible = not student.grades_visible
        student.save(update_fields=['grades_visible'])
        status = 'visible' if student.grades_visible else 'hidden'
        return JsonResponse({'status': 'ok', 'visible': student.grades_visible, 'label': status})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@admin_required
def student_search_ajax(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        students = Student.objects.select_related('user').filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(admission_no__icontains=q)
        )[:30]
        for student in students:
            results.append({
                'id': student.id,
                'text': f"{student.user.get_full_name()} ({student.admission_no})"
            })
    return JsonResponse({'results': results})