from django.db import models

# -------------------------------------------------
# Modelo para las unidades de medida
# Ej: kg, litro, pieza, hora, servicio, etc.
# -------------------------------------------------
class UnitOfMeasure(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)  # ej: "kg", "pieza", "hora"
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "products.unit_of_measure"
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"

    def __str__(self):
        return self.name

class Presentation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, help_text="Nombre de la presentación, ej: Cápsula, Tableta, Jarabe, Porción, Botella 500ml")
    description = models.TextField(blank=True, null=True, help_text="Opcional, detalles adicionales")
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.SET_NULL, null=True, blank=True, help_text="Unidad base de la presentación, ej: ml, g, pieza")
    
    class Meta:
        db_table = "products.presentation"
        indexes = [
            models.Index(fields=["name"], name="idx_presentation_name"),
        ]

    def __str__(self):
        return self.name
    
# -------------------------------------------------
# Tabla de impuestos
# -------------------------------------------------
class Tax(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)  # ej: "IVA", "Impuesto local"
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje del impuesto, ej: 16 para 16%")
    description = models.TextField(blank=True, null=True)
    activated = models.BooleanField(default=True)

    # Empresa/negocio
    id_company = models.BigIntegerField(blank=True, null=True)  # opcional si es multiempresa

    # Fechas
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products.tax"
        indexes = [
            models.Index(fields=["name"], name="idx_tax_name"),
            models.Index(fields=["id_company"], name="idx_tax_company"),
        ]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class ProductCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activated = models.BooleanField(default=True)
    id_company = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "products.product_category"
        indexes = [
            models.Index(fields=["name"], name="idx_category_name"),
            models.Index(fields=["id_company"], name="idx_category_company"),
        ]

    def __str__(self):
        return self.name
    
    
class ProductDepartment(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activated = models.BooleanField(default=True)
    id_company = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "products.product_department"
        indexes = [
            models.Index(fields=["name"], name="idx_department_name"),
            models.Index(fields=["id_company"], name="idx_department_company"),
        ]

    def __str__(self):
        return self.name
    
# -------------------------------------------------
# Modelo de productos/servicios genérico, supplies
# -------------------------------------------------
class Product(models.Model):
    # Basic information
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=False, unique=True)
    name = models.CharField(max_length=255,  null=False)
    description = models.TextField(blank=True, null=True)
    
    # cost of buy
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # product/service cost

    #inventory
    this_product_use_inventory=models.BooleanField(default=True, null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        help_text="Presentación del producto"
    )

    min = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    max = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    #this is if the product have batch added, for that automatically PLUS discount of batch most about to expire and that the user no do this manually
    #this input only can show in the frontend when this product have batches
    this_product_discounts_batches_automatically=models.BooleanField(default=True, null=False)

    # Additional information
    department = models.ForeignKey(
        ProductDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories"
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    activated = models.BooleanField(default=True)
    id_company = models.BigIntegerField(blank=True, null=True)  # ForeignKey Company

    #date of creation or update
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products.product"
        indexes = [
            models.Index(fields=["name"], name="idx_product_name"),
            models.Index(fields=["sku"], name="idx_product_sku"),
            models.Index(fields=["id_company"], name="idx_product_id_company"),
            models.Index(fields=["activated"], name="idx_product_activated"),
        ]

    def __str__(self):
        return f"{self.barcode} ({self.name})"



# -------------------------------------------------
# Pack o combo de productos/servicios
# -------------------------------------------------
class Pack(models.Model):
    id = models.BigAutoField(primary_key=True)

    # Basic information
    image1 = models.ImageField(upload_to="products/", blank=True, null=True)
    image2 = models.ImageField(upload_to="products/", blank=True, null=True)
    image3 = models.ImageField(upload_to="products/", blank=True, null=True)
    image4 = models.ImageField(upload_to="products/", blank=True, null=True)

    skus = models.JSONField(blank=True, null=False, default=list) #this is for search the product for multi keys
    alternate_skus = models.JSONField(blank=True, null=True, default=list, help_text="Alternative codes or keywords")
    name = models.CharField(max_length=255,  null=False)
    description = models.TextField(blank=True, null=True)
    
    # Prices and costs
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_with_taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Additional information
    activated = models.BooleanField(default=True)  
    tags = models.JSONField(blank=True, null=True) 
    note = models.TextField(blank=True, null=True)

    # date of creation or update
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    #this is because need 
    PACK_TYPE_CHOICES = [
        (0, 'product'),
        (1, 'service'),
        (2, 'pack/combo')
    ]
    pack_type = models.IntegerField(choices=PACK_TYPE_CHOICES, default=1, help_text="Tipo de pack") #0--product, 1--service, 2--pack (combo)

    id_company = models.BigIntegerField(blank=True, null=False) 

    class Meta:
        db_table = "products.packs"
        indexes = [
            models.Index(fields=["name"], name="idx_pack_name"),
            models.Index(fields=["skus"], name="idx_pack_sku"),
            models.Index(fields=["id_company"], name="idx_pack_id_company"),
            models.Index(fields=["activated"], name="idx_pack_activated"),
        ]

    # -------------------------------------------------
    # Método para calcular precio con impuestos dinámicamente
    # -------------------------------------------------
    def calculate_price_with_taxes(self):
        total = self.base_price
        for tax in self.taxes.filter(activated=True):
            total += total * (tax.rate / 100)
        return round(total, 2)
    

    def __str__(self):
        return f"{self.name}"


# -------------------------------------------------
# Relación Pack <-> Tax
# -------------------------------------------------
class PackTax(models.Model):
    pack = models.ForeignKey('Pack', on_delete=models.CASCADE, related_name="taxes")
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name="packs")

    class Meta:
        db_table = "products.pack_tax"
        unique_together = ("pack", "tax")

    def __str__(self):
        return f"{self.pack.name} -> {self.tax.name}"
    


# -------------------------------------------------
# Relación de productos dentro de un Pack
# Permite controlar cantidad y merma
# -------------------------------------------------
'''
    Esto puede servir si tengo una boutique, o un restaurante.
    Si en el <PackItem> existen mas de 1 item, se puede desplegar todos los items que no son obligatorios
    (vestidos o diferentes tipos de refrescos) y el usuario podra seleccionar el que necesite
'''
class PackItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="in_packs")

    #Quantity of product required for 1 unit of the pack
    quantity_min = models.DecimalField(max_digits=10, decimal_places=2, default=1) 
    quantity_max = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    #Percentage of spoilage or loss during preparation (this is for restaurants)
    wastage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # example: 5% wastage

    #Optional features and extra price
    #(this is for restaurants that need add a supplies to his combo with a extra price)
    required = models.BooleanField(default=True)  # True = obligatory, False = optional

    # If it is optional, there will be an additional charge. 
    #example the max of this item is 1, but the customer need 3, and have a extra price of 1$ dollar, this means that the two item extra have a cost of 2$ dollars
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    needs_prescription = models.BooleanField(default=False) #this is for know if the product need a prescription of the doctor
    show_this_item_in_the_ticket = models.BooleanField(default=False) #this is for when need print the ticket, can show or not the information of the item

    class Meta:
        db_table = "products.pack_item"
        unique_together = ("pack", "product")  # a product cannot be included more than once in the same pack

    def __str__(self):
        tipo = "Obligatory" if self.required else f"Optional (+{self.extra_price})"
        return f"{self.product.name} en {self.pack.name} ({tipo}, {self.quantity} {self.product.unit})"




# -------------------------------------------------
# Lotes de productos (para caducidad, control de inventario)
# -------------------------------------------------
class ProductBatch(models.Model):
    # identifier of the lote
    id = models.BigAutoField(primary_key=True)
    batch_code = models.CharField(max_length=100, blank=True, null=True)  #optional

    #character of the batch
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    manufacture_date = models.DateField(blank=True, null=True) #this is the date that send the manufacture
    expiry_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    #information of the company
    id_company = models.BigIntegerField(blank=True, null=True)  # equal that Product
    activated = models.BooleanField(default=True)
    
    class Meta:
        db_table = "products.product_batch"
        indexes = [
            models.Index(fields=["product"], name="idx_batch_product"),
            models.Index(fields=["batch_code"], name="idx_batch_code"),
            models.Index(fields=["expiry_date"], name="idx_batch_expiry"),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Lote: {self.batch_code or 'Sin código'} ({self.quantity} {self.product.unit})"




#-----------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------
# Modelo de promociones/ofertas
# -------------------------------------------------
class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto fijo'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    #Discount type
    promo_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')

    # Vigencia
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)  # If it is null, it applies indefinitely.

    # Days of the week and times (optional)
    days_of_week = models.JSONField(blank=True, null=True)  # ej: ["Mon","Tue","Wed"]
    start_hour = models.TimeField(blank=True, null=True)     # hora inicio
    end_hour = models.TimeField(blank=True, null=True)       # hora fin

    # Applicable products and packages
    packs = models.ManyToManyField('products.Pack', blank=True, related_name='promotions')

    # Company/business
    id_company = models.BigIntegerField(blank=True, null=True)

    # Activation
    activated = models.BooleanField(default=True)

    # dates of creatiuon and update
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products.promotion"
        indexes = [
            models.Index(fields=["name"], name="idx_promotion_name"),
            models.Index(fields=["start_date", "end_date"], name="idx_promotion_date"),
            models.Index(fields=["id_company"], name="idx_promotion_company"),
        ]

    def __str__(self):
        return f"{self.name} ({self.promo_type})"

# -------------------------------------------------
# Rangos de cantidad para promociones (bulk discounts)
# -------------------------------------------------
class PromotionQuantityTier(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="quantity_tiers")
    min_quantity = models.PositiveIntegerField()  # minimum quantity to apply
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # percentage or fixed amount depending on promo_type

    class Meta:
        db_table = "products.promotion_quantity_tier"
        ordering = ["min_quantity"]

    def __str__(self):
        return f"{self.min_quantity}+ -> {self.discount_value}"
