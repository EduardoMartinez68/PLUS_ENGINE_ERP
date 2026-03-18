from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.services.models import Pack, ProductDepartment, ProductCategory, Tax, PackTax, BranchPack
from core.models import Branch
from django.db.models import Q
from django.core.paginator import Paginator
from ..plus_wrapper import Plus
import json

def parse_json_field(value, default):
    if not value:
        return default
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except:
        return default
    
class PackService:

    @classmethod
    def add(cls, user, data):
        try:
            # -------------------------
            #1. get the data of the form
            # -------------------------
            name = data.get("name", "").strip()
            description = data.get("description", "")
            base_price = Decimal(str(data.get("base_price", 0)))

            category_id = int(data.get("category")) if data.get("category") else None
            department_id = int(data.get("department")) if data.get("department") else None

            taxes_list = parse_json_field(data.get("taxes"), [])
            skus = parse_json_field(data.get("skus"), [])
            tags = parse_json_field(data.get("tags"), [])
            note = data.get("note", "")

            pack_type=data.get("pack_type", 1)

            #convert IDs to numbers
            taxes_list = [int(t) for t in taxes_list]


            #2. here we will do the valid 
            if not name:
                return {
                    "success": False,
                    "message": "message.pack-name-required",
                    "error": "Name is required"
                }


            company = getattr(user, 'company', None)
            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }
            
            # -------------------------
            # 3. avoid duplicate
            # -------------------------
            exists = Pack.objects.filter(
                company=company,
                name__iexact=name,
                activated=True
            ).exists()

            if exists:
                return {
                    "success": False,
                    "message": "message.pack-already-exists",
                    "error": "Pack already exists"
                }

            # -------------------------
            # Validar departamento
            # -------------------------
            department = None
            if department_id:
                department = ProductDepartment.objects.filter(
                    id=department_id,
                    company=company,
                    activated=True
                ).first()

            # -------------------------
            # valid category
            # -------------------------
            category = None
            if category_id:
                category = ProductCategory.objects.filter(
                    id=category_id,
                    company=company,
                    activated=True
                ).first()

            # -------------------------
            # create Pack (transition)
            # -------------------------
            with transaction.atomic():
                # -------------------------
                # 1. Add pack (global)
                # -------------------------
                #first we will to create the pack of the company
                pack = Pack.objects.create(
                    company=company,
                    name=name,
                    description=description,
                    department=department,
                    category=category,
                    pack_type=pack_type,
                    skus=skus,
                    tags=tags,
                    note=note,
                    activated=True
                )
                # -------------------------
                # 2. Add taxes (global)
                # -------------------------
                total_tax_rate = Decimal('0')

                if taxes_list:
                    taxes = Tax.objects.filter(
                        id__in=taxes_list,
                        company=company,
                        activated=True
                    )

                    pack_taxes = []
                    for tax in taxes:
                        pack_taxes.append(PackTax(pack=pack, tax=tax))
                        total_tax_rate += tax.rate

                    PackTax.objects.bulk_create(pack_taxes)

                # -------------------------
                # 3. Calculate final price once
                # -------------------------
                price_with_taxes = base_price + (base_price * total_tax_rate / Decimal('100'))
                price_with_taxes = round(price_with_taxes, 2)

                # -------------------------
                # 4. Get ALL branches of the company
                # -------------------------
                #after we will to create the price of the pack in the branch
                branches = Branch.objects.filter(
                    company=company,
                    activated=True
                )
 
                # -------------------------
                # 5. Create BranchPack for each branch
                # -------------------------
                branch_packs = []
                for branch in branches:
                    branch_packs.append(
                        BranchPack(
                            company=company,
                            branch=branch,
                            pack=pack,
                            base_price=base_price,
                            price_with_taxes=price_with_taxes,
                            activated=True
                        )
                    )

                BranchPack.objects.bulk_create(branch_packs)
            return {
                "success": True,
                "message": "message.pack-created",
                "error": "",
                "data": {
                    "id": pack.id,
                    "name": pack.name
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
    def update(cls, user, data, can_update_prices):
        try:
            # -------------------------
            # 1. get the data of the form
            # -------------------------
            name = data.get("name", '')
            description = data.get("description", '')
            pack_type = data.get("pack_type", '')
            department_id = data.get("department")
            category_id = data.get("category")

            #get the taxes of the product 
            taxes_list = parse_json_field(data.get("taxes"), [])
            skus = parse_json_field(data.get("skus"), [])
            tags = parse_json_field(data.get("tags"), [])

            
            note = data.get("note", '')

            #here we will see if the user can delete this service. If not can <activated> be true. 
            activated = Plus.to_bool(data.get("activated", True))
 


            # -------------------------
            # 2. Here we will do valid of the form
            # -------------------------
            pack_id = data.get("id")
            if not pack_id:
                return {
                    "success": False,
                    "message": "message.pack-id-required",
                    "error": "Pack id is required"
                }

            if not name:
                return {
                    "success": False,
                    "message": "message.pack-name-required",
                    "error": "Name is required"
                }
            
            #here we will see if the company of the user exist
            company = getattr(user, 'company', None)
            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }
            
            # -------------------------
            # 3. get the pack with help of the company of the user
            # -------------------------
            try:
                pack = Pack.objects.get(id=pack_id, company=company)
            except Pack.DoesNotExist:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }


            # -------------------------
            # valid duplicate (only activate)
            # -------------------------
            exists = Pack.objects.filter(
                company=company,
                name__iexact=name,
                activated=True
            ).exclude(id=pack.id).exists()

            if exists:
                return {
                    "success": False,
                    "message": "message.pack-already-exists",
                    "error": "Another pack with this name already exists"
                }

            # -------------------------
            # valid departament
            # -------------------------
            department = None
            if department_id:
                department = ProductDepartment.objects.filter(
                    id=department_id,
                    company=company,
                    activated=True
                ).first()

            # -------------------------
            # valid category
            # -------------------------
            category = None
            if category_id:
                category = ProductCategory.objects.filter(
                    id=category_id,
                    company=company,
                    activated=True
                ).first()

            # -------------------------
            # transitions
            # -------------------------
            with transaction.atomic():
                # Update pack basic info
                pack.name = name
                pack.description = description
                pack.pack_type = pack_type
                pack.department = department
                pack.category = category
                pack.skus = skus
                pack.tags = tags
                pack.note = note
                pack.activated = activated
                pack.save()

                # -------------------------
                # Taxes replacement
                # -------------------------
                total_tax_rate = Decimal('0')
                PackTax.objects.filter(pack=pack).delete()

                if taxes_list:
                    taxes = Tax.objects.filter(
                        id__in=taxes_list,
                        company=company,
                        activated=True
                    )

                    pack_taxes = []
                    for tax in taxes:
                        pack_taxes.append(PackTax(pack=pack, tax=tax))
                        total_tax_rate += tax.rate

                    PackTax.objects.bulk_create(pack_taxes)

                # -------------------------
                # Update price only for user's branch
                # -------------------------
                if can_update_prices:
                    branch_pack = BranchPack.objects.filter(
                        company=company,
                        branch=user.branch,
                        pack=pack,
                        activated=True
                    ).first()

                    if branch_pack:
                        base_price = Decimal(str(data.get("base_price", branch_pack.base_price)))
                        price_with_taxes = base_price + (base_price * total_tax_rate / Decimal('100'))
                        branch_pack.base_price = base_price
                        branch_pack.price_with_taxes = round(price_with_taxes, 2)
                        branch_pack.save()

            return {
                "success": True,
                "message": "message.pack-updated",
                "error": "",
                "data": {
                    "id": pack.id,
                    "name": pack.name,
                    "activated": pack.activated
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
    def activate(cls, user, pack_id):
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
            # 2. Validate user's company
            # -------------------------
            company = getattr(user, 'company', None)
            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # 3. Get pack
            # -------------------------
            try:
                pack = Pack.objects.get(id=pack_id, company=company)
            except Pack.DoesNotExist:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }

            # -------------------------
            # 4. Activate pack
            # -------------------------
            with transaction.atomic():
                pack.activated = True
                pack.save(update_fields=["activated", "last_update"])

            return {
                "success": True,
                "message": "message.pack-activated",
                "error": "",
                "data": {
                    "id": pack.id,
                    "name": pack.name,
                    "activated": pack.activated
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": "message.unexpected-error",
                "error": str(e)
            }
    
    
    @classmethod
    def search(cls, user, key=None, page=1, activated=True, amountOfData=20):
        try:
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # Query base (multiempresa + activos)
            # -------------------------
            queryset = Pack.objects.filter(
                company=company,
                activated=activated,
                branch_prices__branch=user.branch,
                branch_prices__activated=True
            ).select_related(
                "department", "category"
            ).prefetch_related(
                "taxes__tax"
            )




            # -------------------------
            # Filtro por búsqueda
            # -------------------------
            if key:
                key = key.strip()

                queryset = queryset.filter(
                    Q(name__icontains=key) |
                    Q(skus__icontains=key)   # búsqueda dentro del JSON
                )

            # -------------------------
            # Orden
            # -------------------------
            queryset = queryset.order_by("name")

            # -------------------------
            # Paginación logic
            # -------------------------
            paginator = Paginator(queryset, amountOfData)
            page_obj = paginator.get_page(page)

            # -------------------------
            # Formatear resultados
            # -------------------------
            results = []
            for pack in page_obj:
                branch_price = pack.branch_prices.filter(
                    branch=user.branch,
                    activated=activated
                ).first()

                #create the data of the taxes
                taxes = [
                    [pt.tax.name, float(pt.tax.rate), pt.tax.id]
                    for pt in pack.taxes.all()
                    if pt.tax.activated
                ]

                results.append({
                    "id": pack.id,
                    "name": pack.name,
                    "price": float(branch_price.price_with_taxes) if branch_price else 0,
                    "base_price": float(branch_price.base_price) if branch_price else 0,
                    "pack_type": pack.pack_type,
                    "department": pack.department.name if pack.department and pack.department.activated else '',
                    "category": pack.category.name if pack.category and pack.category.activated else '',
                    "skus": pack.skus,
                    "taxes": taxes
                })

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer":results,
                "pagination": {
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
    def get_information_by_id(cls, user, pack_id, branch=None):
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
            # 3. Get pack
            # -------------------------
            try:
                pack = Pack.objects.select_related(
                    "department",
                    "category"
                ).get(id=pack_id, company=company)
            except Pack.DoesNotExist:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }

            # -------------------------
            # 4. Get branch price (optional)
            # -------------------------
            branch=user.branch
            branch_pack = None
            branch_pack = BranchPack.objects.filter(
                company=company,
                branch=branch,
                pack=pack,
                activated=True
            ).first()

            base_price = branch_pack.base_price if branch_pack else 0
            price_with_taxes = branch_pack.price_with_taxes if branch_pack else 0

            # -------------------------
            # 5. Taxes
            # -------------------------
            pack_taxes = pack.taxes.filter(
                tax__company=company,
                tax__activated=True
            ).select_related("tax")

            taxes_list = [
                {
                    "id": pt.tax.id,
                    "name": pt.tax.name
                }
                for pt in pack_taxes
            ]
            # -------------------------
            # 6. Safe image helper
            # -------------------------
            def get_image_url(image_field):
                try:
                    return image_field.url if image_field else None
                except:
                    return None

            # -------------------------
            # 7. Build response
            # -------------------------
            data = {
                "id": pack.id,
                "name": pack.name,
                "description": pack.description,
                "pack_type": pack.pack_type,
                "department": {
                    "id": pack.department.id,
                    "name": pack.department.name
                } if pack.department else None,
                "category": {
                    "id": pack.category.id,
                    "name": pack.category.name
                } if pack.category else None,
                
                "taxes": taxes_list,

                "base_price": float(base_price),
                "price_with_taxes": float(price_with_taxes),
                "skus": pack.skus or [],
                "tags": pack.tags or [],
                "note": pack.note,
                "activated": pack.activated,
                "images": {
                    "image1": get_image_url(pack.image1),
                    "image2": get_image_url(pack.image2),
                    "image3": get_image_url(pack.image3),
                    "image4": get_image_url(pack.image4),
                },
                "creation_date": pack.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                "last_update": pack.last_update.strftime("%Y-%m-%d %H:%M:%S"),
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