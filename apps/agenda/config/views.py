#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..plus_wrapper import Plus
import os
import sys
from datetime import datetime
from django.db.models import F
from ..models import TypeAppoint, Appointment
from django.http import JsonResponse
import json
from django.shortcuts import render
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
            date_finishDay =  body_json.get("end_date", "")
            date_startHour =  body_json.get("start_time", "")
            date_finishHour =  body_json.get("end_time", "")
    
            #convert to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
            
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': Plus.convert_from_utc(date_start_utc, timezone),
                'end': Plus.convert_from_utc(date_finish_utc, timezone)
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
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            print("Date Start:", date_start)
            print("Date Finish:", date_finish)
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
                    finish_repeat_date=None,
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
            date_finishDay =  body_json.get("end_date", "")
            date_startHour =  body_json.get("start_time", "")
            date_finishHour =  body_json.get("end_time", "")
    
            #convert to datetime 
            date_start = datetime.strptime(f"{date_startDay} {date_startHour}", "%Y-%m-%d %H:%M")
            date_finish = datetime.strptime(f"{date_finishDay} {date_finishHour}", "%Y-%m-%d %H:%M")
            
            #get the time zone of the user 
            timezone=user.timezone
            date_start_utc = Plus.convert_to_utc(date_start, timezone)
            date_finish_utc = Plus.convert_to_utc(date_finish, timezone)
    
            return {
                'start': Plus.convert_from_utc(date_start_utc, timezone),
                'end': Plus.convert_from_utc(date_finish_utc, timezone)
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
    
            #here we will see if the date start is valid and the date finish is valid
            if not validate_date_range(date_start, date_finish):
                return JsonResponse({'success': False, 'message': 'message.error.invalid-date-range'}, status=200)
            
            print("Date Start:", date_start)
            print("Date Finish:", date_finish)
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
                    finish_repeat_date=None,
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
    
            search_text=body_json
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
    
            search_text=body_json
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
def create_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD')
    
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
                return JsonResponse({'success': False, 'message': 'Error al crear el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD')
    
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
                return JsonResponse({'success': False, 'message': 'Error al crear el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

