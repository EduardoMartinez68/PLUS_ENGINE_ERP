from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch, UserRole, Role, UserDepartment, Permit, CustomUser, SubscriptionPlan, UserSubscription, UserSession
import os
from django.utils import timezone
from datetime import timedelta

#when tis we will read our file .env
from dotenv import load_dotenv 
from django.contrib.auth.decorators import login_required

load_dotenv()
KEY_TINYMCE = os.getenv('KEY_TINYMCE')

@login_required(login_url='login')
def home(request):
    apps = APPS_CACHE
    user = request.user
    company = user.company  # Company instance
    branch = user.branch  # Branch instance

    return render(request, 'core/home.html',{'apps': apps,'KEY_TINYMCE':KEY_TINYMCE,'user': user,'company': company,'branch': branch})

from django.shortcuts import render, redirect


#here we will import the message for translate the ERP with the language of the user
from apps.rolesAndPermissions.services.permits import get_all_the_permissions

#send emails to the users
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def get_languages_of_the_erp():
    #if the user not have a login, now we will get all the language that exist in the system of home
    base_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'language')
    base_path = os.path.abspath(base_path)
    languages = [
        name for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]

    return languages

def send_welcome_email(user):
    """
    Send a welcome email to a new registered user
    """
    company_name=os.getenv('NAME_COMPANY', 'PLUS ERP')

    subject = "🎉 Bienvenido a " + company_name + " 🎉"
    from_email = settings.DEFAULT_FROM_EMAIL
    plus_url = settings.PLUS_URL

    to = [user.email]

    context = {
        "user_name": user.name,
        "user_email": user.email,
        "company_name": user.company.company_name if user.company else "",
        "login_url": f"https://{plus_url}/login/",
        "support_email": settings.DEFAULT_FROM_EMAIL,
    }

    # We render the HTML
    html_content = render_to_string("emails/welcome_email.html", context)

    # Plain text version (in case the client does not support HTML)
    text_content = f"""
    Hola {user.name},

    Bienvenido al mejor software para odontologos de Mexico.
    Tu cuenta ha sido creada correctamente.

    Puedes iniciar sesión aquí:
    {context['login_url']}

    ¡Gracias por confiar en nosotros!
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

#this function is for get the IP of the user that is register to the web
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

from django.conf import settings
def register(request):
    import re
    is_valid = True
    error_message = None
    form_login = {}
    languages=get_languages_of_the_erp()

    if request.method == 'POST':
        def is_valid_email(email):
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            return re.match(pattern, email) is not None

        data = request.POST  # QueryDict
        # --- Convertimos a diccionario plano ---
        form_login = {k: v[0] for k, v in data.lists()}

        if 'accept_terms' not in form_login:
            error_message = 'Debes aceptar los Términos y Condiciones.'
            is_valid = False

        # --- Check required fields ---
        required_fields = ['email', 'name', 'cellphone', 'country', 'password1', 'password2']
        missing_fields = [field for field in required_fields if not form_login[field]]
        if missing_fields:
            error_message = 'Por favor, completa todos los campos obligatorios.' #"home.message.please-fill-in-all-required-fields"
            is_valid = False

        # --- Validate passwords ---
        password1 = form_login['password1'].strip()
        password2 = form_login['password2'].strip()
        if password1 != password2 or not password1:
            error_message = 'Las contraseñas ingresadas no coinciden.' #'home.error.the-password-not-be-equals'
            is_valid = False
        elif len(password1) < 8:
            error_message = 'Las contraseñas debe tener minimo 8 caracteres.'
            is_valid = False
        elif not (re.search(r'[A-Z]', password1) and 
                  re.search(r'[a-z]', password1) and 
                  re.search(r'[0-9]', password1) and 
                  re.search(r'[!@#$%^&*(),.?":{}|<>]', password1)):
            error_message = 'La contraseña debe incluir una mayúscula, una minúscula, un número y un carácter especial.' #'home.error.the-password-need-more-characteres'
            is_valid = False

        # --- Validate cellphone ---
        cellphone_pattern = re.compile(r'^\+?\d{8,15}$')
        if not cellphone_pattern.match(form_login['cellphone']):
            error_message = 'El número ingresado no es correcto.' #"home.error.the-cellphone-no-exist"
            is_valid = False

        # --- Validate email ---
        emailUser=form_login['email'].strip().lower()
        if not is_valid_email(emailUser):
            error_message = 'El correo electronico no es valido.' #"home.error.the-email-no-is-valid"
            is_valid = False

        # --- Check if email already exists ---
        if CustomUser.objects.filter(email=emailUser).exists():
            error_message = 'El correo electronico ya existe' #"home.error.email-already-exists"
            is_valid = False

        if is_valid:
            try:
                # --- Create user ---
                user = CustomUser.objects.create_user(
                    email=emailUser,
                    password=password1,
                    username=form_login['name'],
                    name=form_login['name'],
                    cellphone=form_login['cellphone'],
                    country=form_login['country'],
                    language = form_login['language'] if 'language' in form_login else 'es',
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City',

                    # --- terms and conditions ---
                    terms_accepted=True,
                    terms_version=settings.TERMS_VERSION,
                    terms_accepted_at=timezone.now(),
                    terms_accepted_ip=get_client_ip(request),
                    terms_user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                # --- Create company ---
                company_name = form_login['name_company'] if 'name_company' in form_login else f'Company of {emailUser}'
                company = Company.objects.create(
                    company_name=company_name,
                    name_of_the_person_in_charge=form_login['name'],
                    email_of_the_person_in_charge=form_login['email'],
                    cellphone=form_login['cellphone'],
                    country=form_login['country'],
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City'
                )

                # --- Create branch ---
                branch = Branch.objects.create(
                    company=company,
                    name_branch=company_name,
                    country=form_login['country'],
                    cellphone=form_login['cellphone'],
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City'
                )

                # --- Create default role ---
                role, created = UserRole.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={'description': 'Rol Admin'}
                )

                # --- Assign all permissions that exist in the ERP---
                all_permissions = get_all_the_permissions()
                for app_name, perms_data in all_permissions.items():
                    if isinstance(perms_data, dict) and "permissions" in perms_data:
                        for code in perms_data["permissions"]:
                            permit, created = Permit.objects.get_or_create(code=code, defaults={'app': app_name})
                            Role.objects.get_or_create(role=role, permit=permit, defaults={'active': True})

                #---------departament of the user---------------
                department, created = UserDepartment.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={
                        "description": "",
                        "color": "#007bff",
                        "manager": user,
                        "activated": True,
                    },
                )


                # --- Assign user to company/branch/role ---
                user.company = company
                user.branch = branch
                user.user_role = role
                user.save()

                #---FIRST 1. We will to create the plan of demo for the user---
                #if the database is new, now we will to create the plan of demo
                plan_demo, _ = SubscriptionPlan.objects.get_or_create(
                    code=0, 
                    defaults={'name': 'Free Trial', 'price': 0}
                )

                #now here we will to create the subscription of the user
                UserSubscription.objects.create(
                    user=user,
                    plan=plan_demo,
                    status='Free',

                    #Set the end of the trial to 15 days from now
                    current_period_end=timezone.now() + timedelta(days=15),
                    provider="manual"
                )

                send_welcome_email(user)
                
                # --- Authenticate and log in automatically ---
                authenticated_user = authenticate(request, email=form_login['email'], password=password1)
                if authenticated_user:
                    login(request, authenticated_user)
                    return redirect('/home')


                
                messages_success = '¡Tu cuenta fue creada con éxito!' #"home.message.the-user-was-register-with-success"
                return render(request, 'login.html', {'form_login': form_login, 'success_message': messages_success, 'languages': languages})

            except Exception as e:
                print(e)
                error_message = f"Error: {str(e)}"

    return render(request, 'login.html', {'form_login': form_login, 'error_message': error_message, 'languages': languages})





from django.contrib.auth import authenticate, login
from core.forms import LoginForm

def login_view(request):
    form = LoginForm()
    error_message = None

    #if the user not have a login, now we will get all the language that exist in the system of home
    languages=get_languages_of_the_erp()

    if request.method == 'POST':
        email = request.POST['email'].strip().lower()
        password = request.POST['password']

        try:
            # Authenticate usando USERNAME_FIELD='email'
            user = CustomUser.objects.get(email=email)
            if user is not None:
                if user.check_password(password):
                    try:
                        #here we will get the information of the subscription of the user
                        subscription = user.subscription
                    except:
                        #if the user not have a subscription activate also we will to create one for save in his session
                        plan_free, _ = SubscriptionPlan.objects.get_or_create(code=0, defaults={'name': 'Free'})
                        UserSubscription.objects.create(user=user, plan=plan_free, status='free') 
                    
                    #here we will get the information of the subscription of the user
                    subscription = user.subscription
                    if not subscription.can_add_new_device(): #see if the user can add new device

                        #get we will to get all the drives of the user 
                        current_sessions = UserSession.objects.filter(user=user).order_by('session__expire_date')
                        oldest_session = current_sessions.first() #get the more old and close his session
                        if oldest_session.session:
                                oldest_session.session.delete()

                        oldest_session.delete() #delete the login of the model
                        #error_message = "Has alcanzado el número máximo de dispositivos vinculados" #"home.error.not-can-add-other-drive"
                        #return render(request, 'login.html', {'form': form, 'error_message': error_message, 'languages': languages})
                    
                    if subscription.is_expired():
                        error_message = "Tu suscripción ha finalizado. Por favor, renuévala para seguir disfrutando del servicio." #"home.error.not-can-add-other-drive"
                        return render(request, 'login.html', {'form': form, 'error_message': error_message, 'languages': languages})
                    
                    # 1. SAVE THE SESSION
                    login(request, user)

                    # 2. Vinculate the session with the user
                    # We obtain the current session (login() needs to have already occurred)
                    if not request.session.session_key:
                        request.session.create()

                    #save the session in our model UserSession
                    from django.contrib.sessions.models import Session
                    session_instance = Session.objects.get(session_key=request.session.session_key)
                    UserSession.objects.get_or_create(
                        user=user, 
                        session=session_instance,
                        defaults={'device_name': request.META.get('HTTP_USER_AGENT', 'Unknown')}
                    )

                    #when the user is login, now we will to redirect to home
                    return redirect('home')
                else:
                    error_message = 'La contraseña es incorrecta' #'home.error.no-can-login'
            else:
                # if the user not exist or the password is denied
                error_message = 'No existe este usuario'#'home.error.no-can-login'
        except Exception as e:
            print(e)
            error_message = 'No se pudo iniciar sesión. Inténtalo otra vez.' #'home.error.no-can-login'


    data = request.POST  # QueryDict
    # --- Convertimos a diccionario plano ---
    login_form = {k: v[0] for k, v in data.lists()}
    return render(request, 'login.html', {'login_form': login_form, 'error_message': error_message, 'languages': languages})



from django.contrib.auth import logout
from django.contrib.sessions.models import Session
def logout_view(request):
    if request.user.is_authenticated:
        session_key = request.session.session_key

        if session_key:
            # Eliminar el registro del dispositivo
            UserSession.objects.filter(
                user=request.user,
                session__session_key=session_key
            ).delete()

            # Eliminar la sesión de Django (opcional, pero limpio)
            Session.objects.filter(session_key=session_key).delete()

    logout(request)
    return redirect('login')


#----------------------------------------------------------------AD------------------------------------------------------
#In this view we will to create the views of ad of the company or also the web for show like is PLUS ERP 

def view_ad(request):
    return render(request, 'web_ad/index.html') 


def terms_and_conditions(request):
    context={'version': settings.TERMS_VERSION}
    return render(request, 'terms_and_conditions.html', context) 