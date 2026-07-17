from io import BytesIO

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from apps.customers.plus_wrapper import Plus
from apps.sales.models import Sale, SaleItem, Pack, SaleHistory, SalePaymentMethod, DataReports
from apps.services.models import HistoryInventory
from apps.services.models import Inventory
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import threading
from apps.contract.models import Contract
from apps.sales.models import LinkPayOnline
from django.db.models import F
from django.conf import settings 
from apps.setting.models import NotificationSetting
from core.models import Company, Branch
from django.db.models import Sum

class Sales:
    @classmethod
    def calculate_all_the_move_money(cls):

        companies = Company.objects.all()

        total_companies = 0
        total_branches = 0

        for company in companies:

            total_companies += 1

            branches = Branch.objects.filter(company=company)

            for branch in branches:

                total_branches += 1

                report, created = DataReports.objects.get_or_create(
                    company=company,
                    branch=branch
                )

                inside = (
                    SalePaymentMethod.objects.filter(
                        company=company,
                        branch=branch,
                        amount__gt=0
                    ).aggregate(total=Sum("amount"))["total"] or 0
                )

                outside = (
                    SalePaymentMethod.objects.filter(
                        company=company,
                        branch=branch,
                        amount__lt=0
                    ).aggregate(total=Sum("amount"))["total"] or 0
                )

                report.total_inside_money = inside
                report.total_outside_money = abs(outside)
                report.save(update_fields=[
                    "total_inside_money",
                    "total_outside_money"
                ])

        return {
            "companies": total_companies,
            "branches": total_branches
        }
    
    @classmethod
    def add_money_movement(cls, company, branch, amount):
        current_year = timezone.now().year

        report, created = DataReports.objects.get_or_create(
            company=company,
            branch=branch,
            year=current_year,
            defaults={
                "total_inside_money": 0,
                "total_outside_money": 0,
            }
        )

        if amount >= 0:
            DataReports.objects.filter(pk=report.pk).update(
                total_inside_money=F("total_inside_money") + amount
            )
        else:
            DataReports.objects.filter(pk=report.pk).update(
                total_outside_money=F("total_outside_money") + abs(amount)
            )

    @classmethod
    def send_inventory_email_thread(
        cls,
        subject,
        html_content,
        recipient_list
    ):

        try:
            email = EmailMultiAlternatives(

                subject=subject,

                body="Your email client does not support HTML.",

                from_email="plus_recordatorios@gmail.com",

                to=recipient_list,
            )

            email.attach_alternative(
                html_content,
                "text/html"
            )

            email.send()

        except Exception as e:

            print(
                f"Error sending inventory email: {e}"
            )

    @classmethod
    def send_low_inventory_notifications(
        cls,
        company,
        branch,
        products
    ):

        if not products:
            return

        notification = NotificationSetting.objects.prefetch_related(
            'users__user'
        ).filter(
            company=company,
            branch=branch,
            type_notification='inventory_low',
            notify_by_email=True
        ).first()

        if not notification:
            return

        emails = []

        for relation in notification.users.all():

            user = relation.user

            if user.email:

                emails.append(user.email)

        emails = list(set(emails))

        if not emails:
            return

        # build html
        html_content = """
        <h2>
            Low inventory alert
        </h2>

        <p>
            The following products are below
            minimum stock:
        </p>

        <ul>
        """

        for product in products:

            html_content += f"""
            <li>
                <strong>{product['name']}</strong><br>

                Stock:
                {product['stock']}<br>

                Minimum:
                {product['min_stock']}
            </li>

            <br>
            """

        html_content += "</ul>"

        subject = "Low inventory alert"

        thread = threading.Thread(

            target=cls.send_inventory_email_thread,

            args=(
                subject,
                html_content,
                emails
            )
        )

        thread.start()

    @classmethod
    def add(cls, user, data):
        """
        create a sale with his items and return:
        {
            "id": sale.id,
            "reference": sale.reference
        }
        """
        try:
            with transaction.atomic():

                # ---------- dates ----------
                expiration_date = None
                payment_term_days = int(data.get("payment_term_days") or 0) #convert to int because this come as string from the frontend

                if data.get("expiration_date"):
                    expiration_date = data.get("expiration_date") #save the expiration date that come from the frontend
                    expiration_date=Plus.convert_to_utc(expiration_date, user.timezone)
                elif payment_term_days > 0:
                    expiration_date = timezone.now() + timedelta(days=payment_term_days)
                    expiration_date=Plus.convert_to_utc(expiration_date, user.timezone)

                
                #here we will to get the customer for save in the sale, but for now we will save as None because we not have the module of customers
                customer=None
                customer_id=data.get("customer")
                if customer_id:
                    from apps.customers.models import Customer
                    customer = Customer.objects.filter(id=customer_id, company=user.company).first()

                employee=user
                employee_id=data.get("employee")
                if employee_id:
                    from core.models import CustomUser
                    employee = CustomUser.objects.filter(id=employee_id, company=user.company).first()

                # ---------- create sales ----------
                sale = Sale.objects.create(
                    company=user.company,
                    branch=user.branch,
                    customer=customer,
                    user=employee,
                    name_sale=data.get("name_sale", ''),
                    created_by=user,
                    subtotal=Decimal(data.get("subtotal", 0)),
                    discount_total=Decimal(data.get("discount_total", 0)),
                    tax_total=Decimal(data.get("tax_total", 0)),
                    total=Decimal(data.get("total", 0)),
                    balance=Decimal(data.get("total", 0)),
                    payment_term_days=payment_term_days,
                    expiration_date=expiration_date,
                    status='pending',
                    currency=data.get("currency", 'MXN')
                )

                # ---------- create the items ----------
                items = data.get("items", [])
                
                for item in items:

                    # search pack for SKU (only if exist SKU, because if not exist is because this is a product flash without pack)
                    pack = None
                    sku = item.get("sku") or item.get("name")

                    if sku: #if exist a sku in the product/service we will to see the information and save 
                        pack = Pack.objects.filter(
                            skus__contains=[sku],
                            company=user.company
                        ).first()
                        # if the product not exist, this is a product flash

                    # calculate the total tax rate (there may be several)
                    taxes = item.get("taxes", [])
                    total_tax_rate = sum(Decimal(t.get("rate", 0)) for t in taxes)

                    #save the item in the database
                    SaleItem.objects.create(
                        sale=sale,
                        pack=pack,
                        name=item.get("name",""),
                        quantity=Decimal(item.get("quantity", 1)),
                        unit_price=Decimal(item.get("unit_price", 0)),
                        discount=Decimal(item.get("discount", 0)),
                        tax_rate=total_tax_rate,
                        taxes=taxes, #save the taxes in the field taxes for know the taxes of the item in the moment of the sale
                        tax_amount=Decimal(item.get("taxes_total", 0)),
                        subtotal=Decimal(item.get("subtotal", 0)),
                        total=Decimal(item.get("total", 0))
                    )



                #----now we will to create the link for pay online with this sale----------------
                LinkPayOnline.objects.create(
                    sale=sale
                )

                # ---------- answer ----------
                return {
                    "success": True,
                    "message": "",
                    "error": "",
                    "answer": {
                        "id": sale.id,
                        "reference": sale.reference,
                        "status": sale.status
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e),
                "answer": {}
            }

    @classmethod
    def discount_inventory(
        cls,
        pack,
        branch,
        quantity_sold,
        low_inventory_products=None,
        user=None
    ):
        
        if low_inventory_products is None:
            low_inventory_products = []

        items = pack.items.select_related(
            'product'
        ).all()

        for item in items:

            if not item.product.track_inventory:
                continue

            try:

                inventory = Inventory.objects.select_related(
                    'pack',
                    'company',
                    'branch'
                ).get(
                    pack=item.product,
                    branch=branch
                )

            except Inventory.DoesNotExist:
                continue

            old_stock = inventory.stock

            discount_quantity = (
                item.quantity * quantity_sold
            )

            inventory.stock = F('stock') - discount_quantity
            inventory.save(update_fields=['stock'])

            inventory.refresh_from_db()
           
            # inventory history
            HistoryInventory.objects.create(
                company=inventory.company,
                branch=inventory.branch,
                pack=inventory.pack,
                old_stock=old_stock,
                new_stock=inventory.stock,
                unity_type=inventory.pack.unity_type,
                user=user
            )

            # low inventory validation
            if inventory.stock <= inventory.min_stock:
                low_inventory_products.append({
                    "id": inventory.pack.id,
                    "name": inventory.pack.name,
                    "stock": inventory.stock,
                    "min_stock": inventory.min_stock,
                    "branch": inventory.branch.name_branch
                })


        return low_inventory_products

    @classmethod
    def do_a_sale(cls, user, sale_id, data):
        try:
            with transaction.atomic():

                sale = Sale.objects.filter(
                    id=sale_id,
                    company=user.company
                ).first()

                if not sale:
                    return {"success": False, "error": "sale not found", "answer": {}}

                if sale.status in ["cancelled", "expiration_date"]:
                    return {"success": False, "error": "sale cannot be paid", "answer": {}}

                # -------- get payment breakdown --------
                pay_cash = Decimal(data.get("payCash", 0))
                pay_debit = Decimal(data.get("payDebit", 0))
                pay_credit = Decimal(data.get("payCredit", 0))
                pay_terminal = Decimal(data.get("payTerminal", 0))
                pay_transfer = Decimal(data.get("payTransfer", 0))

                cash_received = Decimal(pay_cash + pay_debit + pay_credit+pay_terminal+pay_transfer)

                if cash_received <= 0:
                    return {"success": False, "error": "invalid payment amount", "answer": {}}

                # Validate frontend is not lying
                if cash_received != Decimal(data.get("cash_received", 0)):
                    return {"success": False, "error": "payment mismatch", "answer": {}}

                

                # -------- old values --------
                old_amount_paid = sale.amount_paid
                old_balance = sale.balance

                # -------- calculate --------
                new_amount_paid = old_amount_paid + cash_received
                new_balance = sale.total - new_amount_paid

                change_given = Decimal("0")

                if new_balance < 0:
                    change_given = abs(new_balance)
                    new_balance = Decimal("0")
                    new_amount_paid = sale.total

                #------------now here we will see if the user can do the buy for time or need do the buy of one time----------------
                if sale.payment_term_days == 0 and new_balance > 0:
                    return {
                        "success": False,
                        "message": "sales.error.insufficient-money",
                        "error": "full payment required for this sale",
                        "answer": {}
                    }
            
                # -------- update sale --------
                sale.amount_paid = new_amount_paid
                sale.balance = new_balance

                if new_balance == 0:
                    sale.status = "paid"
                else:
                    sale.status = "accepted"

                if not sale.startDate:
                    sale.startDate = timezone.now()

                first_buy=sale.first_buy_do
                sale.first_buy_do=True
                sale.save()

                # -------- create history --------
                history=SaleHistory.objects.create(
                    sale=sale,
                    cash_received=cash_received,
                    change_given=change_given,
                    old_amount_paid=old_amount_paid,
                    old_balance=old_balance,
                    new_amount_paid=new_amount_paid,
                    new_balance=new_balance,
                    created_by=user
                )

                # -------- save payment methods --------
                payment_methods = []

                if pay_cash > 0:
                    payment_methods.append(("cash", pay_cash))

                card_total = pay_debit + pay_credit
                if card_total > 0:
                    payment_methods.append(("card", card_total))

                if pay_terminal > 0:
                    payment_methods.append(("terminal", pay_terminal))

                if pay_transfer > 0:
                    payment_methods.append(("transfer", pay_transfer))

                # Guardar métodos usados
                for method, amount in payment_methods:
                    SalePaymentMethod.objects.create(
                        company=user.company,
                        branch=user.branch,
                        sale=sale,
                        payment=history,
                        user=user,
                        method=method,
                        amount=amount
                    )

                    cls.add_money_movement(
                        company=user.company,
                        branch=user.branch,
                        amount=amount
                    )

                # Registrar cambio como salida de efectivo
                if change_given > 0:
                    SalePaymentMethod.objects.create(
                        company=user.company,
                        branch=user.branch,
                        sale=sale,
                        payment=history,
                        user=user,
                        method="change",
                        amount=-change_given   # NEGATIVO (sale dinero)
                    )

                    cls.add_money_movement(
                        company=user.company,
                        branch=user.branch,
                        amount=-change_given
                    )


                #now we will update the inventory with this sale. First we need see if this is the first sale
                low_inventory_products = [] #here we will to save the product that be low inventory
                if not first_buy:
                    sale_items = SaleItem.objects.select_related(
                        'pack'
                    ).filter(
                        sale=sale
                    )

                    for item in sale_items:
                        if item.pack:
                            cls.discount_inventory(
                                pack=item.pack,
                                branch=user.branch,
                                quantity_sold=item.quantity,
                                low_inventory_products=low_inventory_products,
                                user=user
                            )

                
                # send notifications
                cls.send_low_inventory_notifications(
                    company=user.company,
                    branch=user.branch,
                    products=low_inventory_products
                )

                return {
                    "success": True,
                    "answer": {
                        "reference": sale.reference,
                        "sale_id": sale.id,
                        "status": sale.status,
                        "amount_paid": float(sale.amount_paid),
                        "balance": float(sale.balance),
                        "change_given": float(change_given)
                    }
                }

        except Exception as e:
            return {"success": False, "error": str(e), "answer": {}}
        
    @classmethod
    def update_status(cls, user, sale_id, new_status):
        """
        only update the status of the sale.
        
        parameters:
            user
            sale_id
            new_status (str)

        Return:
        {
            "id": sale.id,
            "reference": sale.reference,
            "status": sale.status
        }
        """

        # Status permitidos desde el modelo
        valid_status = dict(Sale._meta.get_field('status').choices).keys()

        if new_status not in valid_status:
            raise ValueError(f"Status inválido: {new_status}")

        with transaction.atomic():

            # Buscar la venta (seguridad por empresa)
            sale = Sale.objects.filter(
                id=sale_id,
                company=user.company
            ).first()

            if not sale:
                raise ValueError("La venta no existe o no tienes permiso")

            # Opcional: bloquear si ya está cancelada o expirada
            if sale.status in ['cancelled', 'expiration_date']:
                raise ValueError("No se puede modificar una venta cancelada o expirada")

            # Si cambia a accepted → marcar fecha de inicio
            if new_status == 'accepted' and sale.status != 'accepted':
                sale.startDate = timezone.now()

            # Si cambia a paid → marcar como pagado
            if new_status == 'paid':
                sale.amount_paid = sale.total
                sale.balance = 0

            sale.status = new_status
            sale.save(update_fields=[
                'status',
                'startDate',
                'amount_paid',
                'balance'
            ])

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer": {
                    "id": sale.id,
                    "reference": sale.reference,
                    "status": sale.status
                }
            }
    
     
    #this function is for get the IP of the customer
    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # puede venir una lista de IPs → tomamos la primera
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @classmethod
    def save_signature(cls, request, user, sale_id, data):
        """
        only update the status of the sale.
        
        parameters:
            user
            sale_id
            new_status (str)

        Return:
        {
            "id": sale.id,
            "reference": sale.reference,
            "status": sale.status
        }
        """

        # this is the new status of the sale
        new_status='accepted'

        with transaction.atomic():

            # search the sale in the company
            sale = Sale.objects.filter(
                id=sale_id,
                company=user.company
            ).first()


            #if not exist the sale we return a error
            if not sale:
                raise ValueError("La venta no existe o no tienes permiso")

            #if the sale was cancelled or expired also return a error for security
            if sale.status in ['cancelled', 'expiration_date']:
                raise ValueError("No se puede modificar una venta cancelada o expirada")

            #get the IP of the user 
            ip = cls.get_client_ip(request)

            #if can update the sale to accepted now we will to create a sale or get the contract that have
            #vinculate the sale if exist.
            contract, created = Contract.objects.get_or_create(
                sale=sale,
                contract_text=data.get('contract_text',''),

                #information of the customer
                patiente_signature_json=data.get('patiente_signature_json',''),
                patient_name=data.get('patient_name',''),
                company_signature_json=data.get('company_signature_json',''),
                company_name=data.get('company_name',''),
                patient_ip=ip,
            )

            if not contract:
                raise ValueError("No se creo el contrato")

                
            # save the date for know when was accepted the sale
            if new_status == 'accepted' and sale.status != 'accepted':
                sale.startDate = timezone.now()


            #update the status and the information
            sale.status = new_status
            sale.save(update_fields=[
                'status',
                'startDate',
                'amount_paid',
                'balance'
            ])

            return {
                "success": True,
                "message": "",
                "error": "",
                "answer": {
                    "id": sale.id,
                    "reference": sale.reference,
                    "status": sale.status
                }
            }


    @classmethod
    def cancel_sale(cls, user, sale_id, data):
        #here we will see if the user write a note for cancelled this sale,
        #else we send a message of error to the frontend
        note_cancelled = data.get('note_cancelled', '')
        if not note_cancelled.strip():
            return {
                "success": False,
                "message": "sales.message.not-add-comment-cancel-sale",
                "error": "You need write a note for cancelled this sale",
            }
        
        sale = Sale.objects.filter(
            id=sale_id,
            company=user.company
        ).first()

        if not sale:
            return {
                "success": False,
                "message": "sales.message.this-sale-not-exist",
                "error": "This sale does not exist",
            }
        
        #here we will see if the sale not is cancelled 
        #if the sale is cancelled we will to send a message of error
        if sale.status == "cancelled":
            return {
                "success": False,
                "message": "sales.message.sale-already-cancelled",
                "error": "This sale was already cancelled",
            }
        
        if sale.amount_paid > 0:

            old_amount_paid = sale.amount_paid
            old_balance = sale.balance

            refund_amount = sale.amount_paid

            new_amount_paid = Decimal("0.00")
            new_balance = Decimal("0.00")

            # Crear movimiento inverso
            refund = SaleHistory.objects.create(
                sale=sale,
                cash_received = -refund_amount,  # negativo
                change_given = 0,
                old_amount_paid = old_amount_paid,
                old_balance = old_balance,
                new_amount_paid = new_amount_paid,
                new_balance = new_balance,
                created_by = user
            )

            # Método de pago negativo
            SalePaymentMethod.objects.create(
                company=sale.company,
                branch=sale.branch,
                sale=sale,
                payment=refund,
                user=user,
                method="change",
                amount = -refund_amount
            )

            cls.add_money_movement(
                company=user.company,
                branch=user.branch,
                amount=-refund_amount
            )

        sale.amount_paid = Decimal("0.00")
        sale.balance = Decimal("0.00")
        sale.status = "cancelled"
        sale.note_cancelled=note_cancelled
        sale.save()

        return {
            "success": True,
            "message": "",
            "error": "",
            "answer": {
                "id": sale.id,
                "reference": sale.reference,
                "status": sale.status
            }
        }


    @classmethod
    def get_sale_info(cls, user, sale_id):
        """
        Return all information of a sale:
        {
            sale info,
            customer,
            items
        }
        """
        try:
            # ---------- get sale ----------
            sale = Sale.objects.select_related(
                "customer", "user", "branch"
            ).prefetch_related(
                "items"  # related_name in SaleItem -> sale = ForeignKey(..., related_name="items")
            ).filter(
                id=sale_id,
                company=user.company
            ).first()

            if not sale:
                return {
                    "success": False,
                    "message": "",
                    "error": "sale not found",
                    "answer": {}
                }

            # ---------- customer info ----------
            customer_data = None
            if sale.customer:
                customer_data = {
                    "id": sale.customer.id,
                    "name": getattr(sale.customer, "name", ""),
                    "email": getattr(sale.customer, "email", ""),
                }


            employee_data = None
            if sale.user:
                employee_data = {
                    "id": sale.user.id,
                    "name": getattr(sale.user, "name", ""),
                }
            # ---------- items ----------
            items_data = []

            for item in sale.items.all():
                items_data.append({
                    "id": item.id,
                    "pack_id": item.pack.id if item.pack else None,
                    "name": item.name,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "discount": float(item.discount),
                    "taxes": item.taxes,
                    "tax_rate": float(item.tax_rate),
                    "tax_amount": float(item.tax_amount),
                    "subtotal": float(item.subtotal),
                    "total": float(item.total),
                })

            #link of buy
            #get the link of the sale for pay online. If not exist we will create a new link for this sale
            link_pay_online_url=''
            link_pay_online=LinkPayOnline.objects.filter(sale=sale).first()
            if not link_pay_online: #if not exist a link for pay online we will create a new link for this sale
                link_pay_online=LinkPayOnline.objects.create(sale=sale)


            #now we will to see if the link of pay is valid 
            if link_pay_online.activate:
                #if the link is active we will to add the link in the email for pay online
                link_pay_online_url=f"{settings.PLUS_URL}/sales/pay_sale/{link_pay_online.key_link}"

            # ---------- sale info ----------
            expiration_date=None
            if sale.expiration_date:
                expiration_date=Plus.convert_from_utc(sale.expiration_date, user.timezone)
            sale_data = {
                "id": sale.id,
                'name_sale':sale.name_sale,
                "reference": sale.reference,
                "status": sale.status,
                "customer": customer_data,
                "employee":employee_data,
                "branch_id": sale.branch.id if sale.branch else None,
                "user_id": sale.user.id if sale.user else None,
                "subtotal": float(sale.subtotal),
                "discount_total": float(sale.discount_total),
                "tax_total": float(sale.tax_total),
                "currency": sale.currency,
                "total": float(sale.total),
                "balance": float(sale.balance),
                "payment_term_days": sale.payment_term_days,
                "expiration_date": expiration_date,
                "created_at": sale.created_at if hasattr(sale, "created_at") else None,
                "items": items_data,
                "note_cancelled":sale.note_cancelled,
                "link_pay_online_url":link_pay_online_url
            }
            
            return {    
                "success": True,
                "message": "",
                "error": "",
                "answer": sale_data
            }

        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e),
                "answer": {}
            }
        
    @classmethod
    def search(cls, user, key=None, page=1, view_sales_totals=False,
            customer_id=None, user_id=None,
            date_start=None, date_end=None, status=None):
        


        try:
            query = Sale.objects.filter(company=user.company, branch=user.branch)

            # 🔎 1. Búsqueda por texto
            if key:
                query = query.filter(
                    Q(reference__icontains=key) |
                    Q(name_sale__icontains=key)
                )

            # 👤 2. Filtro por cliente
            if customer_id:
                query = query.filter(customer_id=customer_id)

            # 👨‍⚕️ 3. Filtro por usuario (doctor/vendedor)
            if user_id:
                query = query.filter(user_id=user_id)

            # 📅 4. Filtro por fechas
            if date_start:
                date_start=Plus.convert_to_utc(date_start, user.timezone)
                query = query.filter(creationDate__date__gte=date_start)

            if date_end:
                date_end=Plus.convert_to_utc(date_end, user.timezone)
                query = query.filter(creationDate__date__lte=date_end)

            # 📌 5. Filtro por estado
            if status:
                query = query.filter(status=status)

            # 🔥 Orden
            query = query.order_by('-creationDate', '-id')

            # 📄 Paginación
            paginator = Paginator(query, 20)

            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            results = []

            def get_initials(name=''):
                return ''.join([word[0] for word in name.split()][:2]).upper()
            

            for sale in page_obj:
                date = Plus.convert_from_utc(sale.creationDate, user.timezone)
                formatted_date = Plus.format_date_to_text(date.isoformat(), user.language, 1)

                total = Plus.format_currency(sale.total, sale.currency) if view_sales_totals else '---'
                amount_paid = Plus.format_currency(sale.amount_paid, sale.currency) if view_sales_totals else '---'
                balance = Plus.format_currency(sale.balance, sale.currency) if view_sales_totals else '---'

                user_name = sale.user.name if sale.user else 'Doc.'
                photo=sale.user.avatar.url if sale.user and sale.user.avatar else '/static/img/employees-select.webp'


                results.append({
                    "id": sale.id,
                    "reference": sale.reference,
                    "name_sale": sale.name_sale if sale.name_sale else 'sales.navbar.new',
                    "customer": sale.customer.name if sale.customer else 'sales.label.public',
                    "photo_user": photo,
                    "user": user_name,
                    "total": total,
                    "amount_paid": amount_paid,
                    "balance": balance,
                    "currency": sale.currency,
                    "status": sale.status,
                    "creationDate": formatted_date,
                    "branch": sale.branch.name_branch if sale.branch else None
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
                "message": "",
                "error": str(e),
                "answer": [],
                "pagination": {}
            }

    @classmethod
    def get_sale_history(cls, user, sale_id, page=1, per_page=10):
        try:
            # 🔹 1. Validate sale exists and belongs to user company
            sale = Sale.objects.select_related('company', 'branch').filter(
                id=sale_id,
                company=user.company  # ajusta si tu user no tiene company directa
            ).first()

            if not sale:
                return {
                    "success": False,
                    "message": "",
                    "error": "Sale not found",
                    "answer": []
                }

            # 🔹 2. Get payment history with methods
            histories = SaleHistory.objects.filter(
                sale=sale
            ).select_related(
                'created_by'
            ).prefetch_related(
                Prefetch(
                    'methods',
                    queryset=SalePaymentMethod.objects.all()
                )
            ).order_by('-date')

            # 🔹 3. Pagination
            paginator = Paginator(histories, per_page)
            page_obj = paginator.get_page(page)

            results = []

            for history in page_obj:
                methods_data = []

                for method in history.methods.all():
                    methods_data.append({
                        "method": method.method,
                        "amount": float(method.amount),
                        "date": method.date
                    })

                #here we will format the date for show in the frontend with the language and timezone of the user
                date=Plus.convert_from_utc(history.date, user.timezone)
                formatted_date = Plus.format_date_to_text(date.isoformat(), user.language, 1)

                results.append({
                    "id": history.id,
                    "cash_received": float(history.cash_received),
                    "change_given": float(history.change_given),
                    "date": formatted_date,
                    "old_amount_paid": float(history.old_amount_paid),
                    "old_balance": float(history.old_balance),
                    "new_amount_paid": float(history.new_amount_paid),
                    "new_balance": float(history.new_balance),
                    "fiscal_uuid": history.fiscal_uuid,
                    "fiscal_status": history.fiscal_status,
                    "created_by": history.created_by.id if history.created_by else None,
                    "created_by_name": history.created_by.username if history.created_by else None,
                    "payment_methods": methods_data
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
                "message": "",
                "error": str(e),
                "answer": []
            }
        
    #-------------------------this is for send the email of the sale with the cotization-------------------------

    @staticmethod
    def _send_email_thread(subject, html_content, recipient_list):
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body="Tu cliente de correo no soporta HTML.",
                from_email="noreply@denty.cloud",
                to=recipient_list,
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
        except Exception as e:
            print(f"Error enviando cotización: {e}")

    @classmethod
    def send_sale_email(cls, user, sale_id, to_email=None):
        try:
            sale = Sale.objects.select_related(
                'customer', 'company', 'branch'
            ).prefetch_related(
                'items',
                'payments'
            ).get(
                id=sale_id,
                branch=user.branch
            )

            # 1️⃣ Validar email
            recipient_email = to_email or (sale.customer.email if sale.customer else None)

            if not recipient_email:
                return {
                    "success": False,
                    "message": "El cliente no tiene email registrado",
                    "error": "EMAIL_EMPTY",
                    "answer": []
                }

            # 2️⃣ Recalcular totales en backend (seguridad)
            total = Decimal("0.00")
            subtotal = Decimal("0.00")
            tax_total = Decimal("0.00")

            for item in sale.items.all():
                subtotal += item.subtotal
                tax_total += item.tax_amount
                total += item.total

            payments = sale.payments.all().order_by('date')

            #get the link of the sale for pay online. If not exist we will create a new link for this sale
            link_pay_online_url=''
            link_pay_online=LinkPayOnline.objects.filter(sale=sale).first()
            if not link_pay_online: #if not exist a link for pay online we will create a new link for this sale
                link_pay_online=LinkPayOnline.objects.create(sale=sale)


            #now we will to see if the link of pay is valid 
            if link_pay_online.activate:
                #if the link is active we will to add the link in the email for pay online
                link_pay_online_url=f"{settings.PLUS_URL}/sales/pay_sale/{link_pay_online.key_link}"



            # 3️⃣ Contexto para template
            context = {
                "sale": sale,
                "items": sale.items.all(),
                "subtotal": subtotal,
                "tax_total": tax_total,
                "total": total,
                "branch": sale.branch,
                "company": sale.company,
                "payments": payments,
                "link_pay_online_url": link_pay_online_url
            }

            html_content = render_to_string(
                "sales/quotation_email.html",
                context
            )

            # 4️⃣ Lanzar envío asíncrono
            thread = threading.Thread(
                target=cls._send_email_thread,
                args=(
                    f"Cotización {sale.reference}",
                    html_content,
                    [recipient_email]
                )
            )
            thread.start()

            return {
                "success": True,
                "message": f"Cotización enviada a {recipient_email}",
                "error": "",
                "answer": {}
            }

        except Sale.DoesNotExist:
            return {
                "success": False,
                "message": "Venta no encontrada",
                "error": "SALE_NOT_FOUND",
                "answer": []
            }

        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": str(e),
                "answer": []
            }
        

    #-------------------------this is for the link of pay online-------------------------
    @classmethod
    def get_information_of_link_of_pay(cls, key_link):
        try:
            # Utilizamos select_related para llaves foráneas y prefetch_related para los items (reversa)
            link = LinkPayOnline.objects.select_related(
                'sale', 
                'sale__customer', 
                'sale__branch',
                'sale__company'
            ).prefetch_related(
                'sale__items'
            ).get(key_link=key_link, activate=True)
            
            sale = link.sale

            if not sale:
                return {"success": False, "error": "Sale not found", "answer": {}}
            
            #get the information of buy 
            data_bank={
                "bank_account":sale.company.bank_account if sale.company.bank_account else '',
                "bank_name":sale.company.bank_name if sale.company.bank_name else ''
            }
  

            # Estructuramos una respuesta rica en datos
            sale_data = {
                "id": sale.id,
                "reference": sale.reference,
                "total": float(sale.total),
                "subtotal": float(sale.subtotal),
                "tax_total": float(sale.tax_total),
                "discount_total": float(sale.discount_total),
                "amount_paid": float(sale.amount_paid),
                "balance": float(sale.balance), # Lo que falta por pagar
                "currency": sale.currency,
                "status": sale.status,
                "logo_url": sale.company.logo.url if sale.company and sale.company.logo else None,
                "customer_name": sale.customer.name if sale.customer else "Cliente General",
                "branch_name": sale.branch.name_branch if sale.branch else "",
                "data_bank":data_bank,
                # Mapeamos los items de la venta
                "items": [
                    {
                        "name": item.name,
                        "quantity": float(item.quantity),
                        "unit_price": float(item.unit_price),
                        "total": float(item.total)
                    } for item in sale.items.all()
                ]
            }

            return {
                "success": True,
                "answer": sale_data
            }

        except LinkPayOnline.DoesNotExist:
            return {"success": False, "error": "Link no encontrado o inactivo", "answer": {}}
        except Exception as e:
            return {"success": False, "error": str(e), "answer": {}}