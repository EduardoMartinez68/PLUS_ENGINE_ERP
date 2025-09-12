import base64
from django.core.files.base import ContentFile
from ..models import Customer, CustomerType, CustomerSource

def save_customer(user, form, user_admin=None, password_admin=None):
    """
    Creates a client associated with the user's company.
    `form` must be a dictionary containing the form fields.
    """
    try:
        # get the company and the branch of the user that would like add a customer
        company = user.company
        branch = user.branch

        # Create client instance
        customer = Customer()
        customer.company = company
        customer.branch = branch

        # Personal information
        customer.name = form.get("name", "")
        customer.email = form.get("email") or None
        customer.phone = form.get("phone") or None
        customer.cellphone = form.get("cellphone") or None
        customer.country = form.get("country", "MX")
        customer.address = form.get("address") or None
        customer.city = form.get("city") or None
        customer.state = form.get("state") or None
        customer.postal_code = form.get("postal_code") or None
        customer.num_ext = form.get("num_ext") or None
        customer.num_int = form.get("num_int") or None
        customer.reference = form.get("reference") or None
        customer.activated = form.get("activated") in ("on", True, "true", "True")

        # information of the company of the customer
        customer.this_customer_is_a_company = form.get("this_customer_is_a_company") in ("on", True, "true", "True")
        customer.company_name = form.get("company_name") or None
        customer.contact_name = form.get("contact_name") or None
        customer.contact_email = form.get("contact_email") or None
        customer.contact_phone = form.get("contact_phone") or None
        customer.contact_cellphone = form.get("contact_cellphone") or None
        customer.website = form.get("website") or None
        customer.note = form.get("note") or None

        # information of the customer in the company
        customer.points = form.get("points") or 0
        customer.credit = form.get("credit") or 0
        customer.tags = form.get("tags") or None
        customer.number_of_price_of_sale = form.get("number_of_price_of_sale") or 1 #forever the price be 1 for default

        # do a relation with CustomerType and CustomerSource
        type_id = form.get("customer_type")
        if type_id:
            try:
                customer.customer_type = CustomerType.objects.get(id=type_id)
            except CustomerType.DoesNotExist:
                customer.customer_type = None

        source_id = form.get("source")
        if source_id:
            try:
                customer.source = CustomerSource.objects.get(id=source_id)
            except CustomerSource.DoesNotExist:
                customer.source = None

        #here we will see if exist a image in base64
        avatar_data = form.get("avatar")
        if avatar_data:
            # fromat "data:image/png;base64,XXXX"
            if "," in avatar_data:
                fmt, imgstr = avatar_data.split(",", 1)
                ext = fmt.split("/")[1].split(";")[0]  # png, jpeg...
                customer.avatar.save(f"{customer.name}_avatar.{ext}", ContentFile(base64.b64decode(imgstr)), save=False)

        # save the customer
        customer.save()

        return {"success": True, "customer_id": customer.id}
    except Exception as e:
        return {"success": False, "error": str(e)}
