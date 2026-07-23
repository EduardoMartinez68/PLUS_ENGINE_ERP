
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from core.models import Branch
from core.Plus import Plus
from apps.services.models import Pack, Inventory, HistoryInventory
from django.core.paginator import Paginator
from django.db.models import Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.db import models
from django.core.exceptions import ValidationError

class InventoryService:
    @classmethod
    def search_with_inventory(cls, user, key=None, page=1, status=None, activated=True, amountOfData=20, show_for_sale=None):
        try:
            company = getattr(user, 'company', None)
            branch = getattr(user, 'branch', None)

            if not company or not branch:
                return {
                    "success": False,
                    "message": "message.user-without-company-or-branch",
                    "error": "User must have a company and branch assigned"
                }

            # -------------------------
            # 1. Query base con Anotaciones de Inventario
            # -------------------------
            # Usamos Coalesce para que si no existe registro de inventario, el valor sea 0
            queryset = Pack.objects.filter(
                company=company,
                activated=activated,
                track_inventory=True
            ).annotate(
                current_stock=Coalesce(
                    models.Subquery(
                        Inventory.objects.filter(pack=models.OuterRef('pk'), branch=branch).values('stock')[:1]
                    ), 0, output_field=DecimalField()
                ),
                minimum_stock=Coalesce(
                    models.Subquery(
                        Inventory.objects.filter(pack=models.OuterRef('pk'), branch=branch).values('min_stock')[:1]
                    ), 0, output_field=DecimalField()
                )
            ).select_related("department", "category").prefetch_related("taxes__tax", "branch_prices")

            # -------------------------
            # 2. Filtro por Status (Inventario)
            # -------------------------
            # status 1: Por terminarse (stock <= min_stock)
            # status 2: Suficiente (stock > min_stock)
            if status == 1:
                queryset = queryset.filter(current_stock__lte=F('minimum_stock'))
            elif status == 2:
                queryset = queryset.filter(current_stock__gt=F('minimum_stock'))
  
            # -------------------------
            # 3. Filtros de búsqueda y visibilidad
            # -------------------------
            if show_for_sale is not None:
                queryset = queryset.filter(show_fo_sale=show_for_sale)

            if key:
                key = key.strip()
                queryset = queryset.filter(
                    Q(name__icontains=key) | Q(skus__icontains=key)
                )

            # -------------------------
            # 4. Orden y Paginación
            # -------------------------
            queryset = queryset.order_by("name")
            paginator = Paginator(queryset, amountOfData)
            page_obj = paginator.get_page(page)

            # -------------------------
            # 5. Formatear resultados
            # -------------------------
            results = []
            for pack in page_obj:
                minimum_stock=float(pack.minimum_stock)
                current_stock=float(pack.current_stock)
                missing=current_stock-minimum_stock

                #now we will see the status of the inventory use <missing> and <minimum_stock> 
                if missing>0:
                    if current_stock>(minimum_stock+((minimum_stock+1)/3)):
                        status_inventory='stock-available'
                    else:
                        status_inventory='safety-stock'
                else:
                    status_inventory='low-stock'

                results.append({
                    "id": pack.id,
                    "img": '/static/img/info/supplies.webp',
                    "name": pack.name,
                    "description": pack.description,
                    "pack_type": pack.pack_type,
                    "department": pack.department.name if pack.department and pack.department.activated else '',
                    "category": pack.category.name if pack.category and pack.category.activated else '',
                    "skus": pack.skus,
                    "stock": current_stock,
                    "min_stock": minimum_stock,
                    "missing":missing,
                    "status_inventory":status_inventory,
                    "unity_type":pack.unity_type
                })

            return {
                "success": True,
                "message": "",
                "answer": results,
                "pagination": {
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_records": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }

        except Exception as e:
            return {"success": False, "message": "message.unexpected-error", "error": str(e)}
        

    @classmethod
    def get_information_by_id(cls, user, pack_id):
        try:
            # -------------------------
            # 1. Validate pack_id
            # -------------------------
            if not pack_id:
                return {
                    "success": False,
                    "message": "message.pack-id-required",
                    "error": "Pack id is required"
                }

            # -------------------------
            # 2. Validate company
            # -------------------------
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # 3. Validate branch
            # -------------------------
            branch = getattr(user, 'branch', None)

            if not branch:
                return {
                    "success": False,
                    "message": "message.user-without-branch",
                    "error": "User has no branch"
                }

            # -------------------------
            # 4. Get pack
            # -------------------------
            try:
                pack = Pack.objects.get(
                    id=pack_id,
                    company=company
                )

            except Pack.DoesNotExist:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }

            # -------------------------
            # 5. Get inventory
            # -------------------------
            inventory = Inventory.objects.filter(
                company=company,
                branch=branch,
                pack=pack
            ).first()

            stock = inventory.stock if inventory else 0
            min_stock = inventory.min_stock if inventory else 0

            # -------------------------
            # 6. Build response
            # -------------------------
            data = {
                "id": pack.id,
                "name": pack.name,
                "sku": pack.skus[0] if pack.skus else None,
                "skus": pack.skus or [],
                "min_stock": float(min_stock),
                "stock": float(stock)
            }

            return {
                "success": True,
                "message": "message.pack-found",
                "error": "",
                "answer": data
            }

        except ValidationError as e:
            return {
                "success": False,
                "message": "message.validation-error",
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }
    
    @classmethod
    def get_history_inventory(cls,user,branch, page=1, start_date=None,end_date=None,pack_id=None,user_id=None):
        try:

            # -------------------------
            # 1. Validate company
            # -------------------------
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # 2. Validate branch
            # -------------------------
            if not branch:
                return {
                    "success": False,
                    "message": "message.branch-required",
                    "error": "Branch is required"
                }

            # -------------------------
            # 3. Build query
            # -------------------------
            queryset = HistoryInventory.objects.filter(
                company=company,
                branch=branch
            )

            # -------------------------
            # 4. Optional filters
            # -------------------------

            # Filter by pack
            if pack_id:
                queryset = queryset.filter(pack_id=pack_id)

            # Filter by user
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            # Filter by date range
            if start_date and end_date:
                queryset = queryset.filter(
                    update_date__range=[start_date, end_date]
                )

            elif start_date:
                queryset = queryset.filter(
                    update_date__gte=start_date
                )

            elif end_date:
                queryset = queryset.filter(
                    update_date__lte=end_date
                )

            # -------------------------
            # 5. Order query
            # -------------------------
            queryset = queryset.select_related(
                'pack',
                'user'
            ).order_by('-update_date')

            # -------------------------
            # 6. Pagination
            # -------------------------
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(page)

            # -------------------------
            # 7. Build results
            # -------------------------
            results = []

            for item in page_obj:
                date = Plus.convert_from_utc(item.update_date, user.timezone)
                update_date = Plus.format_date_to_text(date.isoformat(), user.language, 1)
                old_stock = float(item.old_stock)
                new_stock = float(item.new_stock)

                difference = new_stock - old_stock

                if difference > 0:
                    movement_type = "increase"
                elif difference < 0:
                    movement_type = "decrease"
                else:
                    movement_type = "no-change"

                results.append({
                    "id": item.id,
                    "pack_id": item.pack.id,
                    "pack_name": item.pack.name,
                    "old_stock": old_stock,
                    "new_stock": new_stock,
                    "difference": difference,
                    "movement_type": movement_type,
                    "unity_type": item.unity_type,
                    "updated_by": item.user.username if item.user else None,
                    "update_date": update_date
                })

            # -------------------------
            # 8. Return response
            # -------------------------
            return {
                "success": True,
                "message": "message.history-found",
                "answer": results,
                "pagination": {
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_records": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }

        except ValidationError as e:
            return {
                "success": False,
                "message": "message.validation-error",
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }

    @classmethod
    def update_inventory(cls, user, pack_id, stock=None, min_stock=None):
        try:
            # -------------------------
            # 1. Validate pack_id
            # -------------------------
            if not pack_id:
                return {
                    "success": False,
                    "message": "message.pack-id-required",
                    "error": "Pack id is required"
                }

            # -------------------------
            # 2. Validate company
            # -------------------------
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # 3. Validate branch
            # -------------------------
            branch = getattr(user, 'branch', None)

            if not branch:
                return {
                    "success": False,
                    "message": "message.user-without-branch",
                    "error": "User has no branch"
                }

            # -------------------------
            # 4. Get pack
            # -------------------------
            try:
                pack = Pack.objects.get(
                    id=pack_id,
                    company=company
                )

            except Pack.DoesNotExist:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }

            # -------------------------
            # 5. Get or create inventory
            # -------------------------
            inventory, created = Inventory.objects.get_or_create(
                company=company,
                branch=branch,
                pack=pack,
                defaults={
                    "stock": 0,
                    "min_stock": 0
                }
            )

            # -------------------------
            # 7. See if exist a change in the inventory of the pack fo save the move in the history
            # -------------------------
            old_stock=inventory.stock
            new_stock=Decimal(str(stock))

            if old_stock!=new_stock:
                HistoryInventory.objects.create(
                    company=user.company,
                    branch=user.branch,
                    pack=inventory.pack,
                    old_stock=old_stock,
                    new_stock=new_stock,
                    unity_type=inventory.pack.unity_type,
                    user=user
                )

            # -------------------------
            # 8. Update values
            # -------------------------
            if stock is not None:
                inventory.stock = Decimal(str(stock))

            if min_stock is not None:
                inventory.min_stock = Decimal(str(min_stock))



            inventory.save()


            
            # -------------------------
            # 9. Build response
            # -------------------------
            data = {
                "id": pack.id,
                "name": pack.name,
                "stock": float(inventory.stock),
                "min_stock": float(inventory.min_stock),
                "updated": True
            }

            return {
                "success": True,
                "message": "message.inventory-updated",
                "error": "",
                "answer": data
            }

        except ValidationError as e:
            return {
                "success": False,
                "message": "message.validation-error",
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }