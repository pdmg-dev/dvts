"""Jinja2 custom filters for the application."""

from datetime import datetime
from decimal import Decimal


def format_currency(value):
    """Format a number as Philippine Peso currency.

    Args:
        value: Number to format (int, float, Decimal, or string)

    Returns:
        Formatted currency string (e.g., "₱1,234.56")
    """
    if value is None:
        return "₱0.00"

    try:
        amount = Decimal(str(value))
        return f"₱{amount:,.2f}"
    except (ValueError, TypeError):
        return "₱0.00"


def format_date(value, format_string="%b %d, %Y"):
    """Format a date or datetime object.

    Args:
        value: datetime or date object
        format_string: strftime format string (default: "Month DD, YYYY")

    Returns:
        Formatted date string
    """
    if value is None:
        return ""

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value

    return value.strftime(format_string)


def format_datetime(value):
    """Smart datetime formatter for Jinja."""

    if value is None:
        return ""

    # If value is a string, parse it
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value  # Return original if parsing fails

    now = datetime.now()

    # Case 1: Today → time only
    if value.date() == now.date():
        return value.strftime("%I:%M %p").lstrip("0")  # Remove leading zero

    # Case 2: This year → Month + Day
    if value.year == now.year:
        return value.strftime("%b %d")

    # Case 3: Different year → Full date
    return value.strftime("%m/%d/%y")


def truncate_text(value, length=50, suffix="..."):
    """Truncate text to a specified length.

    Args:
        value: String to truncate
        length: Maximum length before truncation
        suffix: String to append when truncated (default: "...")

    Returns:
        Truncated string with suffix if needed
    """
    if value is None:
        return ""

    value = str(value)
    if len(value) <= length:
        return value

    return value[:length].rsplit(" ", 1)[0] + suffix


def nl2br(value):
    """Convert newlines to HTML <br> tags.

    Args:
        value: String with newlines

    Returns:
        String with <br> tags
    """
    if value is None:
        return ""

    return str(value).replace("\n", "<br>")


def init_filters(app):
    """Register all custom filters with the Flask app.

    Args:
        app: Flask application instance
    """
    app.jinja_env.filters["currency"] = format_currency
    app.jinja_env.filters["date"] = format_date
    app.jinja_env.filters["datetime"] = format_datetime
    app.jinja_env.filters["truncate_text"] = truncate_text
    app.jinja_env.filters["nl2br"] = nl2br
