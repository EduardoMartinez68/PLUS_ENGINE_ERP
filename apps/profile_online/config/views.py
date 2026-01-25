#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
import pytz
from datetime import datetime, time
from apps.agenda.models import Appointment
from apps.profile_online.models import PublicProfile,ProfileService, AppointmentOnline
from django.http import JsonResponse
from datetime import datetime, timedelta
from ..services.appoints import get_online_schedules_of_profile, create_schedule_online, update_schedule_online
from ..services.address import save_profile_location
from ..services.schedule import update_profile_schedule
from ..services.services import add_services, update_services
from ..services.profile import get_information_of_the_profile, update_profile_online, get_available_slots
import json 
from django.http import JsonResponse
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def profile_online_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'profile_online/home_profile_online.html')
    else:
        return render(request, 'profile_online/home_profile_online.html')

@login_required(login_url='login')
def get_information_of_profile_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        result=get_information_of_the_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        result=get_information_of_the_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_profile_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=update_profile_online(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=update_profile_online(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_add_services(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=add_services(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=add_services(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_services(request, service_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=update_services(request.user, service_id, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=update_services(request.user, service_id, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_schedule(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=update_profile_schedule(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=update_profile_schedule(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_address(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=save_profile_location(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
    
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=save_profile_location(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_get_information_about_appoints_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        result=get_online_schedules_of_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        result=get_online_schedules_of_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_add_schedule_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=create_schedule_online(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=create_schedule_online(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_schedule_online(request, id_schedule):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=update_schedule_online(request.user, data, id_schedule) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'POST': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
    
        result=update_schedule_online(request.user, data, id_schedule) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

def view_profile(request, slug):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        profile = (
            PublicProfile.objects
                .select_related("user", "user__subscription", "user__subscription__plan")
                .prefetch_related(
                    "services",
                    "schedules",
                    "locations",
                    "reviews",
                )
                .filter(
                    public_slug=slug,
                    is_public=True
                )
                .first()
        )
    
        # if the profile not exist now we will to render a web of error
        if not profile:
            return render(
                request,
                "profile_online/profile_not_available.html",
                status=404  # SEO-friendly
            )
    
        #now we will see if exist this subscription and get the type need
        subscription = getattr(profile.user, 'subscription', None)
        if not subscription or not subscription.have_profile_online():
                return render(
                    request, 
                    "profile_online/profile_not_available.html", 
                    status=403
                )
        
        # address
        main_location = next(
            (loc for loc in profile.locations.all() if loc.is_main),
            None
        )
    
    
        #here we will to see that picture use 
        DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/2716/2716038.png"
        avatar_url = DEFAULT_AVATAR
        if profile.profile_image:
            avatar_url = profile.profile_image.url
        elif hasattr(profile.user, "avatar") and profile.user.avatar:
            avatar_url = profile.user.avatar.url
    
    
        context = {
            "profile": profile,
            "avatar_url": avatar_url,
            "main_location": main_location,
            "services": profile.services.filter(is_active=True).order_by("order"),
            "schedules": profile.schedules.all(),
            "reviews": profile.reviews.filter(is_approved=True),
        }
    
        return render(request, 'profile_online/profile.html', context)
    else:
        profile = (
            PublicProfile.objects
                .select_related("user", "user__subscription", "user__subscription__plan")
                .prefetch_related(
                    "services",
                    "schedules",
                    "locations",
                    "reviews",
                )
                .filter(
                    public_slug=slug,
                    is_public=True
                )
                .first()
        )
    
        # if the profile not exist now we will to render a web of error
        if not profile:
            return render(
                request,
                "profile_online/profile_not_available.html",
                status=404  # SEO-friendly
            )
    
        #now we will see if exist this subscription and get the type need
        subscription = getattr(profile.user, 'subscription', None)
        if not subscription or not subscription.have_profile_online():
                return render(
                    request, 
                    "profile_online/profile_not_available.html", 
                    status=403
                )
        
        # address
        main_location = next(
            (loc for loc in profile.locations.all() if loc.is_main),
            None
        )
    
    
        #here we will to see that picture use 
        DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/2716/2716038.png"
        avatar_url = DEFAULT_AVATAR
        if profile.profile_image:
            avatar_url = profile.profile_image.url
        elif hasattr(profile.user, "avatar") and profile.user.avatar:
            avatar_url = profile.user.avatar.url
    
    
        context = {
            "profile": profile,
            "avatar_url": avatar_url,
            "main_location": main_location,
            "services": profile.services.filter(is_active=True).order_by("order"),
            "schedules": profile.schedules.all(),
            "reviews": profile.reviews.filter(is_approved=True),
        }
    
        return render(request, 'profile_online/profile.html', context)

def view_schedules_online_json(request, slug):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    
        profile = PublicProfile.objects.filter(public_slug=slug, is_public=True).first()
        if not profile:
            return JsonResponse({"success": False, "message": "Perfil no encontrado"}, status=404)
    
        start_date_str = request.GET.get("start_date")
        if not start_date_str:
            return JsonResponse({"success": False, "message": "start_date es requerido"}, status=400)
    
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=6)
    
        slots = get_available_slots(profile, start_date, end_date)
    
        # Organizar slots por día
        days = {}
        for slot in slots:
            day = slot["date"].strftime("%A")  # lunes, martes...
            if day not in days:
                days[day] = []
            days[day].append({
                "date": slot["date"].strftime("%Y-%m-%d"),
                "start_time": slot["start_time"].strftime("%H:%M"),
                "end_time": slot["end_time"].strftime("%H:%M"),
            })
    
        return JsonResponse({
            "success": True,
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        })
    else:
    
        profile = PublicProfile.objects.filter(public_slug=slug, is_public=True).first()
        if not profile:
            return JsonResponse({"success": False, "message": "Perfil no encontrado"}, status=404)
    
        start_date_str = request.GET.get("start_date")
        if not start_date_str:
            return JsonResponse({"success": False, "message": "start_date es requerido"}, status=400)
    
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=6)
    
        slots = get_available_slots(profile, start_date, end_date)
    
        # Organizar slots por día
        days = {}
        for slot in slots:
            day = slot["date"].strftime("%A")  # lunes, martes...
            if day not in days:
                days[day] = []
            days[day].append({
                "date": slot["date"].strftime("%Y-%m-%d"),
                "start_time": slot["start_time"].strftime("%H:%M"),
                "end_time": slot["end_time"].strftime("%H:%M"),
            })
    
        return JsonResponse({
            "success": True,
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        })

def reserve_appointment(request, slug):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)
    
        profile = PublicProfile.objects.filter(public_slug=slug, is_public=True).first()
        if not profile:
            return JsonResponse({"success": False, "message": "Perfil no encontrado"}, status=404)
    
        try:
            customer_name = request.POST.get("customer_name")
            customer_email = request.POST.get("customer_email")
            customer_phone = request.POST.get("customer_phone")
            service_id = request.POST.get("service")
            date_str = request.POST.get("date")
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
    
            if not all([customer_name, customer_email, customer_phone, service_id, date_str, start_time_str, end_time_str]):
                return JsonResponse({"success": False, "message": "Todos los campos son obligatorios"})
    
            service = ProfileService.objects.filter(id=service_id, profile=profile).first()
            if not service:
                return JsonResponse({"success": False, "message": "Servicio no válido"})
    
            appointment_online = AppointmentOnline.objects.create(
                profile=profile,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                service=service,
                date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                start_time=time.fromisoformat(start_time_str),
                end_time=time.fromisoformat(end_time_str),
                status="pending",
            )
           # ------------------------
            # 2️⃣ Crear cita en agenda
            # ------------------------
            # calcular datetime de inicio y fin
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            start_time_obj = time.fromisoformat(start_time_str)
            end_time_obj = time.fromisoformat(end_time_str)
            
            # si quieres asignar un customer y usuario específico
            user = profile.user  # si tu PublicProfile tiene el doctor como user
            doctor_tz = pytz.timezone(user.timezone or 'America/Mexico_City')
            start_datetime = doctor_tz.localize(datetime.combine(date_obj, start_time_obj))
            end_datetime = doctor_tz.localize(datetime.combine(date_obj, end_time_obj))
    
            # si no, asigna un usuario por defecto o haz un lookup
            appointment_agenda = Appointment.objects.create(
                title=f"Cita Online: {customer_name}",
                description=f"Servicio: {service.name}",
                date_start=start_datetime,
                date_finish=end_datetime,
                user=user,
                customer=None,  # si tienes un Customer relacionado, puedes buscarlo por email o nombre
                online_appointment_id=appointment_online.id
            )
    
            from apps.agenda.services.email import send_reminder_to_the_customer
            send_reminder_to_the_customer(appointment_agenda, 0)
    
            return JsonResponse({"success": True, "message": "Cita reservada con éxito"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)
    
        profile = PublicProfile.objects.filter(public_slug=slug, is_public=True).first()
        if not profile:
            return JsonResponse({"success": False, "message": "Perfil no encontrado"}, status=404)
    
        try:
            customer_name = request.POST.get("customer_name")
            customer_email = request.POST.get("customer_email")
            customer_phone = request.POST.get("customer_phone")
            service_id = request.POST.get("service")
            date_str = request.POST.get("date")
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
    
            if not all([customer_name, customer_email, customer_phone, service_id, date_str, start_time_str, end_time_str]):
                return JsonResponse({"success": False, "message": "Todos los campos son obligatorios"})
    
            service = ProfileService.objects.filter(id=service_id, profile=profile).first()
            if not service:
                return JsonResponse({"success": False, "message": "Servicio no válido"})
    
            appointment_online = AppointmentOnline.objects.create(
                profile=profile,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                service=service,
                date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                start_time=time.fromisoformat(start_time_str),
                end_time=time.fromisoformat(end_time_str),
                status="pending",
            )
           # ------------------------
            # 2️⃣ Crear cita en agenda
            # ------------------------
            # calcular datetime de inicio y fin
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            start_time_obj = time.fromisoformat(start_time_str)
            end_time_obj = time.fromisoformat(end_time_str)
            
            # si quieres asignar un customer y usuario específico
            user = profile.user  # si tu PublicProfile tiene el doctor como user
            doctor_tz = pytz.timezone(user.timezone or 'America/Mexico_City')
            start_datetime = doctor_tz.localize(datetime.combine(date_obj, start_time_obj))
            end_datetime = doctor_tz.localize(datetime.combine(date_obj, end_time_obj))
    
            # si no, asigna un usuario por defecto o haz un lookup
            appointment_agenda = Appointment.objects.create(
                title=f"Cita Online: {customer_name}",
                description=f"Servicio: {service.name}",
                date_start=start_datetime,
                date_finish=end_datetime,
                user=user,
                customer=None,  # si tienes un Customer relacionado, puedes buscarlo por email o nombre
                online_appointment_id=appointment_online.id
            )
    
            from apps.agenda.services.email import send_reminder_to_the_customer
            send_reminder_to_the_customer(appointment_agenda, 0)
    
            return JsonResponse({"success": True, "message": "Cita reservada con éxito"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

def guest_confirm_appointment(request, appoint_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 1. Buscar la cita o lanzar 404 si no existe
        try:
            appointment = Appointment.objects.get(id=appoint_id)
        except Appointment.DoesNotExist:
            # En lugar de 404 genérico, enviamos a tu propio template de error
            return render(request, 'webs/error_appointment_not_found.html', {
                'message': 'Lo sentimos, el enlace de esta cita no es válido o ha expirado.'
            }, status=404)
        
        # 2. Si es una petición POST, procesamos la respuesta del cliente
        if request.method == 'POST':
            action = request.POST.get('action') # 'confirm' o 'cancel'
            
            if appointment.status == 'C': # 'C' de Confirmada
                return JsonResponse({'success': False, 'message': 'Esta cita ya había sido confirmada previamente.'})
            
            if action == 'confirm':
                appointment.status = 'C'
                appointment.save()
                return JsonResponse({'success': True, 'message': '¡Cita confirmada con éxito!'})
            
            elif action == 'cancel':
                appointment.status = 'X' # 'X' de Cancelada
                appointment.save()
                return JsonResponse({'success': True, 'message': 'Cita cancelada. Gracias por avisarnos.'})
    
        # 3. Si es GET, renderizamos la página de confirmación
        # Pasamos el estado para saber si mostrar los botones o un mensaje de "Ya procesada"
        context = {
            'appointment': appointment,
            'is_pending': appointment.status == 'P', # Solo mostramos botones si está Pendiente
        }
        return render(request, 'profile_online/confirm_appoints.html', context)
    else:
        # 1. Buscar la cita o lanzar 404 si no existe
        try:
            appointment = Appointment.objects.get(id=appoint_id)
        except Appointment.DoesNotExist:
            # En lugar de 404 genérico, enviamos a tu propio template de error
            return render(request, 'webs/error_appointment_not_found.html', {
                'message': 'Lo sentimos, el enlace de esta cita no es válido o ha expirado.'
            }, status=404)
        
        # 2. Si es una petición POST, procesamos la respuesta del cliente
        if request.method == 'POST':
            action = request.POST.get('action') # 'confirm' o 'cancel'
            
            if appointment.status == 'C': # 'C' de Confirmada
                return JsonResponse({'success': False, 'message': 'Esta cita ya había sido confirmada previamente.'})
            
            if action == 'confirm':
                appointment.status = 'C'
                appointment.save()
                return JsonResponse({'success': True, 'message': '¡Cita confirmada con éxito!'})
            
            elif action == 'cancel':
                appointment.status = 'X' # 'X' de Cancelada
                appointment.save()
                return JsonResponse({'success': True, 'message': 'Cita cancelada. Gracias por avisarnos.'})
    
        # 3. Si es GET, renderizamos la página de confirmación
        # Pasamos el estado para saber si mostrar los botones o un mensaje de "Ya procesada"
        context = {
            'appointment': appointment,
            'is_pending': appointment.status == 'P', # Solo mostramos botones si está Pendiente
        }
        return render(request, 'profile_online/confirm_appoints.html', context)

