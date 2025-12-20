from apps.profile_online.models import PublicProfile, ProfileService
from django.db import  IntegrityError
from ..plus_wrapper import Plus

def add_services(user,data):
    try:
        #first we will see if exist a PublicProfile of this user
        profile = PublicProfile.objects.filter(user=user).first()

        #if not exist the profile online, we will to create 
        if not profile:
            profile = PublicProfile(user=user)
            profile.save()

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
                "message": "profile_online.error.need-add-the-name-of-the-services",
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
    

def update_services(user, service_id, data):
    try:
        # get the profile online of user
        profile = PublicProfile.objects.filter(user=user).first()

        if not profile:
            return {
                "success": False,
                "message": "profile_online.error.profile-not-exist",
            }

        # see if the service is of the user
        service = ProfileService.objects.filter(
            id=service_id,
            profile=profile
        ).first()

        if not service:
            return {
                "success": False,
                "message": "profile_online.error.service-not-found",
            }

        # get the data of the form
        name = data.get('name')
        price = data.get('price')
        currency = data.get('currency','mxn')
        is_active = Plus.to_bool(data.get('is_active',False))
        order = data.get('order')

        #valid the form
        if name is not None:
            if not name or name.isspace():
                return {
                    "success": False,
                    "message": "profile_online.error.need-add-the-name-of-the-services",
                }
            service.name = name

        if price is not None:
            if not str(price).strip():
                return {
                    "success": False,
                    "message": "profile_online.error.need-add-the-price-of-the-services",
                }
            service.price = price


        service.currency = currency
        service.is_active = Plus.to_bool(is_active)

        if order is not None:
            try:
                service.order = int(order)
            except ValueError:
                service.order = 0

        #save the change of the service
        service.save()

        return {
            "success": True,
            "message": "profile_online.success.service-online-update",
            "answer": service.id
        }

    except IntegrityError:
        return {
            "success": False,
            "message": "profile.error.integrity",
        }

    except Exception as e:
        return {
            "success": False,
            "message": "profile.error.integrity",
            "error": str(e),
        }