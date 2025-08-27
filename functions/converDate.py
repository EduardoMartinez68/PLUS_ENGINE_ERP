from datetime import datetime
import pytz

def convert_to_utc(date_obj: datetime, user_timezone_str: str) -> datetime:
    """
    Converts a naive datetime from the user's time zone to UTC.

    :param date_obj: Naive datetime (without tzinfo)
    :param user_timezone_str: Time zone string, e.g., 'America/Mexico_City'
    :return: Datetime in UTC
    """
    user_tz = pytz.timezone(user_timezone_str)
    localized_date = user_tz.localize(date_obj)  # converts to aware in user's zone
    return localized_date.astimezone(pytz.UTC)   # converts to UTC

def convert_from_utc(utc_date: datetime, user_timezone_str: str) -> datetime:
    """
    Converts a UTC datetime to the user's timezone.

    :param utc_date: UTC-aware datetime
    :param user_timezone_str: Timezone string, e.g., 'America/Mexico_City'
    :return: Datetime adjusted to the user's timezone
    """
    user_tz = pytz.timezone(user_timezone_str)
    return utc_date.astimezone(user_tz)