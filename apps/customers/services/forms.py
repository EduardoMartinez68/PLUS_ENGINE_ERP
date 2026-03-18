
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
            "activated", "priority", "gender",

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
        if cellphone and not re.match(r"^\d{10}$", cellphone):
            raise forms.ValidationError("El celular debe tener 10 dígitos")
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


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = [
            "company",
            "created_at",
            "updated_at",
            "avatar",
        ]