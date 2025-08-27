#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.db.models import F
from ..models import TypeAppoint
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
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #--------------------
            print(body_json)
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
            date_start = None
            date_finish = None
    
            time_alert = body_json.get("alert_time", "0") #this is for know when to alert in minute
            priority = body_json.get("priority", "0") #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = None
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat", "") #this is for that the ERP knows how often to repeat this event in days
            finish_repeat_date = body_json.get("time_end_repeat", "")
    
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
            user = request.user
    
            #her we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=400)
            
    
    
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    else:
        if request.method == 'POST':
            try:
                body_json = json.loads(request.body)  # convert bytes to Python
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'message.error.the-form-have-a-error', 'error': str(e)}, status=400)
    
            #--------------------
            print(body_json)
            titleEvent = body_json.get("name_event", "").strip()
            description = body_json.get("description", "")
            date_start = None
            date_finish = None
    
            time_alert = body_json.get("alert_time", "0") #this is for know when to alert in minute
            priority = body_json.get("priority", "0") #for default the priority is equal to 0
            activate_event_all_the_day = body_json.get("activate_event_all_the_day") == "on"
    
    
            emails_guests = None
            location = body_json.get("location", "")
            link = body_json.get("link", "")
    
            repeat_this_event = body_json.get("repeat_this_event") == "on" #True/False
            time_repeat =  body_json.get("time_repeat", "") #this is for that the ERP knows how often to repeat this event in days
            finish_repeat_date = body_json.get("time_end_repeat", "")
    
    
            send_notification = body_json.get("send_notification") == "on"  # True/False
            i_am_free = body_json.get("i_am_free") == "on"  # True/False
            
            id_type_appoint = body_json.get("type_event", None) #get the id of the type of event
            user = request.user
    
            #her we will see if the user added a name to the event
            if not titleEvent:
                return JsonResponse({'success': False, 'message': 'message.error.need-a-name-for-your-event'}, status=400)
            
    
    
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
    
            print(body_json)
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
    
            print(body_json)
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

