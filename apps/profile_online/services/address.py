from django.db import IntegrityError
from apps.profile_online.models import PublicProfile, ProfileLocation

def save_profile_location(user, data):
    try:
        # 1. Obtener o crear perfil
        profile = PublicProfile.objects.filter(user=user).first()
        if not profile:
            profile = PublicProfile.objects.create(user=user)

        # 2. Obtener datos
        address = data.get("address", "").strip()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        google_maps_url = data.get("google_maps_url")
        is_main = bool(data.get("is_main", True))

        # 3. Validación básica
        if not address:
            return {
                "success": False,
                "message": "profile_online.error.need-add-address",
            }

        # 4. Si será principal, desactivar las demás
        if is_main:
            ProfileLocation.objects.filter(
                profile=profile,
                is_main=True
            ).update(is_main=False)

        # 5. Obtener ubicación existente (principal)
        location = ProfileLocation.objects.filter(
            profile=profile,
            is_main=True
        ).first()

        # 6. Crear o actualizar
        if location:
            location.address = address
            location.latitude = latitude or None
            location.longitude = longitude or None
            location.google_maps_url = google_maps_url or None
            location.is_main = is_main
            location.save()
        else:
            location = ProfileLocation.objects.create(
                profile=profile,
                address=address,
                latitude=latitude or None,
                longitude=longitude or None,
                google_maps_url=google_maps_url or None,
                is_main=is_main
            )

        return {
            "success": True,
            "message": "profile_online.success.location-saved",
            "answer": location.id
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