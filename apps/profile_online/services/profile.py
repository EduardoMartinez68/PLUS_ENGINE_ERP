from apps.profile_online.models import PublicProfile, ProfileService, ProfileSchedule, ProfileLocation, ProfileReview
from django.db.models import Prefetch
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from django.forms.models import model_to_dict
from ..plus_wrapper import Plus

def get_information_of_the_profile(user):
    """
    Get all the information of the profile online of the user
    """

    try:
        profile = (
            PublicProfile.objects
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "services",
                    queryset=ProfileService.objects.order_by("order")
                ),
                "schedules",
                "locations",
                Prefetch(
                    "reviews",
                    queryset=ProfileReview.objects.filter(is_approved=True)
                )
            )
            .get(user=user)
        )

    except PublicProfile.DoesNotExist:
        return {
            "success": False,
            "message": "profile_online.error.not-exit-information",
            "error":"This profile not was found"
        }

    # ===============================
    # BASE PROFILE INFO
    # ===============================
    data = {
        "success": True,
        "answer":{
            "profile": {
                "id": profile.id,
                "public_slug": profile.public_slug,
                "is_public": profile.is_public,
                "is_verified": profile.is_verified,

                "title": profile.title,
                "specialty": profile.specialty,
                "university": profile.university,
                "about": profile.about,
                "whatsapp": profile.whatsapp,
                "phone": profile.phone,

                "cover_image": profile.cover_image.url if profile.cover_image else None,
                "profile_image": profile.profile_image.url if profile.profile_image else None,

                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            },

            # ===============================
            # SERVICES
            # ===============================
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "price": float(service.price),
                    "currency": service.currency,
                    "is_active": service.is_active,
                    "order": service.order,
                }
                for service in profile.services.all()
            ],

            # ===============================
            # SCHEDULES
            # ===============================
            "schedules": [
                {
                    "id": schedule.id,
                    "day_of_week": schedule.day_of_week,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                    "note": schedule.note,
                }
                for schedule in profile.schedules.all()
            ],

            # ===============================
            # LOCATIONS
            # ===============================
            "locations": [
                {
                    "id": location.id,
                    "address": location.address,
                    "latitude": float(location.latitude) if location.latitude else None,
                    "longitude": float(location.longitude) if location.longitude else None,
                    "google_maps_url": location.google_maps_url,
                    "is_main": location.is_main,
                }
                for location in profile.locations.all()
            ],

            # ===============================
            # REVIEWS
            # ===============================
            "reviews": [
                {
                    "id": review.id,
                    "author_name": review.author_name,
                    "rating": review.rating,
                    "comment": review.comment,
                    "created_at": review.created_at,
                }
                for review in profile.reviews.all()
            ]
            
        },
    }

    return data



import re
def normalize_whatsapp(number: str, default_country="52"):
    """
    Normalize a number for WhatsApp (E.164 without +)
    """
    if not number:
        return None

    #Remove everything that is not a number
    digits = re.sub(r"\D", "", number)
    return digits
    # If it starts with 52 and has a valid length, we'll leave it.
    if digits.startswith(default_country):
        return digits

    # If it is a local Mexican number (10 digits), add country
    if len(digits) == 10:
        return f"{default_country}{digits}"

    # Si no cumple, se considera inválido
    return None

def update_profile_online(user, data):
    """
    Create or update the profile online of the user.
    """

    try:
        profile = PublicProfile.objects.filter(user=user).first()
        created = False

        if not profile:
            profile = PublicProfile(user=user)
            created = True

        update_fields = []

        # -------------------------------
        # Public slug
        # -------------------------------
        raw_slug = data.get("public_slug")
        if raw_slug is not None:
            slug = slugify(raw_slug)

            if not slug:
                return {
                    "success": False,
                    "message": "profile.error.invalid_slug",
                }

            if (
                PublicProfile.objects
                .filter(public_slug=slug)
                .exclude(pk=profile.pk)
                .exists()
            ):
                return {
                    "success": False,
                    "message": "profile.error.slug_already_exists",
                }

            profile.public_slug = slug
            update_fields.append("public_slug")

        # -------------------------------
        # Visibility
        # -------------------------------
        profile.is_public = Plus.to_bool(data.get("is_public", False))
        update_fields.append("is_public")

        # -------------------------------
        # Text fields
        # -------------------------------
        text_fields = [
            "title",
            "specialty",
            "university",
            "whatsapp",
            "phone",
            "about",
        ]

        for field in text_fields:
            if field in data:
                setattr(profile, field, data.get(field))
                update_fields.append(field)

        # -------------------------------
        # Whatsapp normalization
        # -------------------------------
        if "whatsapp" in data:
            normalized_whatsapp = normalize_whatsapp(data.get("whatsapp"))
            profile.whatsapp = normalized_whatsapp
            update_fields.append("whatsapp")

        # -------------------------------
        # Images
        # -------------------------------
        if data.get("cover_image"):
            profile.cover_image = data["cover_image"]
            update_fields.append("cover_image")

        if data.get("profile_image"):
            profile.profile_image = data["profile_image"]
            update_fields.append("profile_image")

        # -------------------------------
        # Save
        # -------------------------------
        if not update_fields and not created:
            return {
                "success": True,
                "message": "profile_online.success.information-of-the-profle-update",
            }

        with transaction.atomic():
            if created:
                profile.save()
            else:
                profile.save(update_fields=update_fields)

        return {
            "success": True,
            "message": "profile_online.success.information-of-the-profle-update",
            "created": created,
            "answer": profile.id,
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
    
from datetime import datetime, timedelta
from apps.profile_online.models import PublicProfile,ProfileService
from datetime import datetime, time
def get_available_slots(profile, start_date, end_date):
    
    available_slots = []

    schedules = profile.schedules_online.filter(is_active=True)
    if not schedules.exists():
        return []

    exceptions = profile.schedule_exceptions.filter(date__gte=start_date, date__lte=end_date)
    appointments = profile.online_appointment.filter(date__gte=start_date, date__lte=end_date, status__in=['pending','confirmed'])

    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        day_schedules = schedules.filter(day_of_week=day_of_week)

        for schedule in day_schedules:
            slot_start = datetime.combine(current_date, schedule.start_time)
            slot_end = datetime.combine(current_date, schedule.end_time)
            delta = timedelta(minutes=schedule.slot_duration)

            while slot_start + delta <= slot_end:
                slot_start_time = slot_start.time()
                slot_end_time = (slot_start + delta).time()

                conflict = False

                # verificar excepciones
                for exc in exceptions.filter(date=current_date):
                    exc_start = exc.start_time or time(0,0)
                    exc_end = exc.end_time or time(23,59)
                    if exc_start < slot_end_time and exc_end > slot_start_time:
                        conflict = True
                        break
                if conflict:
                    slot_start += delta
                    continue

                # verificar citas existentes
                for app in appointments.filter(date=current_date):
                    if app.start_time < slot_end_time and app.end_time > slot_start_time:
                        conflict = True
                        break
                if conflict:
                    slot_start += delta
                    continue

                # slot disponible
                available_slots.append({
                    "date": current_date,
                    "start_time": slot_start_time,
                    "end_time": slot_end_time
                })

                slot_start += delta

        current_date += timedelta(days=1)

    return available_slots