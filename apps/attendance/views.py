from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import localdate
from apps.accounts.decorators import admin_required, teacher_required
from apps.academics.models import StudentClass
from apps.people.models import Student
from .models import Attendance

from django.core.paginator import Paginator

@login_required
@teacher_required
def attendance_record(request):
    if request.user.is_admin:
        classes = StudentClass.objects.all()
    else:
        from apps.people.models import Teacher
        teacher = get_object_or_404(Teacher, user=request.user)
        classes = teacher.assigned_classes.all()

    # Auto-select if only one class
    if not request.GET.get('student_class') and classes.count() == 1:
        selected_class_id = str(classes.first().pk)
    else:
        selected_class_id = request.GET.get('student_class')

    selected_date_str = request.GET.get('date', localdate().isoformat())
    selected_class = None
    students = []
    page_obj = None

    if selected_class_id:
        if not request.user.is_admin:
            if not classes.filter(pk=selected_class_id).exists():
                messages.error(request, 'Access denied to this class.')
                return redirect('attendance:record')

        selected_class = get_object_or_404(StudentClass, pk=selected_class_id)
        all_students = Student.objects.filter(
            student_class=selected_class, is_active=True
        ).select_related('user')

        if request.method == 'POST':
            # Process ALL students on POST, not just current page
            for s in all_students:
                status  = request.POST.get(f'status_{s.pk}', 'present')
                remarks = request.POST.get(f'remarks_{s.pk}', '')
                att_obj, _ = Attendance.objects.get_or_create(
                    student=s,
                    date=selected_date_str,
                    defaults={'student_class': selected_class}
                )
                att_obj.student_class = selected_class
                att_obj.status  = status
                att_obj.remarks = remarks
                att_obj.save()

            messages.success(request, 'Attendance recorded successfully.')
            return redirect(
                f"{request.path}?student_class={selected_class_id}&date={selected_date_str}"
            )

        # Attach attendance objects then paginate
        exist_att = Attendance.objects.filter(
            student_class=selected_class, date=selected_date_str
        )
        attendance_dict = {a.student_id: a for a in exist_att}
        for s in all_students:
            s.attendance_obj = attendance_dict.get(s.pk)

        paginator = Paginator(all_students, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))
        students  = page_obj

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'selected_class_id': selected_class_id,
        'selected_date': selected_date_str,
        'students': students,
        'page_obj': page_obj,
    }
    return render(request, 'attendance/record.html', context)

@login_required
@teacher_required
def ajax_mark_attendance(request):
    """AJAX REST-like endpoint to mark attendance dynamically."""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        date_str = request.POST.get('date')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')

        if not student_id or not date_str or not status:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters.'}, status=400)

        student = get_object_or_404(Student, pk=student_id)
        
        att_obj, created = Attendance.objects.get_or_create(
            student=student,
            date=date_str,
            defaults={'student_class': student.student_class}
        )
        att_obj.status = status
        if remarks:
            att_obj.remarks = remarks
        att_obj.save()

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@login_required
@teacher_required
def attendance_report(request):
    if request.user.is_admin:
        classes = StudentClass.objects.all()
    else:
        from apps.people.models import Teacher
        teacher = get_object_or_404(Teacher, user=request.user)
        classes = teacher.assigned_classes.all()

    # Auto-select if only one class
    if not request.GET.get('student_class') and classes.count() == 1:
        selected_class_id = str(classes.first().pk)
    else:
        selected_class_id = request.GET.get('student_class')

    selected_class = None
    report_data = []
    page_obj = None

    if selected_class_id:
        if not request.user.is_admin:
            if not classes.filter(pk=selected_class_id).exists():
                messages.error(request, 'Access denied to this class.')
                return redirect('attendance:report')

        selected_class = get_object_or_404(StudentClass, pk=selected_class_id)
        from django.db.models import Count, Q

        students = Student.objects.filter(
            student_class=selected_class, is_active=True
        ).select_related('user').annotate(
            total_days   = Count('attendances'),
            present_days = Count('attendances', filter=Q(attendances__status='present')),
            late_days    = Count('attendances', filter=Q(attendances__status='late')),
            absent_days  = Count('attendances', filter=Q(attendances__status='absent')),
            excused_days = Count('attendances', filter=Q(attendances__status='excused')),
        )

        all_report = []
        for s in students:
            attended = s.present_days + s.late_days
            rate     = (attended / s.total_days * 100) if s.total_days > 0 else 100.0
            all_report.append({
                'student'  : s,
                'total'    : s.total_days,
                'present'  : s.present_days,
                'late'     : s.late_days,
                'absent'   : s.absent_days,
                'excused'  : s.excused_days,
                'rate'     : rate,
                'alert'    : rate < 75.0,
            })

        paginator = Paginator(all_report, 10)
        page_obj  = paginator.get_page(request.GET.get('page', 1))
        report_data = page_obj

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'selected_class_id': selected_class_id,
        'report_data': report_data,
        'page_obj'         : page_obj,
    }
    return render(request, 'attendance/report.html', context)