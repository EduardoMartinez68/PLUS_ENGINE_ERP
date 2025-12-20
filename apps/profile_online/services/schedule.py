from apps.profile_online.models import PublicProfile, ProfileSchedule
from django.db import IntegrityError
from ..plus_wrapper import Plus
from datetime import time
from django.db import IntegrityError

def update_profile_schedule(user, data):
    try:
        # 1. Obtener o crear perfil
        profile = PublicProfile.objects.filter(user=user).first()
        if not profile:
            profile = PublicProfile.objects.create(user=user)

        DAYS_MAP = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5,
            "saturday": 6,
            "sunday": 7,
        }

        updated_days = []

        for day_key, day_number in DAYS_MAP.items():
            open_key = f"{day_key}_open"
            close_key = f"{day_key}_close"

            open_time = data.get(open_key)
            close_time = data.get(close_key)

            if not open_time or not close_time:
                continue

            # convertir string → time
            open_time_obj = time.fromisoformat(open_time)
            close_time_obj = time.fromisoformat(close_time)

            # 2. Día cerrado → eliminar si existe
            if open_time_obj == time(0, 0) and close_time_obj == time(0, 0):
                ProfileSchedule.objects.filter(
                    profile=profile,
                    day_of_week=day_number
                ).delete()
                continue

            # 3. Crear o actualizar
            schedule, created = ProfileSchedule.objects.update_or_create(
                profile=profile,
                day_of_week=day_number,
                defaults={
                    "start_time": open_time_obj,
                    "end_time": close_time_obj,
                }
            )

            updated_days.append(day_number)

        return {
            "success": True,
            "message": "profile_online.success.schedule-updated",
            "answer": updated_days
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