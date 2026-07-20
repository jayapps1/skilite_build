from django.core.validators import RegexValidator


validate_hex_color = RegexValidator(
    regex=r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$",
    message=(
        "Enter a valid HEX colour such as #2563EB "
        "or an eight-digit value such as #2563EBFF."
    ),
)
