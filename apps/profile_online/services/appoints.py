from apps.profile_online.models import PublicProfile, ScheduleOnline
from ..plus_wrapper import Plus
from django.db import IntegrityError
from datetime import datetime, time

def get_online_schedules_of_profile(user):
    """
    Get online schedules of the doctor's profile
    """

    try:
        profile = (
            PublicProfile.objects
            .prefetch_related("schedules_online")
            .get(user=user)
        )

    except PublicProfile.DoesNotExist:
        return {
            "success": False,
            "message": "profile_online.error.not-exist-schedules",
            "error": "This profile was not found"
        }

    # ===============================
    # ONLINE SCHEDULES
    # ===============================
    schedules = [
        {
            "id": schedule.id,
            "day_of_week": schedule.day_of_week,
            "day_name": schedule.get_day_of_week_display(),
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "slot_duration": schedule.slot_duration,
            "is_active": schedule.is_active,
        }
        for schedule in profile.schedules_online
        .filter(is_active=True)
        .order_by("day_of_week", "start_time")
    ]

    return {
        "success": True,
        "answer": schedules
    }


    
def create_schedule_online(user, data):
    """
    Create or update an online schedule for the user's profile
    """

    try:
        # ===============================
        # 1. Obtener perfil
        # ===============================
        profile = PublicProfile.objects.filter(user=user).first()
        if not profile:
            return {
                "success": False,
                "message": "profile_online.error.profile-not-found",
                "error": "Profile not found"
            }

        # ===============================
        # 2. Obtener datos del formulario
        # ===============================
        day_of_week = data.get("day_of_week")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        is_active = Plus.to_bool(data.get("is_active", True))

        # ===============================
        # 3. Validaciones básicas
        # ===============================
        if day_of_week is None:
            return {
                "success": False,
                "message": "profile_online.error.day-required",
            }

        if not start_time or not end_time:
            return {
                "success": False,
                "message": "profile_online.error.time-required",
            }

        # convertir string → time
        start_time_obj = time.fromisoformat(start_time)
        end_time_obj = time.fromisoformat(end_time)

        if start_time_obj >= end_time_obj:
            return {
                "success": False,
                "message": "profile_online.error.invalid-time-range",
            }
        
        # convertir a datetime para poder restar
        start_dt = datetime.combine(datetime.today(), start_time_obj)
        end_dt = datetime.combine(datetime.today(), end_time_obj)
        # duración total en minutos
        slot_duration = int((end_dt - start_dt).total_seconds() / 60)


        # ===============================
        # 4. Crear o actualizar horario
        # ===============================
        schedule = ScheduleOnline.objects.create(
            profile=profile,
            day_of_week=int(day_of_week),
            start_time=start_time_obj,
            end_time=end_time_obj,
            slot_duration=int(slot_duration),
            is_active=is_active,
        )
        created = True

        return {
            "success": True,
            "message": "profile_online.success.schedule-saved",
            "answer": {
                "id": schedule.id,
                "created": created,
                "day_name": schedule.get_day_of_week_display(),
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "slot_duration": schedule.slot_duration,
                "is_active": schedule.is_active,
            }
        }

    except IntegrityError:
        return {
            "success": False,
            "message": "profile_online.error.integrity",
            "error": "Duplicate schedule or invalid data"
        }

    except Exception as e:
        return {
            "success": False,
            "message": "profile_online.error.unexpected",
            "error": str(e),
        }
    
def update_schedule_online(user,data,id_schedule):
    """
    Update an existing online schedule for the user's profile
    """
    try:
        # ===============================
        # 1. Obtener perfil
        # ===============================
        profile = PublicProfile.objects.filter(user=user).first()
        if not profile:
            return {
                "success": False,
                "message": "profile_online.error.profile-not-found",
                "error": "Profile not found"
            }

        # ===============================
        # 2. Obtener el horario a actualizar
        # ===============================
        try:
            schedule = ScheduleOnline.objects.get(id=id_schedule, profile=profile)
        except ScheduleOnline.DoesNotExist:
            return {
                "success": False,
                "message": "profile_online.error.schedule-not-found",
                "error": "Schedule not found"
            }

        # ===============================
        # 3. Obtener datos del formulario
        # ===============================
        day_of_week = data.get("day_of_week")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        is_active = Plus.to_bool(data.get("is_active", True))

        # ===============================
        # 4. Validaciones básicas
        # ===============================
        if day_of_week is None:
            return {
                "success": False,
                "message": "profile_online.error.day-required",
            }

        if not start_time or not end_time:
            return {
                "success": False,
                "message": "profile_online.error.time-required",
            }

        # convertir string → time
        start_time_obj = time.fromisoformat(start_time)
        end_time_obj = time.fromisoformat(end_time)

        if start_time_obj >= end_time_obj:
            return {
                "success": False,
                "message": "profile_online.error.invalid-time-range",
            }

        # calcular duración en minutos
        start_dt = datetime.combine(datetime.today(), start_time_obj)
        end_dt = datetime.combine(datetime.today(), end_time_obj)
        slot_duration = int((end_dt - start_dt).total_seconds() / 60)

        # ===============================
        # 5. Actualizar campos
        # ===============================
        schedule.day_of_week = int(day_of_week)
        schedule.start_time = start_time_obj
        schedule.end_time = end_time_obj
        schedule.slot_duration = slot_duration
        schedule.is_active = is_active
        schedule.save()

        return {
            "success": True,
            "message": "profile_online.success.schedule-updated",
            "answer": {
                "id": schedule.id,
                "day_name": schedule.get_day_of_week_display(),
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "slot_duration": schedule.slot_duration,
                "is_active": schedule.is_active,
            }
        }

    except IntegrityError:
        return {
            "success": False,
            "message": "profile_online.error.integrity",
            "error": "Duplicate schedule or invalid data"
        }

    except Exception as e:
        return {
            "success": False,
            "message": "profile_online.error.unexpected",
            "error": str(e),
        }