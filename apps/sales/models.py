from django.db import models
from decimal import Decimal
from core.models import Company, Branch, CustomUser
from apps.services.models import Pack

#-------------------------------------------------------------------------------------SETTINGS OF THE SALES---------------------------------------------
from apps.customers.models import Customer
class Sale(models.Model):
    id = models.BigAutoField(primary_key=True)
    name_sale = models.CharField(max_length=400, blank=True, null=True) 
    reference = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True,) #assigned to 

    creationDate = models.DateTimeField(auto_now_add=True) #this is when the sale be create
    startDate = models.DateTimeField(auto_now_add=True, null=True, blank=True) #this is when the customer accepted the treatment

    #this is the information of the sale. This information only be use for show information in the table of view home
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0) #this is for know when to buy the customer
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0) #this is acount balance the customer
    currency = models.CharField(
        max_length=3,
        default='MXN'
    )

    #this variable is for know when be buy this sale
    #this is use with help of the variable <startDate>
    payment_term_days = models.PositiveIntegerField(default=0) #7 days after, 15 days after, etc when is 0 is because the buy do this day
    expiration_date = models.DateTimeField(null=True) #this is for know if the <cotizacion> can expire. If the sale expire not can update nor use it


    #here we will see if the status of the treatment
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'), #this is when the user create the treatment
            ('accepted', 'accepted'), #this is when the customer accepted the treatment (this not not yet be use for facture the sale. This is a quote)
            ('paid', 'paid'), #this is when the customer accepted the treatment
            ('cancelled', 'cancelled'),
            ('expiration_date', 'expiration_date')
        ],
        default='pending'
    )
    note_cancelled=models.TextField(blank=True, null=True)

    #---------------this is for know the data fiscal of the sale in other country---------------
    #this be use for know the facture of the sale. In mexico we will use the method 'PUE' is the sale was did this day, else
    # if the sale was did in more of a buy, we will use the method 'PPD' 
    fiscal_uuid = models.CharField(max_length=100, null=True, blank=True)
    fiscal_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'),
            ('generated', 'generated'),
            ('error', 'error')
        ],
        default='pending'
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_created'
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            last_sale = Sale.objects.order_by('-id').first()
            next_id = 1 if not last_sale else last_sale.id + 1
            self.reference = f"SAL-{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.id} - {self.total}"
    

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    pack = models.ForeignKey(Pack, on_delete=models.SET_NULL, null=True)

    taxes = models.JSONField(default=list, blank=True) #here we will save the taxes of the item, this is for know the taxes of the item in the moment of the sale, because if we change the tax of the product, this not need to change in the sale
    name = models.CharField(max_length=255)  # name of the product/service/combo in this moment
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # price in this moment
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name
    

class SaleHistory(models.Model):
    sale = models.ForeignKey(
        Sale,
        related_name='payments',
        on_delete=models.CASCADE
    )    
    

    #-------------------------information of the buy--------------------
    cash_received = models.DecimalField(max_digits=12, decimal_places=2) #this is the money that the customer give
    change_given = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Change returned to the customer"
    ) #this is the change that the user give the customer
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    #-------------------------information of the Sale--------------------
    old_amount_paid = models.DecimalField(max_digits=12, decimal_places=2) #This is to find out how much I had before making this deposit
    old_balance = models.DecimalField(max_digits=12, decimal_places=2) #This is to find out how much I owed before making the deposit.

    new_amount_paid = models.DecimalField(max_digits=12, decimal_places=2) #This is to find out how much money I deposited after payment
    new_balance = models.DecimalField(max_digits=12, decimal_places=2) #This is to find out how much you owe now.

    #---------------this is for know the data fiscal of the sale in other country---------------
    fiscal_uuid = models.CharField(max_length=100, null=True, blank=True)
    fiscal_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'),
            ('generated', 'generated'),
            ('error', 'error')
        ],
        default='pending'
    )

    #who received the payment
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_history_created'
    )
    def __str__(self):
        return f"Payment {self.amount} for Sale {self.sale.id}"
    
class SalePaymentMethod(models.Model):
    #key fot filter after 
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    #this is for have a history of method of buy in the branch
    sale = models.ForeignKey(
        'Sale',
        related_name='payment_methods',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    payment = models.ForeignKey(
        SaleHistory,
        related_name='methods',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True,) #assigned to 

    PAYMENT_METHODS = [
        ('cash', 'cash'),
        ('card', 'card'),
        ('transfer', 'transfer'),
        ('change', 'change'), #this is for know that the user outside money. When be use this method, the <amount> need be negative.
    ]

    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

