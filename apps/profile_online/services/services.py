from apps.profile_online.models import PublicProfile, ProfileService, ProfileSchedule, ProfileLocation, ProfileReview
from django.db.models import Prefetch
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from django.forms.models import model_to_dict
from ..plus_wrapper import Plus

def add_services(user,data):
    try:
        #first we will see if exist a PublicProfile of this user
        profile = PublicProfile.objects.filter(user=user).first()
        created = False

        #if not exist the profile online, we will to create 
        if not profile:
            profile = PublicProfile(user=user)
            profile.save()
            created = True


        #now we will to add the information of the new service 
        #first we will see if have all the information need 
        name=data.get('name', '')
        price=data.get('price', '')
        currency=data.get('currency', 'mxn')
        is_active=Plus.to_bool(data.get('is_active',False))
        order=int(data.get('order', 0))

        if name.isspace():
            return {
                "success": False,
                "message": "Necesitas agregar el nombre del servicio",
            }
        
        if price.isspace():
            return {
                "success": False,
                "message": "profile_online.error.need-add-the-price-of-the-services",
            }
        
        #if all the data that send the form be success now we will to create the service 
        services=ProfileService(profile=profile, name=name, price=price, currency=currency, is_active=is_active, order=order)
        services.save()

        return {
            "success": True,
            "message": "profile_online.success.service-online-add",
            "answer":services.id
        }
    
    except IntegrityError:
        return {
            "success": False,
            "message": "profile.error.integrity",
        }

    except Exception as e:
        return {
            "success": False,
            "message": "profile.error.unexpected",
            "error": str(e),
        }