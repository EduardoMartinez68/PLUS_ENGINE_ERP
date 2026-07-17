
from django import forms
from apps.customers.models import Customer
import re

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "sku", "name", "email", "phone", "cellphone",
            "country", "address", "city", "state",
            "postal_code", "num_ext", "num_int", "reference",
            "activated", "priority", "gender", "date_of_birth",

            "this_customer_is_a_company",
            "company_name", "contact_name",
            "contact_email", "contact_phone", "contact_cellphone",
            "website", "note",

            "points", "credit", "tags", "number_of_price_of_sale"
        ]

    # ---------- VALIDATIONS ----------
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and "@" not in email:
            raise forms.ValidationError("Correo electrónico inválido")
        return email

    def clean_cellphone(self):
        cellphone = self.cleaned_data.get("cellphone")
        if not cellphone:
            return cellphone
        
        cellphone = cellphone.replace(" ", "") #delete all the space in the cellphone

        # Pattern Explanation:
        # ^(\+\d{1,3})? -> Optional prefix (e.g., +52, +1)
        # \s? -> Optional space
        # \d{10} -> The 10 required digits
        # (?: -> Optional start of extension group
        # \s?(ext|x)\s? -> Space, 'ext' or 'x', and another space (optional)
        # \d+ -> Extension digits
        # )? -> The trailing question mark makes the entire group optional
        # $ -> End of string
        pattern = r"^(\+\d{1,3})?\s?\d{10}(?:\s?(ext|x)\s?\d+)?$"

        # We use `re.sub` to remove extra spaces if you want to normalize the data.
        # But for validation, `match` is sufficient.
        if not re.match(pattern, cellphone.strip(), re.IGNORECASE):
            raise forms.ValidationError(
                "Formato inválido. Ejemplos aceptados: 4443579030, +52 4443579030, 4443579030 ext 123"
            )

        return cellphone

    def clean_contact_email(self):
        email = self.cleaned_data.get("contact_email")
        if email and "@" not in email:
            raise forms.ValidationError("Correo de contacto inválido")
        return email

    def clean(self):
        """
        Validaciones cruzadas
        """
        cleaned = super().clean()

        if cleaned.get("this_customer_is_a_company"):
            if not cleaned.get("company_name"):
                raise forms.ValidationError(
                    "Si el cliente es una empresa, el nombre de la empresa es obligatorio"
                )

        return cleaned
    
    def points_validators(value):
        if value < 0:
            raise forms.ValidationError("Los puntos no pueden ser negativos")


class CustomerUpdateForm(CustomerForm):
    class Meta(CustomerForm.Meta):
        exclude = [
            "company",
            "creation_date",
            "avatar_updated_at",
            "avatar",
        ]