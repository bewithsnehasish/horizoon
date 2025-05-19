from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

aadhaar_regex = RegexValidator(
    regex=r"^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$",
    message="Aadhaar number must be 12 digits long, should not start with 0 or 1, and should not contain any spaces or special characters",
    code="invalid_aadhaar",
)
