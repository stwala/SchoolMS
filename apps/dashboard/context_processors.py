# apps/dashboard/context_processors.py
from .models import SchoolSettings

def school_settings(request):
    return {'school_settings': SchoolSettings.get()}