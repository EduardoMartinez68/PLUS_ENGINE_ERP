from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.services.models import Pack, ProductDepartment, ProductCategory, Tax, PackTax, BranchPack, Inventory, PackItem, HistoryInventory
from core.models import Branch
from django.db.models import Q, Prefetch
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
            track_inventory =Plus.to_bool(data.get("track_inventory", False))
            show_fo_sale=Plus.to_bool(data.get('show_fo_sale', False))
            stock = Plus.to_float(data.get("stock", 0))
            min_stock = Plus.to_float(data.get("min_stock", 0))
            pack_type= Plus.to_float(data.get("pack_type", 1))
            unity_type=data.get('unity_type', 1)
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
                    activated=True,
                    unity_type=unity_type,
                    track_inventory=track_inventory,
                    show_fo_sale=show_fo_sale
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


                # -------------------------
                # 6. Create Inventory per branch
                # -------------------------
                PackItem.objects.create(
                    pack=pack,
                    product=pack,
                    quantity=1
                )

                if track_inventory and pack_type == 0:  # only in products
                    inventories = []

                    for branch in branches:
                        inventories.append(
                            Inventory(
                                company=company,
                                branch=branch,
                                pack=pack,
                                stock=stock,
                                min_stock=min_stock
                            )
                        )

                    Inventory.objects.bulk_create(inventories)
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
    def update(cls, user, data, can_update_prices, can_update_inventory):
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
            track_inventory =Plus.to_bool(data.get("track_inventory", False))
            show_fo_sale=Plus.to_bool(data.get('show_fo_sale', False))
            stock = Plus.to_float(data.get("stock", 0))
            min_stock = Plus.to_float(data.get("min_stock", 0))
            unity_type=data.get('unity_type', 1)
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
                pack.unity_type=unity_type
                pack.activated = activated
                pack.track_inventory=track_inventory
                pack.show_fo_sale=show_fo_sale
                pack.save()

            # -------------------------
            # Inventory management
            # -------------------------
            branch=user.branch
            inventory = Inventory.objects.filter(
                company=user.company,
                branch=user.branch,
                pack=pack
            ).first()

            # 🟢 Caso 1: activar inventario y no existe
            if track_inventory and not inventory:
                Inventory.objects.create(
                    company=company,
                    branch=branch,
                    pack=pack,
                    stock=stock,
                    min_stock=min_stock
                )

            # 🟡 Caso 2: ya existe → actualizar
            elif track_inventory and inventory and can_update_inventory:
                #here we will see if the user do a change 
                old_stock=inventory.stock
                new_stock=Decimal(str(stock))

                if old_stock!=new_stock: #if exist a change save the data in the history
                    HistoryInventory.objects.create(
                        company=user.company,
                        branch=user.branch,
                        pack=inventory.pack,
                        old_stock=old_stock,
                        new_stock=new_stock,
                        unity_type=inventory.pack.unity_type,
                        user=user
                    )

                inventory.stock = stock
                inventory.min_stock = min_stock
                inventory.save()

            # 🔴 Caso 3: desactivar inventario
            elif not track_inventory and inventory:
                # OPCIÓN A (recomendada): NO borrar, solo dejarlo
                inventory.min_stock = 0
                inventory.save()

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
                    base_price = Plus.to_float(data.get("base_price", branch_pack.base_price))
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
    def search2(cls, user, key=None, page=1, activated=True, amountOfData=20, show_for_sale=None):
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
            # Filtro show_for_sale
            # -------------------------
            if show_for_sale is not None:
                queryset = queryset.filter(
                    show_fo_sale=show_for_sale
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
                    "img":'/static/img/info/supplies.webp',
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
    def search(cls, user, key=None, page=1, activated=True, amountOfData=20, show_for_sale=None):
        try:
            company = getattr(user, "company", None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # Query base
            # -------------------------
            queryset = Pack.objects.filter(
                company=company,
                activated=activated
            ).select_related(
                "department",
                "category"
            ).prefetch_related(
                Prefetch(
                    "branch_prices",
                    queryset=BranchPack.objects.filter(
                        branch=user.branch
                    ),
                    to_attr="current_branch_price"
                ),
                "taxes__tax"
            )

            # -------------------------
            # Mostrar para venta
            # -------------------------
            if show_for_sale is not None:
                queryset = queryset.filter(
                    show_fo_sale=show_for_sale
                )

            # -------------------------
            # Buscar
            # -------------------------
            if key:
                key = key.strip()

                queryset = queryset.filter(
                    Q(name__icontains=key) |
                    Q(skus__icontains=key)
                )

            queryset = queryset.order_by("name")

            # -------------------------
            # Paginación
            # -------------------------
            paginator = Paginator(queryset, amountOfData)
            page_obj = paginator.get_page(page)

            results = []

            for pack in page_obj:

                # Obtener precio de la sucursal
                if pack.current_branch_price:
                    branch_price = pack.current_branch_price[0]
                else:
                    # Si no existe, crearlo automáticamente
                    branch_price = BranchPack.objects.create(
                        company=company,
                        branch=user.branch,
                        pack=pack,
                        base_price=0,
                        price_with_taxes=0,
                        activated=True
                    )

                taxes = [
                    [pt.tax.name, float(pt.tax.rate), pt.tax.id]
                    for pt in pack.taxes.all()
                    if pt.tax.activated
                ]

                results.append({
                    "id": pack.id,
                    "img": "/static/img/info/supplies.webp",
                    "name": pack.name,
                    "price": float(branch_price.price_with_taxes),
                    "base_price": float(branch_price.base_price),
                    "pack_type": pack.pack_type,
                    "department": pack.department.name if pack.department and pack.department.activated else "",
                    "category": pack.category.name if pack.category and pack.category.activated else "",
                    "skus": pack.skus,
                    "taxes": taxes
                })

            return {
                "success": True,
                "message": "",
                "error": "",
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
            # 4.1 Get inventory
            # -------------------------
            inventory = Inventory.objects.filter(
                company=company,
                branch=branch,
                pack=pack
            ).first()
            stock = inventory.stock if inventory else 0
            min_stock = inventory.min_stock if inventory else 0
            track_inventory = pack.track_inventory
            show_fo_sale=pack.show_fo_sale

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
            # 5.1 Get items of pack
            # -------------------------
            pack_items = PackItem.objects.filter(
                pack=pack
            ).select_related("product")

            items_list = []

            for item in pack_items:

                product = item.product

                # get branch price of item
                item_branch_pack = BranchPack.objects.filter(
                    company=company,
                    branch=branch,
                    pack=product,
                    activated=True
                ).first()

                base_price_item = item_branch_pack.base_price if item_branch_pack else 0
                price_item = item_branch_pack.price_with_taxes if item_branch_pack else 0

                # image
                img = None

                try:
                    img = product.image1.url if product.image1 else '/static/img/info/supplies.webp'
                except:
                    img = '/static/img/info/supplies.webp'

                items_list.append({
                    "id": product.id,
                    "name": product.name,
                    "quantity": float(item.quantity),
                    "price": float(price_item),
                    "base_price": float(base_price_item),
                    "skus": product.skus or [],
                    "img": img
                })
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
                "unity_type":pack.unity_type,
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
                "track_inventory": track_inventory,
                "show_fo_sale":show_fo_sale,
                "stock": float(stock),
                "min_stock": float(min_stock),
                "images": {
                    "image1": get_image_url(pack.image1),
                    "image2": get_image_url(pack.image2),
                    "image3": get_image_url(pack.image3),
                    "image4": get_image_url(pack.image4),
                },
                "creation_date": pack.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                "last_update": pack.last_update.strftime("%Y-%m-%d %H:%M:%S"),
                "items_list":items_list
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
    def update_item_pack(cls, user, pack_id, data):
        try:
            # -------------------------
            # 1. Get company
            # -------------------------
            company = getattr(user, 'company', None)

            if not company:
                return {
                    "success": False,
                    "message": "message.user-without-company",
                    "error": "User has no company"
                }

            # -------------------------
            # 2. Validate pack
            # -------------------------
            pack = Pack.objects.filter(
                id=pack_id,
                company=company,
                activated=True
            ).first()

            if not pack:
                return {
                    "success": False,
                    "message": "message.pack-not-found",
                    "error": "Pack not found"
                }

            # -------------------------
            # 3. Get items list
            # -------------------------
            list_items = data.get("listItem", [])

            if not isinstance(list_items, list):
                return {
                    "success": False,
                    "message": "message.invalid-items-format",
                    "error": "listItem must be an array"
                }

            # -------------------------
            # 4. Transaction
            # -------------------------
            with transaction.atomic():

                # -------------------------
                # Delete current items
                # -------------------------
                PackItem.objects.filter(pack=pack).delete()

                new_items = []

                for item in list_items:

                    product_id = item.get("id")
                    quantity = item.get("quantity", 1)

                    # validate
                    if not product_id:
                        continue

                    try:
                        quantity = Decimal(str(quantity))
                    except:
                        quantity = Decimal("1")

                    # -------------------------
                    # Find product
                    # -------------------------
                    product = Pack.objects.filter(
                        id=product_id,
                        company=company,
                        activated=True
                    ).first()

                    if not product:
                        continue

                    # avoid recursive self pack
                    # if you want allow self pack remove this
                    if int(pack.id) == int(product.id):
                        continue

                    new_items.append(
                        PackItem(
                            pack=pack,
                            product=product,
                            quantity=quantity
                        )
                    )

                # -------------------------
                # Bulk create
                # -------------------------
                if new_items:
                    PackItem.objects.bulk_create(new_items)

            return {
                "success": True,
                "message": "message.pack-items-updated",
                "error": "",
                "data": {
                    "pack_id": pack.id,
                    "total_items": len(new_items)
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