from django.utils import timezone
from datetime import timedelta

def get_current_datetime():
    """Get current datetime in UTC."""
    return timezone.now()

def add_days(date, days):
    """Add days to a date."""
    return date + timedelta(days=days)

def add_hours(datetime_obj, hours):
    """Add hours to a datetime."""
    return datetime_obj + timedelta(hours=hours)

def calculate_duration(start_time, end_time):
    """Calculate duration between two datetimes."""
    return end_time - start_time

def is_date_past(date):
    """Check if a date is in the past."""
    return date < timezone.now()

def is_date_future(date):
    """Check if a date is in the future."""
    return date > timezone.now()
