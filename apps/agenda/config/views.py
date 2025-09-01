#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.utils.timezone import  make_aware, is_naive, get_default_timezone
from dateutil.relativedelta import relativedelta
from django.utils.timezone import localtime
from dateutil import parser as ps
from django.utils import timezone
from ..plus_wrapper import Plus
import os
import sys
from datetime import datetime, timedelta, time
from django.db.models import F
from ..models import TypeAppoint, Appointment
from django.http import JsonResponse
import json
from django.shortcuts import render
from email import parser
@login_required(login_url='login')
def agenda_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_agenda.html')
    else:
        return render(request, 'home_agenda.html')

@login_required(login_url='login')
def create_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        def get_date_of_the_event(user, body_json: json) -> dict:
            #data that get of the user from the frontend
            date_startDay =  body_json.get("start_date", "")
            date_startHour =  body_json.get("start_time", "")
    
            date_finishDay =  body_json.get("end_date", "")
            date_finishHour =  body_json.get("end_time", "")
    
            #convert the information to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
    
    
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': date_start_utc,
                'end': date_finish_utc
            }
        
        def validate_date_range(start: datetime, end: datetime) -> bool:
            """
            Verifies that the start date is less or equals than the end date.
            Returns True if valid, False otherwise.
            """
            if start > end:
                return False
            return True
    
    
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #get the data of the user
            user = request.user
    
            #--------------------get the data of the form---------------------
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
    
            time_alert = body_json.get("alert_time") or 0 #this is for know when to alert in minute
            priority = body_json.get("priority") or 0 #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = body_json.get("emails_guests", []) #this is a list of emails
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat") or 0 #this is for that the ERP knows how often to repeat this event in days
            time_end_repeat = body_json.get("time_end_repeat") or None #this is for that the ERP knows when to stop repeating this event in days
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
    
            
            #first here we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=200)
    
            #---------------------------get the information of the date of the event--------------------------
            event_dates = get_date_of_the_event(user, body_json)
            date_start=event_dates['start'] #date when start the event
            date_finish=event_dates['end'] #date when finish the event
    
            date_end_repeat = date_start + timedelta(days=int(time_end_repeat))
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            #now we will to create a appointment
            try:
                appointment = Appointment.objects.create(
                    title=titleEvent,
                    description=description,
                    date_start=date_start,
                    date_finish=date_finish,
                    time_alert=int(time_alert),
                    priority=int(priority),
                    activate_event_all_the_day=activate_event_all_the_day,
                    emails_guests=emails_guests,
                    location=location,
                    link=link,
                    repeat_this_event=repeat_this_event,
                    time_repeat=int(time_repeat) if time_repeat else 0,
                    finish_repeat_date=date_end_repeat if date_end_repeat else None,
                    send_notification=send_notification,
                    i_am_free=i_am_free,
                    id_type_appoint_id=id_type_appoint, 
                    user=user
                )
    
                #return the new event with his id for that in the frontend can use it
                return JsonResponse({'success': True, 'message': 'message.success.add-new-event', 'event_id': appointment.id}, status=200)
    
            except Exception as e:
                print("Error creating event:", e)
                return JsonResponse({'success': False, 'message': 'message.success.not-can-add-new-event', 'error': str(e)}, status=200)
            
    
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    else:
        def get_date_of_the_event(user, body_json: json) -> dict:
            #data that get of the user from the frontend
            date_startDay =  body_json.get("start_date", "")
            date_startHour =  body_json.get("start_time", "")
    
            date_finishDay =  body_json.get("end_date", "")
            date_finishHour =  body_json.get("end_time", "")
    
            #convert the information to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
    
    
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': date_start_utc,
                'end': date_finish_utc
            }
        
        def validate_date_range(start: datetime, end: datetime) -> bool:
            """
            Verifies that the start date is less or equals than the end date.
            Returns True if valid, False otherwise.
            """
            if start > end:
                return False
            return True
    
    
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #get the data of the user
            user = request.user
    
            #--------------------get the data of the form---------------------
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
    
            time_alert = body_json.get("alert_time") or 0 #this is for know when to alert in minute
            priority = body_json.get("priority") or 0 #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = body_json.get("emails_guests", []) #this is a list of emails
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat") or 0 #this is for that the ERP knows how often to repeat this event in days
            time_end_repeat = body_json.get("time_end_repeat") or None #this is for that the ERP knows when to stop repeating this event in days
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
    
            
            #first here we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=200)
    
            #---------------------------get the information of the date of the event--------------------------
            event_dates = get_date_of_the_event(user, body_json)
            date_start=event_dates['start'] #date when start the event
            date_finish=event_dates['end'] #date when finish the event
    
            date_end_repeat = date_start + timedelta(days=int(time_end_repeat))
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            #now we will to create a appointment
            try:
                appointment = Appointment.objects.create(
                    title=titleEvent,
                    description=description,
                    date_start=date_start,
                    date_finish=date_finish,
                    time_alert=int(time_alert),
                    priority=int(priority),
                    activate_event_all_the_day=activate_event_all_the_day,
                    emails_guests=emails_guests,
                    location=location,
                    link=link,
                    repeat_this_event=repeat_this_event,
                    time_repeat=int(time_repeat) if time_repeat else 0,
                    finish_repeat_date=date_end_repeat if date_end_repeat else None,
                    send_notification=send_notification,
                    i_am_free=i_am_free,
                    id_type_appoint_id=id_type_appoint, 
                    user=user
                )
    
                #return the new event with his id for that in the frontend can use it
                return JsonResponse({'success': True, 'message': 'message.success.add-new-event', 'event_id': appointment.id}, status=200)
    
            except Exception as e:
                print("Error creating event:", e)
                return JsonResponse({'success': False, 'message': 'message.success.not-can-add-new-event', 'error': str(e)}, status=200)
            
    
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@login_required(login_url='login')
def get_events_by_date_range(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        """
       Get all events of a user between start_date and end_date.
    
        Parameters:
            user: CustomUser instance
            start_date: Start datetime of the range
            end_date: End datetime of the range
    
        Return:
            Appointment QuerySet sorted by start date
        """
        def add_event_to_the_list(e, date_start, date_finish):
            return {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date_start': localtime(date_start).isoformat(),
                'date_finish': localtime(date_finish).isoformat(),
                'time_alert': e.time_alert,
                'priority': e.priority,
                'activate_event_all_the_day': e.activate_event_all_the_day,
                'emails_guests': e.emails_guests,
                'location': e.location,
                'link': e.link,
                'repeat_this_event': e.repeat_this_event,
                'time_repeat': e.time_repeat,
                'finish_repeat_date': e.finish_repeat_date.isoformat() if e.finish_repeat_date else None,
                'send_notification': e.send_notification,
                'i_am_free': e.i_am_free,
                'type_appoint': {
                    'id': e.id_type_appoint.id if e.id_type_appoint else None,
                    'name': e.id_type_appoint.name if e.id_type_appoint else None,
                    'description': e.id_type_appoint.description if e.id_type_appoint else None,
                    'color': e.id_type_appoint.color if e.id_type_appoint else None,
                }
            }
    
        def create_events_that_need_most_of_a_day(e, date_start, date_finish):
            events_data=[]
            #here we will see if this event is only a day or this event spans multiple days
            if date_start.date() != date_finish.date():
                #now we will to create all the event in the week
                current_date = date_start.date()
                end_date = date_finish.date()
    
                while current_date <= end_date:
                    current_date = date_start.date()
                    end_date = date_finish.date()
    
                    while current_date <= end_date:
                        # start of the day's piece
                        if current_date == date_start.date():
                            start_time = date_start.time()
                        else:
                            start_time = time(0, 0)
    
                        # end of the day's piece
                        if current_date == date_finish.date():
                            end_time = date_finish.time()
                        else:
                            end_time = time(23, 59)
    
                        # create datetime for the chunk
                        chunk_start = datetime.combine(current_date, start_time, tzinfo=date_start.tzinfo)
                        chunk_end = datetime.combine(current_date, end_time, tzinfo=date_start.tzinfo)
    
                        events_data.append(add_event_to_the_list(e, chunk_start, chunk_end))
    
                        #next day
                        current_date += timedelta(days=1)
            else:
                # Event is only one day
                events_data.append(add_event_to_the_list(e, date_start, date_finish))
    
    
            return events_data
     
    
        def get_the_events_repeat_of_the_user(user, start_date: datetime, end_date: datetime) -> list:
            #start_date and end_date is date that was transform to the time of the user from the GET
            #get the appoints in the database that can be repeat
            events = Appointment.objects.filter(
                user=user,
                repeat_this_event=True#,
                #finish_repeat_date__gte=F('date_start')  # this is for get only appoints that not was finished 
            ).select_related('id_type_appoint').order_by('date_start') 
    
            events_data = [] #here we will save all the events that can repeat
            
            #we will to read all the event that get from the database
            for e in events:
                #now we will get the duration of the event 
                duration = e.date_finish - e.date_start
                hours = duration.total_seconds() / 3600 #convert to hours. This is for add the time after 
    
                #now we will see when time is repeat the event 1 day, 1 week, 1 month, etc.
                time_repeat=e.time_repeat
    
                #conver the time to the time of the user 
                #this is for change the time of the event to the time of the user
                e.date_start=Plus.convert_from_utc(e.date_start, user.timezone) 
                e.date_finish=Plus.convert_from_utc(e.date_finish, user.timezone) 
    
                #this is for not have a error when need see when finish the event
                if e.finish_repeat_date != None:
                    e.finish_repeat_date=Plus.convert_from_utc(e.finish_repeat_date, user.timezone) 
    
                #need see in that day start the event 
                #this is for choose the day when start the event 
                while e.date_start < start_date:
                    if time_repeat == 1: #day 
                        e.date_start += timedelta(days=1)
                    elif time_repeat == 7: #week
                        e.date_start += timedelta(weeks=1)
                    elif time_repeat == 15: #week
                        e.date_start += timedelta(weeks=2)
                    elif time_repeat == 30: #month
                        e.date_start += relativedelta(months=1)
                    elif time_repeat == 365: #year
                        e.date_start += relativedelta(years=1)
                    else: 
                        break
                
                #when we found teh day where start the calendar, now we can start to create the events 
                #that show in the calendar
                start_date_appoint=e.date_start
    
                #while the start date be <= end_date of the calendar, we will to create new events
                #also think that need see if the repeat of the event finish
                while start_date_appoint <= end_date and (e.finish_repeat_date is None or e.finish_repeat_date > start_date_appoint):
    
                    time_end = start_date_appoint  #this is for save when start the event for change after 
                    date_start = start_date_appoint
    
                    #now we will to create the appoint that send to the frontend
                    if time_repeat == 1: #day 
                        start_date_appoint += timedelta(days=1)
                    elif time_repeat == 7: #week
                        start_date_appoint += timedelta(weeks=1)
                    elif time_repeat == 15: #week
                        start_date_appoint += timedelta(weeks=2)
                    elif time_repeat == 30: #month
                        start_date_appoint += relativedelta(months=1)
                    elif time_repeat == 365: #year
                        start_date_appoint += relativedelta(years=1)
                    else: 
                        break
                    
                    
    
                    #this is for change the time of the event adding to it the hours of duration
                    time_end += timedelta(hours=hours) 
                    
                    #now we will to create a list for save all struct of the event in the calendar in the frontend
                    #for that if the event have a duration of most of a day, show the event broken
                    events_data+=create_events_that_need_most_of_a_day(e, date_start, time_end)
                    
    
    
            return events_data
    
        if request.method == 'GET':
            #cget the data that the frontend send with date
            date_start = request.GET.get('start_date')
            date_finish = request.GET.get('end_date')
    
            #get the date of the user, but need convert to lenguace UTC for search the container in the database
            #because in the database the time is UTC
            start_date = Plus.convert_to_utc(date_start, request.user.timezone)
            end_date = Plus.convert_to_utc(date_finish, request.user.timezone)
    
            #We filter events that are within the range of dates but there is still a lack get the appoints that can repeat 
            user = request.user
            events = Appointment.objects.filter(
                user=user,
                date_start__lte=end_date,
                date_finish__gte=start_date
            ).select_related('id_type_appoint').order_by('date_start')
    
            #first get the event that the user would like repeat 
            events_data=get_the_events_repeat_of_the_user(user, start_date, end_date)
    
            #here we will to serialize the date
            for e in events:
                #convert the format of the date UTC that is save in the server and the transform to the hour of the user 
                date_start = Plus.convert_from_utc(e.date_start, request.user.timezone)
                date_finish = Plus.convert_from_utc(e.date_finish, request.user.timezone)
    
                #here we will see if this event is only a day or this event spans multiple days
                events_data+=create_events_that_need_most_of_a_day(e, date_start, date_finish)
                '''
                if date_start.date() != date_finish.date():
                    #now we will to create all the event in the week
                    current_date = date_start.date()
                    end_date = date_finish.date()
    
                    while current_date <= end_date:
                        current_date = date_start.date()
                        end_date = date_finish.date()
    
                        while current_date <= end_date:
                            # start of the day's piece
                            if current_date == date_start.date():
                                start_time = date_start.time()
                            else:
                                start_time = time(0, 0)
    
                            # end of the day's piece
                            if current_date == date_finish.date():
                                end_time = date_finish.time()
                            else:
                                end_time = time(23, 59)
    
                            # create datetime for the chunk
                            chunk_start = datetime.combine(current_date, start_time, tzinfo=date_start.tzinfo)
                            chunk_end = datetime.combine(current_date, end_time, tzinfo=date_start.tzinfo)
    
                            events_data.append(add_event_to_the_list(e, chunk_start, chunk_end))
    
                            #next day
                            current_date += timedelta(days=1)
                else:
                    # Event is only one day
                    events_data.append(add_event_to_the_list(e, date_start, date_finish))
                '''
            #this is for the frontend
            return JsonResponse({'success': True, 'data': events_data}, status=200)
    else:
        """
       Get all events of a user between start_date and end_date.
    
        Parameters:
            user: CustomUser instance
            start_date: Start datetime of the range
            end_date: End datetime of the range
    
        Return:
            Appointment QuerySet sorted by start date
        """
        def add_event_to_the_list(e, date_start, date_finish):
            return {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date_start': localtime(date_start).isoformat(),
                'date_finish': localtime(date_finish).isoformat(),
                'time_alert': e.time_alert,
                'priority': e.priority,
                'activate_event_all_the_day': e.activate_event_all_the_day,
                'emails_guests': e.emails_guests,
                'location': e.location,
                'link': e.link,
                'repeat_this_event': e.repeat_this_event,
                'time_repeat': e.time_repeat,
                'finish_repeat_date': e.finish_repeat_date.isoformat() if e.finish_repeat_date else None,
                'send_notification': e.send_notification,
                'i_am_free': e.i_am_free,
                'type_appoint': {
                    'id': e.id_type_appoint.id if e.id_type_appoint else None,
                    'name': e.id_type_appoint.name if e.id_type_appoint else None,
                    'description': e.id_type_appoint.description if e.id_type_appoint else None,
                    'color': e.id_type_appoint.color if e.id_type_appoint else None,
                }
            }
    
        def create_events_that_need_most_of_a_day(e, date_start, date_finish):
            events_data=[]
            #here we will see if this event is only a day or this event spans multiple days
            if date_start.date() != date_finish.date():
                #now we will to create all the event in the week
                current_date = date_start.date()
                end_date = date_finish.date()
    
                while current_date <= end_date:
                    current_date = date_start.date()
                    end_date = date_finish.date()
    
                    while current_date <= end_date:
                        # start of the day's piece
                        if current_date == date_start.date():
                            start_time = date_start.time()
                        else:
                            start_time = time(0, 0)
    
                        # end of the day's piece
                        if current_date == date_finish.date():
                            end_time = date_finish.time()
                        else:
                            end_time = time(23, 59)
    
                        # create datetime for the chunk
                        chunk_start = datetime.combine(current_date, start_time, tzinfo=date_start.tzinfo)
                        chunk_end = datetime.combine(current_date, end_time, tzinfo=date_start.tzinfo)
    
                        events_data.append(add_event_to_the_list(e, chunk_start, chunk_end))
    
                        #next day
                        current_date += timedelta(days=1)
            else:
                # Event is only one day
                events_data.append(add_event_to_the_list(e, date_start, date_finish))
    
    
            return events_data
     
    
        def get_the_events_repeat_of_the_user(user, start_date: datetime, end_date: datetime) -> list:
            #start_date and end_date is date that was transform to the time of the user from the GET
            #get the appoints in the database that can be repeat
            events = Appointment.objects.filter(
                user=user,
                repeat_this_event=True#,
                #finish_repeat_date__gte=F('date_start')  # this is for get only appoints that not was finished 
            ).select_related('id_type_appoint').order_by('date_start') 
    
            events_data = [] #here we will save all the events that can repeat
            
            #we will to read all the event that get from the database
            for e in events:
                #now we will get the duration of the event 
                duration = e.date_finish - e.date_start
                hours = duration.total_seconds() / 3600 #convert to hours. This is for add the time after 
    
                #now we will see when time is repeat the event 1 day, 1 week, 1 month, etc.
                time_repeat=e.time_repeat
    
                #conver the time to the time of the user 
                #this is for change the time of the event to the time of the user
                e.date_start=Plus.convert_from_utc(e.date_start, user.timezone) 
                e.date_finish=Plus.convert_from_utc(e.date_finish, user.timezone) 
    
                #this is for not have a error when need see when finish the event
                if e.finish_repeat_date != None:
                    e.finish_repeat_date=Plus.convert_from_utc(e.finish_repeat_date, user.timezone) 
    
                #need see in that day start the event 
                #this is for choose the day when start the event 
                while e.date_start < start_date:
                    if time_repeat == 1: #day 
                        e.date_start += timedelta(days=1)
                    elif time_repeat == 7: #week
                        e.date_start += timedelta(weeks=1)
                    elif time_repeat == 15: #week
                        e.date_start += timedelta(weeks=2)
                    elif time_repeat == 30: #month
                        e.date_start += relativedelta(months=1)
                    elif time_repeat == 365: #year
                        e.date_start += relativedelta(years=1)
                    else: 
                        break
                
                #when we found teh day where start the calendar, now we can start to create the events 
                #that show in the calendar
                start_date_appoint=e.date_start
    
                #while the start date be <= end_date of the calendar, we will to create new events
                #also think that need see if the repeat of the event finish
                while start_date_appoint <= end_date and (e.finish_repeat_date is None or e.finish_repeat_date > start_date_appoint):
    
                    time_end = start_date_appoint  #this is for save when start the event for change after 
                    date_start = start_date_appoint
    
                    #now we will to create the appoint that send to the frontend
                    if time_repeat == 1: #day 
                        start_date_appoint += timedelta(days=1)
                    elif time_repeat == 7: #week
                        start_date_appoint += timedelta(weeks=1)
                    elif time_repeat == 15: #week
                        start_date_appoint += timedelta(weeks=2)
                    elif time_repeat == 30: #month
                        start_date_appoint += relativedelta(months=1)
                    elif time_repeat == 365: #year
                        start_date_appoint += relativedelta(years=1)
                    else: 
                        break
                    
                    
    
                    #this is for change the time of the event adding to it the hours of duration
                    time_end += timedelta(hours=hours) 
                    
                    #now we will to create a list for save all struct of the event in the calendar in the frontend
                    #for that if the event have a duration of most of a day, show the event broken
                    events_data+=create_events_that_need_most_of_a_day(e, date_start, time_end)
                    
    
    
            return events_data
    
        if request.method == 'GET':
            #cget the data that the frontend send with date
            date_start = request.GET.get('start_date')
            date_finish = request.GET.get('end_date')
    
            #get the date of the user, but need convert to lenguace UTC for search the container in the database
            #because in the database the time is UTC
            start_date = Plus.convert_to_utc(date_start, request.user.timezone)
            end_date = Plus.convert_to_utc(date_finish, request.user.timezone)
    
            #We filter events that are within the range of dates but there is still a lack get the appoints that can repeat 
            user = request.user
            events = Appointment.objects.filter(
                user=user,
                date_start__lte=end_date,
                date_finish__gte=start_date
            ).select_related('id_type_appoint').order_by('date_start')
    
            #first get the event that the user would like repeat 
            events_data=get_the_events_repeat_of_the_user(user, start_date, end_date)
    
            #here we will to serialize the date
            for e in events:
                #convert the format of the date UTC that is save in the server and the transform to the hour of the user 
                date_start = Plus.convert_from_utc(e.date_start, request.user.timezone)
                date_finish = Plus.convert_from_utc(e.date_finish, request.user.timezone)
    
                #here we will see if this event is only a day or this event spans multiple days
                events_data+=create_events_that_need_most_of_a_day(e, date_start, date_finish)
                '''
                if date_start.date() != date_finish.date():
                    #now we will to create all the event in the week
                    current_date = date_start.date()
                    end_date = date_finish.date()
    
                    while current_date <= end_date:
                        current_date = date_start.date()
                        end_date = date_finish.date()
    
                        while current_date <= end_date:
                            # start of the day's piece
                            if current_date == date_start.date():
                                start_time = date_start.time()
                            else:
                                start_time = time(0, 0)
    
                            # end of the day's piece
                            if current_date == date_finish.date():
                                end_time = date_finish.time()
                            else:
                                end_time = time(23, 59)
    
                            # create datetime for the chunk
                            chunk_start = datetime.combine(current_date, start_time, tzinfo=date_start.tzinfo)
                            chunk_end = datetime.combine(current_date, end_time, tzinfo=date_start.tzinfo)
    
                            events_data.append(add_event_to_the_list(e, chunk_start, chunk_end))
    
                            #next day
                            current_date += timedelta(days=1)
                else:
                    # Event is only one day
                    events_data.append(add_event_to_the_list(e, date_start, date_finish))
                '''
            #this is for the frontend
            return JsonResponse({'success': True, 'data': events_data}, status=200)

@login_required(login_url='login')
def get_appointment_by_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            event_id = request.GET.get('id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'message.error.event-id-required'}, status=400)
    
            try:
                # select_related antes de get
                e = Appointment.objects.select_related('id_type_appoint').get(id=event_id, user=request.user)
            except Appointment.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
    
            # serializar
            date_start = Plus.convert_from_utc(e.date_start, request.user.timezone)
            date_finish = Plus.convert_from_utc(e.date_finish, request.user.timezone)
    
            event_data = {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date_start': localtime(date_start).isoformat(),
                'date_finish': localtime(date_finish).isoformat(),
                'time_alert': e.time_alert,
                'priority': e.priority,
                'activate_event_all_the_day': e.activate_event_all_the_day,
                'emails_guests': e.emails_guests,
                'location': e.location,
                'link': e.link,
                'repeat_this_event': e.repeat_this_event,
                'time_repeat': e.time_repeat,
                'finish_repeat_date': e.finish_repeat_date.isoformat() if e.finish_repeat_date else None,
                'send_notification': e.send_notification,
                'i_am_free': e.i_am_free,
                'type_appoint': {
                    'id': e.id_type_appoint.id if e.id_type_appoint else None,
                    'name': e.id_type_appoint.name if e.id_type_appoint else None,
                    'description': e.id_type_appoint.description if e.id_type_appoint else None,
                    'color': e.id_type_appoint.color if e.id_type_appoint else None,
                }
            }
    
            return JsonResponse({'success': True, 'data': event_data}, status=200)
    else:
        if request.method == 'GET':
            event_id = request.GET.get('id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'message.error.event-id-required'}, status=400)
    
            try:
                # select_related antes de get
                e = Appointment.objects.select_related('id_type_appoint').get(id=event_id, user=request.user)
            except Appointment.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'message.error.event-not-found'}, status=404)
    
            # serializar
            date_start = Plus.convert_from_utc(e.date_start, request.user.timezone)
            date_finish = Plus.convert_from_utc(e.date_finish, request.user.timezone)
    
            event_data = {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date_start': localtime(date_start).isoformat(),
                'date_finish': localtime(date_finish).isoformat(),
                'time_alert': e.time_alert,
                'priority': e.priority,
                'activate_event_all_the_day': e.activate_event_all_the_day,
                'emails_guests': e.emails_guests,
                'location': e.location,
                'link': e.link,
                'repeat_this_event': e.repeat_this_event,
                'time_repeat': e.time_repeat,
                'finish_repeat_date': e.finish_repeat_date.isoformat() if e.finish_repeat_date else None,
                'send_notification': e.send_notification,
                'i_am_free': e.i_am_free,
                'type_appoint': {
                    'id': e.id_type_appoint.id if e.id_type_appoint else None,
                    'name': e.id_type_appoint.name if e.id_type_appoint else None,
                    'description': e.id_type_appoint.description if e.id_type_appoint else None,
                    'color': e.id_type_appoint.color if e.id_type_appoint else None,
                }
            }
    
            return JsonResponse({'success': True, 'data': event_data}, status=200)

@login_required(login_url='login')
def edit_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        def get_date_of_the_event(user, body_json: json) -> dict:
            #data that get of the user from the frontend
            date_startDay =  body_json.get("start_date_edit", "")
            date_startHour =  body_json.get("start_time_edit", "")
    
            date_finishDay =  body_json.get("end_date_edit", "")
            date_finishHour =  body_json.get("end_time_edit", "")
    
            #convert to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
    
    
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': date_start_utc,
                'end': date_finish_utc
            }
        
        def validate_date_range(start: datetime, end: datetime) -> bool:
            """
            Verifies that the start date is less or equals than the end date.
            Returns True if valid, False otherwise.
            """
            if start > end:
                return False
            return True
    
    
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #her we will get all the information that send the frontend
            event_id = body_json.get('id_event')
    
    
            #get the data of the user
            user = request.user
    
            #--------------------get the data of the form---------------------
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
    
            time_alert = body_json.get("alert_time") or 0 #this is for know when to alert in minute
            priority = body_json.get("priority") or 0 #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = body_json.get("emails_guests", []) #this is a list of emails
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat") or 0 #this is for that the ERP knows how often to repeat this event in days
            time_end_repeat = body_json.get("time_end_repeat") or 0 #this is for that the ERP knows when to stop repeating this event in days
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
    
            
            #first here we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=200)
    
            #---------------------------get the information of the date of the event--------------------------
            event_dates = get_date_of_the_event(user, body_json)
            date_start=event_dates['start'] #date when start the event
            date_finish=event_dates['end'] #date when finish the event
    
            date_end_repeat=None
            
            if time_end_repeat!='0':
                date_end_repeat = date_start + timedelta(days=int(time_end_repeat))
    
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            #now we will to create a appointment
            try:
                appointment = Appointment.objects.get(id=event_id, user=user)
    
                appointment.title = titleEvent
                appointment.description = description
                appointment.date_start = date_start
                appointment.date_finish = date_finish
                appointment.time_alert = int(time_alert)
                appointment.priority = int(priority)
                appointment.activate_event_all_the_day = activate_event_all_the_day
                appointment.emails_guests = emails_guests
                appointment.location = location
                appointment.link = link
                appointment.repeat_this_event = repeat_this_event
                appointment.time_repeat = int(time_repeat) if time_repeat else 0
                appointment.finish_repeat_date = date_end_repeat if date_end_repeat else None
                appointment.send_notification = send_notification
                appointment.i_am_free = i_am_free
                appointment.id_type_appoint_id = id_type_appoint
    
                appointment.save()
    
                return JsonResponse({
                    'success': True,
                    'message': 'message.success.event-updated',
                    'event_id': appointment.id
                }, status=200)
    
            except Appointment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'message.error.event-not-found',
                    "error": "The event was not found"
                }, status=404)
    
            except Exception as e:
                print("Error updating event:", e)
                return JsonResponse({
                    'success': False,
                    'message': 'message.error.cannot-update-event',
                    'error': str(e)
                }, status=500)
    else:
        def get_date_of_the_event(user, body_json: json) -> dict:
            #data that get of the user from the frontend
            date_startDay =  body_json.get("start_date_edit", "")
            date_startHour =  body_json.get("start_time_edit", "")
    
            date_finishDay =  body_json.get("end_date_edit", "")
            date_finishHour =  body_json.get("end_time_edit", "")
    
            #convert to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
    
    
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': date_start_utc,
                'end': date_finish_utc
            }
        
        def validate_date_range(start: datetime, end: datetime) -> bool:
            """
            Verifies that the start date is less or equals than the end date.
            Returns True if valid, False otherwise.
            """
            if start > end:
                return False
            return True
    
    
    
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #her we will get all the information that send the frontend
            event_id = body_json.get('id_event')
    
    
            #get the data of the user
            user = request.user
    
            #--------------------get the data of the form---------------------
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
    
            time_alert = body_json.get("alert_time") or 0 #this is for know when to alert in minute
            priority = body_json.get("priority") or 0 #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = body_json.get("emails_guests", []) #this is a list of emails
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat") or 0 #this is for that the ERP knows how often to repeat this event in days
            time_end_repeat = body_json.get("time_end_repeat") or 0 #this is for that the ERP knows when to stop repeating this event in days
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
    
            
            #first here we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=200)
    
            #---------------------------get the information of the date of the event--------------------------
            event_dates = get_date_of_the_event(user, body_json)
            date_start=event_dates['start'] #date when start the event
            date_finish=event_dates['end'] #date when finish the event
    
            date_end_repeat=None
            
            if time_end_repeat!='0':
                date_end_repeat = date_start + timedelta(days=int(time_end_repeat))
    
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            #now we will to create a appointment
            try:
                appointment = Appointment.objects.get(id=event_id, user=user)
    
                appointment.title = titleEvent
                appointment.description = description
                appointment.date_start = date_start
                appointment.date_finish = date_finish
                appointment.time_alert = int(time_alert)
                appointment.priority = int(priority)
                appointment.activate_event_all_the_day = activate_event_all_the_day
                appointment.emails_guests = emails_guests
                appointment.location = location
                appointment.link = link
                appointment.repeat_this_event = repeat_this_event
                appointment.time_repeat = int(time_repeat) if time_repeat else 0
                appointment.finish_repeat_date = date_end_repeat if date_end_repeat else None
                appointment.send_notification = send_notification
                appointment.i_am_free = i_am_free
                appointment.id_type_appoint_id = id_type_appoint
    
                appointment.save()
    
                return JsonResponse({
                    'success': True,
                    'message': 'message.success.event-updated',
                    'event_id': appointment.id
                }, status=200)
    
            except Appointment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'message.error.event-not-found',
                    "error": "The event was not found"
                }, status=404)
    
            except Exception as e:
                print("Error updating event:", e)
                return JsonResponse({
                    'success': False,
                    'message': 'message.error.cannot-update-event',
                    'error': str(e)
                }, status=500)

@login_required(login_url='login')
def get_the_first_type_events(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
    
                #if exist a list we will get the first data 
                if isinstance(body_json, list) and len(body_json) > 0:
                    search_text = body_json[0]
                else:
                    search_text = ""
            except Exception as e:
                print("Error parsing JSON:", e)
                search_text = ""
    
            try:
                search_text=body_json
    
                #we will see if need get the value for a query. This is when need update a table or a container
                search_text=body_json.get("query", search_text).strip()
            except:
                pass 
    
            #now we will see if exist it for search
            if search_text:
                #search the text that the user would like get from the server
                events = TypeAppoint.objects.filter(
                    user=request.user, name__icontains=search_text
                ).annotate(
                    text=F('name')
                ).values('id', 'text', 'description', 'color')[:20]
            else:
                # if not exist a text for search, we will get the first 20 object from the database and return the information
                events = TypeAppoint.objects.filter(
                    user=request.user
                ).annotate(
                    text=F('name')
                ).values('id', 'text', 'description', 'color')[:20]
    
            return JsonResponse({'success': True, 'results': list(events)})
    
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    else:
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
    
                #if exist a list we will get the first data 
                if isinstance(body_json, list) and len(body_json) > 0:
                    search_text = body_json[0]
                else:
                    search_text = ""
            except Exception as e:
                print("Error parsing JSON:", e)
                search_text = ""
    
            try:
                search_text=body_json
    
                #we will see if need get the value for a query. This is when need update a table or a container
                search_text=body_json.get("query", search_text).strip()
            except:
                pass 
    
            #now we will see if exist it for search
            if search_text:
                #search the text that the user would like get from the server
                events = TypeAppoint.objects.filter(
                    user=request.user, name__icontains=search_text
                ).annotate(
                    text=F('name')
                ).values('id', 'text', 'description', 'color')[:20]
            else:
                # if not exist a text for search, we will get the first 20 object from the database and return the information
                events = TypeAppoint.objects.filter(
                    user=request.user
                ).annotate(
                    text=F('name')
                ).values('id', 'text', 'description', 'color')[:20]
    
            return JsonResponse({'success': True, 'results': list(events)})
    
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@login_required(login_url='login')
def get_type_event_for_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            type_id = request.GET.get('id')
    
            try:
                if type_id:
                    answer = TypeAppoint.objects.filter(id=type_id, user=request.user).annotate(
                        text=F('name')
                    ).values('id', 'text', 'description', 'color').first()
    
                    if not answer:
                        return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.'}, status=404)
    
                    return JsonResponse({'success': True, 'answer': answer})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al obtener el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'GET':
            type_id = request.GET.get('id')
    
            try:
                if type_id:
                    answer = TypeAppoint.objects.filter(id=type_id, user=request.user).annotate(
                        text=F('name')
                    ).values('id', 'text', 'description', 'color').first()
    
                    if not answer:
                        return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.'}, status=404)
    
                    return JsonResponse({'success': True, 'answer': answer})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al obtener el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def create_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
    
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD').strip()
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error to create this type of event.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        data = json.loads(request.body)
    
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD').strip()
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error to create this type of event.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def update_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
                title = data.get('title', '').strip()
                color = data.get('color', '').strip()
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'Se requiere un nombre para el tipo de evento.', 'error': 'Title is empty'}, status=400)
    
                # Verificamos que el type event exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Actualizamos los campos
                type_event.name = title
                if color:
                    type_event.color = color
                type_event.save()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento actualizado correctamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al actualizar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
                title = data.get('title', '').strip()
                color = data.get('color', '').strip()
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'Se requiere un nombre para el tipo de evento.', 'error': 'Title is empty'}, status=400)
    
                # Verificamos que el type event exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Actualizamos los campos
                type_event.name = title
                if color:
                    type_event.color = color
                type_event.save()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento actualizado correctamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al actualizar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required(login_url='login')
def delete_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                # Verificamos que exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Eliminamos el tipo de evento
                type_event.delete()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento eliminado correctamente.'})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al eliminar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('id')
    
                if not type_id:
                    return JsonResponse({'success': False, 'message': 'ID del tipo de evento requerido.', 'error': 'Missing type event id'}, status=400)
    
                # Verificamos que exista y pertenezca al usuario
                try:
                    type_event = TypeAppoint.objects.get(id=type_id, user=request.user)
                except TypeAppoint.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Tipo de evento no encontrado o no tienes permiso.', 'error': 'Not found or unauthorized'}, status=404)
    
                # Eliminamos el tipo de evento
                type_event.delete()
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento eliminado correctamente.'})
    
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al eliminar el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

