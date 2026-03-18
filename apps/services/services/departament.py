from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.services.models import ProductDepartment
from django.core.paginator import Paginator
from ..plus_wrapper import Plus

class Departaments:
    @classmethod
    def add(cls, user, data):
        try:
            # 1. get the information of the form
            name = data.get("name", "").strip()
            description = data.get("description", "")
            activated = data.get("activated", True)

            # 2. here we will to see the valid of the bussiness
            if not name:
                return {
                    "success": False,
                    "message": "services.message.department-name-required",
                    "error": "Department name is required"
                }
            
            # 3. get the company of the user
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "services.message.user-without-company",
                    "error": "User has no company assigned"
                }

            # Avoid duplicates per company
            exists = ProductDepartment.objects.filter(
                company=company,
                name__iexact=name,
                activated=True
            ).exists()

            if exists:
                return {
                    "success": False,
                    "message": "message.department-already-exists",
                    "error": "Department already exists for this company"
                }

            # 4. create the departament
            department = ProductDepartment.objects.create(
                company=company,
                name=name,
                description=description,
                activated=activated
            )

            return {
                "success": True,
                "message": "services.message.department-created",
                "error": "",
                "data": {
                    "id": department.id,
                    "name": department.name,
                    "activated": department.activated
                }
            }

        except ValidationError as e:
            return {
                "success": False,
                "message": "message.validation-error",
                "error": str(e)
            }

        except IntegrityError:
            return {
                "success": False,
                "message": "message.database-error",
                "error": "Integrity error"
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
            # 3. get the company of the user
            company = getattr(user, 'company', None)
            department_id = data.get("id")

            # 2. do validations
            if not department_id:
                return {
                    "success": False,
                    "message": "services.message.department-id-required",
                    "error": "Department id is required"
                }
            
            if not company:
                return {
                    "success": False,
                    "message": "services.message.user-without-company",
                    "error": "User has no company assigned"
                }
            
            # 4. Find an apartment (multi-company insurance)
            try:
                department = ProductDepartment.objects.get(
                    id=department_id,
                    company=company
                )
            except ProductDepartment.DoesNotExist:
                return {
                    "success": False,
                    "message": "services.message.department-not-found",
                    "error": "Department not found or does not belong to this company"
                }
            

            # 1. get the data of the form
            name = data.get("name", department.name)
            description = data.get("description", department.description)
            activated = Plus.to_bool(data.get("activated", True))
            
            if not name:
                return {
                    "success": False,
                    "message": "services.message.department-name-required",
                    "error": "Department name is required"
                }

            # Avoid duplicates (excluding the current one)
            exists = ProductDepartment.objects.filter(
                company=company,
                name__iexact=name,
                activated=True
            ).exclude(id=department_id).exists()

            if exists: #if already exist a departament with name, show a message of error
                return {
                    "success": False,
                    "message": "services.message.department-already-exists",
                    "error": "Another department with this name already exists"
                }

            # 5. update
            department.name = name
            department.description = description
            department.activated = activated
            department.save()

            return {
                "success": True,
                "message": "services.success.the-departament-was-update",
                "error": "",
                "data": {
                    "id": department.id,
                    "name": department.name,
                    "activated": department.activated
                }
            }

        except ValidationError as e:
            return {
                "success": False,
                "message": "message.validation-error",
                "error": str(e)
            }

        except IntegrityError:
            return {
                "success": False,
                "message": "message.database-error",
                "error": "Integrity error"
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
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
            queryset = ProductDepartment.objects.filter(
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
            for department in page_obj:
                results.append({
                    "id": department.id,
                    "name": department.name,
                    "description": department.description
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
    def get_information_by_id(cls, user, departament_id):
        try:
            company = user.company
            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # Query base (multi company + activated)
            # -------------------------
            departament = ProductDepartment.objects.filter(
                id=departament_id,
                company=company
            ).values().first()

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer":departament,
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }