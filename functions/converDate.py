from datetime import datetime
from dateutil import parser
import pytz

def convert_to_utc(date_obj: datetime, user_timezone_str: str) -> datetime:
    """
    Converts a naive datetime from the user's time zone to UTC.

    :param date_obj: Naive datetime (without tzinfo)
    :param user_timezone_str: Time zone string, e.g., 'America/Mexico_City'
    :return: Datetime in UTC
    """

    #first we will see if the date_obj is a string
    if isinstance(date_obj, str):
        date_obj = date_obj.split(' (')[0] #clear the timezone info
        date_obj = parser.parse(date_obj) #this is for transform the text a datetime and avoid errors
        
    # 2. If you already have tzinfo (e.g. GMT-0600), we go directly to UTC
    if date_obj.tzinfo:
        return date_obj.astimezone(pytz.UTC)
    
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