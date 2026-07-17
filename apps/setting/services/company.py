import os

from core.models import CustomUser, Company, Branch
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import base64
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

def update_company(user, data) -> dict:
    result = {"success": False, "message": "", "company": None}

    company = getattr(user, "company", None)
    if not company:
        result["message"] = "El usuario no tiene una compañía asociada."
        return result

    # 🔹 PROCESAR LOGO
    logo_data = data.get("logo")
    if logo_data and isinstance(logo_data, str) and "," in logo_data:
        try:
            # 🔥 Guardar referencia del logo anterior
            old_logo = company.logo.path if company.logo else None

            fmt, imgstr = logo_data.split(",", 1)
            img_data = base64.b64decode(imgstr)

            img = Image.open(BytesIO(img_data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Redimensionar
            max_size = (500, 500)
            img.thumbnail(max_size, Image.LANCZOS)

            # Convertir a WEBP
            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=85)
            buffer.seek(0)

            unique_filename = f"{uuid.uuid4().hex}_logo.webp"

            # 🔥 Guardar nuevo logo
            company.logo.save(unique_filename, ContentFile(buffer.read()), save=False)

            # 🔥 Eliminar logo anterior (si existe)
            if os.path.exists(old_logo):
                try:
                    os.remove(old_logo)
                except PermissionError:
                    pass

        except Exception as e:
            print("Error processing logo:", e)

    try:
        # 🔹 Actualizar otros campos
        for field, value in data.items():
            if field == "logo":
                continue
            if hasattr(company, field):
                setattr(company, field, value)

        company.updated_by = user.email or user.username
        company.save()

        result.update({
            "success": True,
            "message": "Compañía actualizada correctamente.",
            "company": company
        })

    except ValidationError as e:
        result["message"] = f"error in: {e.messages}"
    except Exception as e:
        result["message"] = f"error when try update the company: {str(e)}"

    return result