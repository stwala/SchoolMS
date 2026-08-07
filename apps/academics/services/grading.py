"""
Academic grading utilities.

Handles:
- converting scores into grade letters
- converting grades into points for senior secondary ranking
"""


def get_grade_letter(score):
    """
    Convert percentage score into grade letter.
    
    Adjust these ranges according to your school's grading policy.
    """

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



def get_grade_points(score):
    """
    Senior secondary points system.

    Lower points are better:
    A = 1
    B = 2
    ...
    F = 9
    """

    if score >= 75:
        return 1
    elif score >= 70:
        return 2
    elif score >= 65:
        return 3
    elif score >= 60:
        return 4
    elif score >= 55:
        return 5
    elif score >= 50:
        return 6
    elif score >= 45:
        return 7
    elif score >= 40:
        return 8
    else:
        return 9