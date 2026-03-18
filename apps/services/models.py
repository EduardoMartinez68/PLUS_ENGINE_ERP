from django.db import models
from decimal import Decimal
from core.models import Company, Branch

# -------------------------------------------------
# INFORMATION OPTIONAL
# -------------------------------------------------
class ProductCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="id_company_category_product", null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activated = models.BooleanField(default=True)
    

    class Meta:
        db_table = "services_product_category"
        indexes = [
            models.Index(fields=["name"], name="idx_category_name"),
            models.Index(fields=["company"], name="idx_category_company"),
        ]

    def __str__(self):
        return self.name
    
class ProductDepartment(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="id_company_departament_product", null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = "services_product_department"
        indexes = [
            models.Index(fields=["name"], name="idx_department_name"),
            models.Index(fields=["company"], name="idx_department_company"),
        ]

    def __str__(self):
        return self.name

# -------------------------------------------------
# Pack o combo de productos/servicios
# -------------------------------------------------
class Pack(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="id_company_pack", null=True, blank=True)

    # Basic information
    image1 = models.ImageField(upload_to="products/", blank=True, null=True)
    image2 = models.ImageField(upload_to="products/", blank=True, null=True)
    image3 = models.ImageField(upload_to="products/", blank=True, null=True)
    image4 = models.ImageField(upload_to="products/", blank=True, null=True)

    skus = models.JSONField(blank=True, null=False, default=list) #this is for search the product for multi keys
    name = models.CharField(max_length=255,  null=False)
    description = models.TextField(blank=True, null=True)

    # Additional information
    activated = models.BooleanField(default=True)  
    tags = models.JSONField(blank=True, null=True) 
    note = models.TextField(blank=True, null=True)

    #this is because need 
    PACK_TYPE_CHOICES = [
        (0, 'product'),
        (1, 'service'),
        (2, 'pack/combo')
    ]
    pack_type = models.IntegerField(choices=PACK_TYPE_CHOICES, default=1, help_text="Tipo de pack") #0--product, 1--service, 2--pack (combo)

    # --------------Additional information (optional)--------------
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
        related_name="services"
    )

    # date of creation or update
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_packs"
        indexes = [
            models.Index(fields=["name"], name="idx_pack_name"),
            models.Index(fields=["skus"], name="idx_pack_sku"),
            models.Index(fields=["company"], name="idx_pack_id_company"),
            models.Index(fields=["activated"], name="idx_pack_activated"),
        ]

    # -------------------------------------------------
    # Método para calcular precio con impuestos dinámicamente
    # -------------------------------------------------
    def calculate_price_with_taxes(self):
        total_tax_rate = Decimal('0')

        taxes = self.pack.taxes.select_related('tax').filter(
            tax__activated=True
        )

        for tax_rel in taxes:
            total_tax_rate += tax_rel.tax.rate

        total = self.base_price + (self.base_price * total_tax_rate / Decimal('100'))
        return round(total, 2)

    def __str__(self):
        return f"{self.name}"

class BranchPack(models.Model):
    id = models.BigAutoField(primary_key=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name="branch_prices")

    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_with_taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    activated = models.BooleanField(default=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services_branch_pack"
        unique_together = ("branch", "pack")
        indexes = [
            models.Index(fields=["company", "branch"]),
            models.Index(fields=["company", "pack"])
        ]


# -------------------------------------------------
# Relación Pack <-> Tax
# -------------------------------------------------
class Tax(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="id_company_tax")

    name = models.CharField(max_length=255)  # ej: "IVA", "Impuesto local"
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje del impuesto, ej: 16 para 16%")
    description = models.TextField(blank=True, null=True)
    

    # settings
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = "services_tax"
        indexes = [
            models.Index(fields=["name"], name="idx_tax_name")
        ]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

class PackTax(models.Model):
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name="taxes")
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name="packs")

    class Meta:
        db_table = "services_pack_tax"
        unique_together = ("pack", "tax")

    def __str__(self):
        return f"{self.pack.name} -> {self.tax.name}"
    #here you can create the body of the database 

