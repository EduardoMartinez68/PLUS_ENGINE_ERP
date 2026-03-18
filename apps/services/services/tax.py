from decimal import Decimal
from apps.services.models import Tax
from django.http import JsonResponse
from decimal import Decimal
from ..plus_wrapper import Plus
from django.core.paginator import Paginator

class TaxService:
    @classmethod
    def add(cls, user, data):
        try:
            company = getattr(user, 'company', None)
            

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # data
            # -------------------------
            name = data.get("name", "")
            rate = data.get("rate")
            description = data.get("description", "")

            if not name:
                return {
                    "success": False,
                    "message": "message.tax-name-required",
                    "error": "Tax name is required"
                }

            try:
                rate = Decimal(str(rate))
            except:
                return {
                    "success": False,
                    "message": "message.tax-rate-invalid",
                    "error": "Invalid rate"
                }

            if rate < 0 or rate > 100:
                return {
                    "success": False,
                    "message": "message.tax-rate-range",
                    "error": "Rate must be between 0 and 100"
                }

            # -------------------------
            # Evitar duplicados activos
            # -------------------------
            exists = Tax.objects.filter(
                company=company,
                name__iexact=name,
                activated=True
            ).exists()

            if exists:
                return {
                    "success": False,
                    "message": "message.tax-already-exists",
                    "error": "Tax already exists for this branch/company"
                }

            # -------------------------
            # Crear impuesto
            # -------------------------
            tax = Tax.objects.create(
                company=company,
                name=name,
                rate=rate,
                description=description,
                activated=True
            )

            return {
                "success": True,
                "message": "message.tax-created",
                "error": "",
                "data": {
                    "id": tax.id,
                    "name": tax.name,
                    "rate": float(tax.rate),
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": e,
                "error": ""
            }
        

    @classmethod
    def search(cls, user, key=None, page=1):
        try:
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # Query base (multi company + activated)
            # -------------------------
            queryset = Tax.objects.filter(
                company=company,
                activated=True
            )

            # -------------------------
            # filter by query
            # -------------------------
            if key:
                key = key.strip()
                queryset = queryset.filter(
                    name__icontains=key
                )

            # -------------------------
            # Alphabetic order
            # -------------------------
            queryset = queryset.order_by("name")

            # -------------------------
            # paginator  (20 by pag)
            # -------------------------
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(page)

            # -------------------------
            # Format results
            # -------------------------
            results = []
            for tax in page_obj:
                results.append({
                    "id": tax.id,
                    "name": f'{tax.name} {tax.rate}%',
                    "description": tax.description
                })

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer":results,
                "data": {
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_records": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }
    
    @classmethod
    def update(cls, user, data):
        try:
            tax_id = data.get("id", '')
            name = data.get("name")
            rate = data.get("rate")
            description = data.get("description")
            activated = Plus.to_bool(data.get("activated", True))

            company = user.company

            # Buscar el impuesto que pertenezca a la company
            try:
                tax = Tax.objects.get(id=tax_id, company=company)
            except Tax.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "Impuesto no encontrado o no pertenece a la empresa"
                }, status=404)


            # Actualizar campos si vienen en el formulario
            if name:
                tax.name = name

            if rate:
                try:
                    tax.rate = Decimal(rate)
                except:
                    return JsonResponse({
                        "success": False,
                        "message": "El porcentaje debe ser un número válido"
                    }, status=400)

            if description is not None:
                tax.description = description

            if activated is not None:
                tax.activated = activated

            tax.save()

            return {
                "success": True,
                "message": "",
                "error": ""
            }

        except Exception as e:
            return {
                "success": False,
                "message": "Error",
                "error": str(e) 
            }
        
    @classmethod
    def get_tax(cls, user, tax_id):
        try:
            company = user.company

            # Buscar el impuesto que pertenezca a la empresa
            try:
                tax = Tax.objects.get(id=tax_id, company=company)
            except Tax.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "Impuesto no encontrado o no pertenece a la empresa"
                }, status=404)
            
            # Respuesta con la información
            data = {
                "id": tax.id,
                "name": tax.name,
                "rate": float(tax.rate),
                "description": tax.description,
                "activated": tax.activated,
                "creation_date": tax.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                "last_update": tax.last_update.strftime("%Y-%m-%d %H:%M:%S"),
            }

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer": data
            }

        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e)
            }