from core.models import Branch, BranchSchedule
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import time
from datetime import datetime

def get_branch_schedule_all(branch):
    """
    Devuelve un diccionario plano con los horarios de toda la semana de la sucursal.
    Cada día tiene keys: <day>_open, <day>_close, <day>_closed
    """
    if not branch:
        return {}

    DAYS_MAP = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }

    flat_schedule = {}

    for day_index, day_key in DAYS_MAP.items():
        schedule = BranchSchedule.objects.filter(branch=branch, day_of_week=day_index).first()

        if schedule:
            flat_schedule[f"{day_key}_open"] = schedule.open_time.strftime("%H:%M") if schedule.open_time else ""
            flat_schedule[f"{day_key}_close"] = schedule.close_time.strftime("%H:%M") if schedule.close_time else ""
            flat_schedule[f"{day_key}_closed"] = schedule.is_closed
        else:
            flat_schedule[f"{day_key}_open"] = ""
            flat_schedule[f"{day_key}_close"] = ""
            flat_schedule[f"{day_key}_closed"] = False

    return flat_schedule

def save_branch_schedule(branch, data) -> dict:
    """
    Crea o actualiza los horarios de una sucursal.
    Si no existe un día, se crea automáticamente.
    data proviene del formulario en formato JSON o POST.
    """
    result = {"success": False, "message": "", "answer": None}

    if not branch:
        result["message"] = "No se proporcionó una sucursal válida."
        return result

    try:
        DAYS_MAP = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        updated_days = []

        for day_name, day_index in DAYS_MAP.items():
            open_key = f"{day_name}_open"
            close_key = f"{day_name}_close"
            closed_key = f"{day_name}_closed"

            open_time = data.get(open_key)
            close_time = data.get(close_key)

            # ✅ Detectar correctamente si está cerrado
            is_closed = data.get(closed_key) in ["on", "true", True, "1", 1]

            # Convertir hora string a objeto time
            if open_time:
                h, m = open_time.split(":")
                open_time = time(int(h), int(m))
            else:
                open_time = None

            if close_time:
                h, m = close_time.split(":")
                close_time = time(int(h), int(m))
            else:
                close_time = None

            schedule, created = BranchSchedule.objects.get_or_create(
                branch=branch,
                day_of_week=day_index,
                defaults={
                    "open_time": open_time,
                    "close_time": close_time,
                    "is_closed": is_closed,
                }
            )

            if not created:
                schedule.open_time = open_time
                schedule.close_time = close_time
                schedule.is_closed = is_closed
                schedule.save()

            updated_days.append({
                "day": day_name,
                "created": created,
                "is_closed": is_closed,
                "open_time": open_time.strftime("%H:%M") if open_time else "",
                "close_time": close_time.strftime("%H:%M") if close_time else "",
            })

        result["success"] = True
        result["message"] = "Horarios actualizados correctamente."
        result["answer"] = updated_days

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        result["message"] = f"Error al guardar los horarios: {str(e)}"

    return result