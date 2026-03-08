from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def validate_phone_number(value):
    """Validate phone number format."""
    if not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValidationError(_('Invalid phone number format'))

def validate_postal_code(value):
    """Validate postal code format."""
    if not re.match(r'^\d{5}(-\d{4})?$', value):
        raise ValidationError(_('Invalid postal code format'))

def validate_license_plate(value):
    """Validate license plate format."""
    if not re.match(r'^[A-Z0-9]{2,8}$', value):
        raise ValidationError(_('Invalid license plate format'))

def validate_vin(value):
    """Validate VIN (Vehicle Identification Number)."""
    if len(value) != 17:
        raise ValidationError(_('VIN must be 17 characters long'))
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', value):
        raise ValidationError(_('Invalid VIN format'))
