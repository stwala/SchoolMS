from django.db.models import Sum, Count
from apps.academics.models import Grade
from apps.dashboard.models import ClassNamingRule


def rank_students(student_class, session, term):

    students = student_class.students.all()

    rankings = []

    rule = ClassNamingRule.for_grade(student_class.grade_level)
    ranking_method = rule.ranking_method if rule else 'marks'

    for student in students:

        grades = Grade.objects.filter(
            student=student, student_class=student_class, session=session, term=term
        )

        if ranking_method == "marks":

            total_marks = sum(grade.total_score() for grade in grades)

            subjects_count = grades.count()

            average = total_marks / subjects_count if subjects_count else 0

            rankings.append(
                {
                    "student": student,
                    "total_marks": total_marks,
                    "average": average,
                    "grade": calculate_grade(average),
                    "remark": calculate_remark(average),
                }
            )

    # highest marks first
    rankings.sort(key=lambda x: x["total_marks"], reverse=True)

    for position, row in enumerate(rankings, start=1):
        row["position"] = position

    return rankings


def calculate_grade(score):

    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def calculate_remark(score):

    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    else:
        return "Needs Improvement"
