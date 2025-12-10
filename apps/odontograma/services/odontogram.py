from django.core.exceptions import ObjectDoesNotExist, ValidationError
from typing import Dict, Any, List
from apps.customers.models import Customer
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
import uuid
from ..models import Odontogram, HistoryOdontogram, Tooth, OdontogramSetting
from django.db.models import Q
from ..plus_wrapper import Plus

def get_odontogram_father(odontogram) -> 'Odontogram':
    """
    Return the odontogram father of the history:
    
    - If exist very much data with is_father=True → get the more new and update all the others.
    - If not exist nothing with is_father=True → now get the more new and update his status as father.
    - Forever return a HistoryOdontogram success.
    """

    queryset = HistoryOdontogram.objects.filter(
        customer=odontogram.customer
    ).order_by("-created_at")

    if not queryset.exists():
        return None  # Not exist a odontogram

    with transaction.atomic():
        # 1️⃣ Search all the data that have the status is_father = True
        fathers = queryset.filter(is_father=True).order_by("-created_at")

        if fathers.exists():

            # Official father = newest among the fathers
            official_father = fathers.first()

            # 2️⃣ If there is more than one father, we correct
            extra_fathers = fathers.exclude(id=official_father.id)
            if extra_fathers.exists():
                extra_fathers.update(is_father=False)

            return official_father

        else:
            # 3️⃣ There is no father: choose the most recent one
            newest = queryset.first()
            newest.is_father = True
            newest.save(update_fields=["is_father"])
            return newest

def get_or_create_odontogram(customer, doctor) -> 'Odontogram':
    """
    Obtiene o crea un odontograma para un paciente.
    Si no existe, lo crea automáticamente.
    """
    company = customer.company
    branch = customer.branch  # se asume que el cliente pertenece a una sucursal

    odontogram, created = Odontogram.objects.get_or_create(
        company=company,
        customer=customer,
        defaults={
            "branch": branch,
            "doctor": doctor,
        }
    )

    return odontogram

def get_odontograms(user, sku: str = '', page: int = 1, limit: int = 20) -> Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "odontograma.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    doctor = user

    #if exist a sku in the weeker
    if sku:
        qs = Customer.objects.filter(
            company=company
        )
 
        sku = sku.lower()
        qs = [c for c in qs if (
            (c.sku and sku in c.sku.lower()) or
            (c.name and sku in c.name.lower()) or
            (c.email and sku in c.email.lower()) or
            (c.phone and sku in c.phone.lower()) or
            (c.cellphone and sku in c.cellphone.lower())
        )]
        qs = qs[:20]
        customers=qs
    else:
        # if not exist a sku we get the first 20 odontograms
        customers = Customer.objects.filter(
            company=company,
            odontogram__doctor=doctor
        ).distinct()[:limit]

    results = []
    for c in customers:
        # Obtain or create the patient's odontogram 
        odontogram = get_or_create_odontogram(c, doctor)

        results.append({
            "sku": c.sku,
            "name": c.name,
            "email": c.email,
            "cellphone": c.cellphone,
            "gender": c.gender,
            "date_of_birth": c.date_of_birth,
            "avatar": c.avatar.url if c.avatar else None,

            "odontogram_id": odontogram.id,
            "odontogram_doctor": getattr(odontogram.doctor, "name", ""),
            "odontogram_svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#f5f5f5"/><circle cx="50" cy="50" r="30" fill="#e0e0e0"/></svg>',
            "odontogram_created_at": Plus.format_date_to_text(
                        Plus.convert_from_utc(odontogram.created_at, user.timezone),
                        user.language,
                        2
                    ),
        })

    # Manual pagination
    paginator = Paginator(results, limit)
    page_obj = paginator.get_page(page)

    return {
        "success": True,
        "message": "odontograma.message.success.found",
        "answer": results,

        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_results": paginator.count,
        "results": list(page_obj)
    }

def get_information_odontograms(user, sku: str='', page:int=1, limit:int=20)->Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "odontograma.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    if not sku:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-sku-provided",
            "error": "Customer SKU is required"
        }
    

    #here we will to try get the customer
    try:
        customer = Customer.objects.select_related("company", "branch").get(
            sku=sku, company=company
        )
    except Customer.DoesNotExist:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-customer-found",
            "error": f"No customer found with SKU '{sku}' for this company"
        }

    #when get the customer now we will to get his odontogram
    odontogram = (
        Odontogram.objects.filter(company=company, customer=customer)
        .select_related("doctor", "branch")
        .prefetch_related("odontograms")  # por si se usa related_name en HistoryOdontogram
        .first()
    )


    #if the customer not have a odontograma, we will to create 
    if not odontogram:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-odontogram-found",
            "error": f"No odontogram found for customer {customer.name}"
        }
    

    #return the struct 
    return {
        "success": True,
        "answer": "odontograma.message.success.found",
        "data": {
            "customer": {
                "sku": customer.sku,
                "name": customer.name,
                "email": customer.email,
                "cellphone": customer.cellphone,
                "gender": customer.gender,
                "date_of_birth": customer.date_of_birth,
                "avatar": customer.avatar.url if customer.avatar else None,
                "company": customer.company.name if customer.company else None,

                "odontogram_id": odontogram.id,
                "odontogram_doctor": getattr(odontogram.doctor, "name", ''),
                "odontogram_id": odontogram.id,
                "odontogram_created_at": odontogram.created_at,
            },
        }
    }


def add_new_odontogram(user, data)-> Dict[str, Any]:
    """
    Make a new odontogram for a patient.

    Args:
        user (CustomUser): he is the doctor that be create the odontogram.
        data (dict): This dictionary have:
            - 'customer_id': ID of the customer
            - 'history_name': Name or key of the first history
            - 'is_kid': bool for know if the odontogram is for a kid o an adult

    Returns:
        dict: Information from the created odontogram, including generated IDs.
    """


    # ------------------ Valid the form ------------------
    required_fields = ['customer_id',  'history_name']
    for field in required_fields:
        if field not in data:
            return {
                "success": False,
                "message": "odontograma.error.need-all-the-data",
                "error": f"The input '{field}' is requerid."
            }

    customer_id = data['customer_id']
    history_name = data['history_name']
    is_kid = Plus.to_bool(data.get('is_kid', False))

    #get all the models that need the odontogram
    customer = Customer.objects.get(id=customer_id)
    doctor = user
    company = doctor.company
    branch = doctor.branch


    #first we will see if the odontogram already exist in the company
    existing = Odontogram.objects.filter(
        company=company,
        customer=customer
    )

    if existing.exists():
        return {
            "success": False,
            "message": "odontograma.error.already-exist",
            "error": f"This patient already a odontogram in this company"
        }

    try:
        # ------------------ CREACIÓN DENTRO DE TRANSACCIÓN ------------------
        with transaction.atomic():
            #here we will to create the odontogram root
            odontogram = Odontogram.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                doctor=doctor,
            )

            # create the first history of the odontogram
            history = HistoryOdontogram.objects.create(
                customer=customer,
                is_kid=is_kid,
                key=history_name,
                notes=f"Odontogram create by {user.name or user.username}"
            )

            # Determine which teeth to create
            # Adult: 11–48 | Kid: 51–85
            teeth_range = []
            if not is_kid:
                teeth_range = [n for n in range(11, 19)] + [n for n in range(21, 29)] + \
                            [n for n in range(31, 39)] + [n for n in range(41, 49)]
            else:
                teeth_range = [n for n in range(51, 56)] + [n for n in range(61, 66)] + \
                            [n for n in range(71, 76)] + [n for n in range(81, 86)]

            # Create the tooth
            tooth_objects = [
                Tooth(
                    historyodontogram=history,
                    FDI_number=num,
                    name_key=dict(Tooth.FDI_TEETH).get(num, ""),
                    status="healthy"
                )
                for num in teeth_range
            ]
            Tooth.objects.bulk_create(tooth_objects)



        # ------------------ RETURN ------------------
        return {
            "success": True,
            "odontogram_id": odontogram.id,
            "history_id": history.id,
            "total_teeth_created": len(teeth_range),
            "is_kid": is_kid
        }



    except IntegrityError as e:
        return {
            "success": False,
            "message": "odontograma.error.integrity-error",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": "odontograma.error.unexpected",
            "error": str(e)
        }

def get_latest_history_for_odontogram(user, odontogram_id: int) -> Dict[str, Any]:
    """
    Obtiene el historial más reciente de un odontograma con todos sus dientes.

    Args:
        odontogram_id (int): ID del Odontogram.

    Returns:
        Dict[str, Any]: Diccionario con la información del historial más reciente y sus dientes.
                        Retorna {} si no existe.
    """
    result: Dict[str, Any] = {}

    try:
        odontogram = Odontogram.objects.get(id=odontogram_id, doctor=user)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "message": "odontograma.error.not-exist",
            "answer": {},
            "error": "This odontogram does not exist or you don't have permission"
        }
    
    #get the settings of the odontogram 
    try:
        setting_obj = OdontogramSetting.objects.get(doctor=user)
        setting_odontogram = {
            "typeSystem": setting_obj.typeSystem,
            "color_caries": setting_obj.color_caries,
            "default_treatments": setting_obj.default_treatments
        }
    except OdontogramSetting.DoesNotExist:
        setting_odontogram = {
            "typeSystem": 1,
            "color_caries": "#FF0000",
            "default_treatments": {}
        }

    # Obtener el historial más reciente para este paciente
    latest_history = get_odontogram_father(odontogram)

    if not latest_history:
        return result

    customer = odontogram.customer

    # Obtener todos los dientes asociados al historial
    teeth_qs = latest_history.teeth.all().order_by('FDI_number')
    teeth_data = [
        {
            "id": t.id,
            "FDI_number": t.FDI_number,
            "name_key": t.name_key,
            "status": t.status,
            
            "svg_state": t.svg_state,
            "surfaces":t.surfaces,

            "caries_depth": t.caries_depth,
            "has_tartar":t.has_tartar,
            "status_gum":t.status_gum,
            "mobility":t.mobility,

            "diagnosis":t.diagnosis or '',
            "treatments":t.treatments or '',
            "notes":t.notes or '',
            "last_checkup":t.last_checkup
        }
        for t in teeth_qs
    ]

    # Construir el resultado
    result = {
        "success":True,
        "answer":{
            "history_id": latest_history.id,
            "customer_id": latest_history.customer.id,
            "key": latest_history.key,
            "notes": latest_history.notes,
            "created_at": latest_history.created_at,
            "updated_at": latest_history.updated_at,
            "blocked": latest_history.blocked,
            "periodontograma": latest_history.periodontograma,
            "is_kid":latest_history.is_kid,
            "teeth": teeth_data,
            "setting_odontogram":setting_odontogram,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "avatar": customer.avatar.url if customer.avatar else None,
            }
        }
    }

    return result

def get_history_odontograms(user, odontogram_id, key=None, page=1):
    """
    get the history of the  HistoryOdontogram related to the given odontogram.
    - if get `key`, filter for partial match.
    - if not get `key`, bring the most recent.
    - Uses pagination and returns only 20 per page.
    """

    try:
        odontogram = Odontogram.objects.get(id=odontogram_id)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "error": "Odontograma no encontrado."
        }

    #get the history of the patient
    queryset = HistoryOdontogram.objects.filter(
        customer=odontogram.customer
    ).order_by("-created_at")

    get_odontogram_father(odontogram)
    #if exist a key now we will to filter
    if key:
        queryset = queryset.filter(key__icontains=key)

    #pagination for 20 items per page
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(page)

    # convert to list of dicts
    history_list = [
        {
            "id": h.id,
            "key": h.key,
            "is_kid": h.is_kid,
            "is_father": h.is_father,
            "notes": h.notes,
            "created_at": Plus.format_date_to_text(
                        Plus.convert_from_utc(h.created_at, user.timezone),
                        user.language,
                        1
                    ),
            "updated_at": Plus.format_date_to_text(
                        Plus.convert_from_utc(h.updated_at, user.timezone),
                        user.language,
                        1
                    ),
            "blocked": h.blocked,
        }
        for h in page_obj.object_list
    ]

    return {
        "success": True,
        "total_histories": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "answer": history_list
    }



def create_odontogram_history_service(user, odontogram_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new history of the odontogram.
    Allows copying data from the most recent history (if applicable).
    
    Params:
        - user: The doctor that is creating the history
        - odontogram_id: ID of the odontogram of the patient
        - data: Dict with:
            - key: str
            - notes: str
            - periodontograma: dict
            - is_kid: bool
            - copy: bool  (if the doctor would like copy the data from the last history)
    
    Important rules:
        - Yes `copy=True` only if the history is changing of kid-> adult or adult-> kid, NO copy is made.
        - Yes `copy=False`, always new teeth are created.
        - Yes no previous history, the copy is ignored and new teeth are created.
    """

    try:
        odontogram = Odontogram.objects.get(id=odontogram_id)
    except Odontogram.DoesNotExist:
        return {"success": False, "message":"odontogram.error.this-odontogram-not-exist", "error": "Odontograma not exist."}


    #get the data from the form that send the doctor
    key = data.get("key_odontogram")
    notes = data.get("notes", "")
    is_kid = data.get("is_kid", False)
    periodontograma = data.get("periodontograma", {})
    copy = Plus.to_bool(data.get("is_copy", False))


    #eval the paramt that be needed
    if not key:
        return {"success": False, "message":"odontogram.error.this-key-of-the-odontogram-is-requerid", "error": "The 'key' is obligatory."}

    #get the last history (the father)
    last_history = get_odontogram_father(odontogram)

    #here we will see if we can coppy the data of the last history
    can_copy = False
    if copy and last_history:
        if last_history.is_kid == is_kid:
            # Only we can copy the data of both be kids or if both be adults
            can_copy = True

    # START THE TRANSACTION
    with transaction.atomic():

        # create the new history
        new_history = HistoryOdontogram.objects.create(
            customer=odontogram.customer,
            is_kid=is_kid,
            key=key,
            notes=notes,
            periodontograma=periodontograma,
            blocked=False
        )

        # ----------------------------------------------------------
        # COPY ALL THE DATA OF THE HISTORY FATHER
        # ----------------------------------------------------------
        if can_copy:
            parent_teeth = Tooth.objects.filter(historyodontogram=last_history)

            for t in parent_teeth:
                Tooth.objects.create(
                    historyodontogram=new_history,
                    FDI_number=t.FDI_number,
                    name_key=t.name_key,
                    status=t.status,
                    surfaces=t.surfaces,
                    caries_depth=t.caries_depth,
                    has_tartar=t.has_tartar,
                    status_gum=t.status_gum,
                    mobility=t.mobility,
                    diagnosis=t.diagnosis,
                    notes=t.notes,
                    treatments=t.treatments,
                    svg_state=t.svg_state,
                    last_checkup=t.last_checkup,
                    last_updated_by=user
                )

        # ----------------------------------------------------------
        # IF THE TOOTHS NOT CAN BE COPPIED, CREATE NEW TEETH
        # ----------------------------------------------------------
        else:
            # Selección del set de dientes según niño / adulto
            from ..models import Tooth as ToothModel

            all_teeth = (
                ToothModel.FDI_TEETH[:32] if not is_kid else ToothModel.FDI_TEETH[32:]
            )

            for FDI_number, key_name in all_teeth:
                Tooth.objects.create(
                    historyodontogram=new_history,
                    FDI_number=FDI_number,
                    name_key=key_name,
                    last_updated_by=user
                )

    # FINISH OF THE TRANSACTION
    return {
        "success": True,
        "history_id": new_history.id,
        "message": "Historial creado correctamente.",
        "copied": can_copy
    }


def set_new_father_odontogram(user, history_id: int) -> Dict[str, Any]:
    """
    Sets the given HistoryOdontogram as the new father.
    Steps:
    1. Check permissions and company/branch match.
    2. Turn off all other fathers.
    3. Set this one as the new father.
    """

    try:
        new_father = HistoryOdontogram.objects.select_related("customer").get(id=history_id)
    except ObjectDoesNotExist:
        return {
            "success": False,
            "message": "odontogram.error.this-odontogram-not-exist",
            "error":"This odontogram not exist"
        }

    # ---- VALIDATE THE USER HAS ACCESS TO THIS PATIENT ----
    # Obtiene el odontograma "principal" del paciente (solo para validar la compañía)
    try:
        odontogram = Odontogram.objects.get(customer=new_father.customer)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "message": "odontogram.error.this-odontogram-not-is-valid",
            "error":"This odontogram not is in the history of the odontogram"
        }

    # Validamos que el usuario esté editando dentro de la misma compañía/branch
    if odontogram.company != user.company:
        return {
            "success": False,
            "message": "message.this-user-not-have-this-permission",
            "error":"This odontogram not be in this company"
        }

    # ---- UPDATE FATHER FLAGS ----
    with transaction.atomic():
        # Quitar padre a todos los historiales del mismo paciente
        HistoryOdontogram.objects.filter(
            customer=new_father.customer,
            is_father=True
        ).update(is_father=False)

        # Asignar padre al actual
        new_father.is_father = True
        new_father.save(update_fields=["is_father", "updated_at"])

    return {
        "success": True,
        "message": "odontogram.success.odontogram-father-update",
        "error":"This odontogram was update like father"
    }



def delete_odontogram(user, data) -> Dict[str, Any]:
    odontogram_id = data.get("odontogram_id")

    if not odontogram_id:
        return {
            "success": False,
            "message": "odontogram.error.no-id-provided",
            "error": "You need to provide the id of the odontogram."
        }

    # ---- 1. VALIDATE ODONTOGRAM EXISTENCE ----
    try:
        odontogram = Odontogram.objects.select_related("customer").get(id=odontogram_id)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "message": "odontogram.error.not-found",
            "error": "This odontogram does not exist."
        }

    # ---- 2. SECURITY: validate company ----
    if odontogram.company != user.company:
        return {
            "success": False,
            "message": "message.this-user-not-have-this-permission",
            "error": "You cannot delete odontograms of another company."
        }

    # ---- 3. GET ALL RELATED HISTORY ODONTOGRAMS ----
    histories = list(
        HistoryOdontogram.objects.filter(customer=odontogram.customer)
    )

    if len(histories) == 0:
        # shouldn't happen but safe-case
        odontogram.delete()
        return {
            "success": True,
            "message": "odontogram.success.deleted-empty",
            "error": "Odontogram removed (no histories found)."
        }

    # ---- 4. START ATOMIC OPERATION ----
    with transaction.atomic():

        # If there are multiple histories: delete only the parent
        if len(histories) > 1:
            # Find the father
            father = None
            for h in histories:
                if h.is_father:
                    father = h
                    break

            if not father:
                # Safety: if something weird happens, take the newest as father
                father = histories[0]

            # Delete teeth of father
            father.teeth.all().delete()

            # Delete father history
            father.delete()

            # Now assign new father = newest (first in ordering by created_at desc)
            remaining_histories = HistoryOdontogram.objects.filter(customer=odontogram.customer)

            new_father = remaining_histories.order_by("-created_at").first()
            new_father.is_father = True
            new_father.save(update_fields=["is_father", "updated_at"])

            return {
                "success": True,
                "message": "odontogram.success.history-father-replaced",
                "error": "Father history deleted and replaced by newest one."
            }

        # ---- ONLY ONE HISTORY EXISTS: DELETE EVERYTHING ----
        else:
            only_history = histories[0]

            # Delete teeth of unique history
            only_history.teeth.all().delete()

            # Delete the only history
            only_history.delete()

            # Delete odontogram files
            odontogram.odontogram_files.all().delete()

            # Delete odontogram
            odontogram.delete()

            return {
                "success": True,
                "message": "",
                "error": "",
                "last_record":True
            }
#-------------------------------------------update tooth in the odontogram-------------------------------------------------
def tooth_belongs_to_doctor_odontogram(tooth_id:int, odontogram_id:int, user)->bool:
    """
    In this function we will see if the tooth exist in the odontogram that the doctor would like update

    Args:
        tooth_id (int): ID of the tooth.
        odontogram_id (int): ID of the odontogram.
        user (CustomUser): User (doctor) that would like update the tooth.

    Returns:
        bool: True if the tooth is in the odontogram.
    """
    try:
        # get the tooth
        tooth = Tooth.objects.select_related('historyodontogram').get(id=tooth_id)
        history = tooth.historyodontogram

        # get the ofontogram
        odontogram = Odontogram.objects.select_related('doctor', 'customer').get(id=odontogram_id)

        # We check if the tooth belongs to the same patient (customer)
        # and the odontogram belongs to the same doctor
        if odontogram.doctor == user and odontogram.customer == history.customer:
            return True
        else:
            return False

    except ObjectDoesNotExist:
        return False

    except Exception as e:
        # if exist a error we will to return False for default
        return False
    
def update_tooth(tooth_id: int, odontogram_id:int, data:Dict, user) -> Dict[str, Any]:
    """
    Update the information of a tooth with help of his ID.

    Args:
        tooth_id (int): ID of the tooth.
        data (dict): information that send the form.
        user (CustomUser): this is the user that do the update.

    Returns:
        dict: Diccionario con el resultado del proceso.
    """
    #first we will see if the tooth exist in the odontogram 
    if not tooth_belongs_to_doctor_odontogram(tooth_id, odontogram_id, user):
        return {
            "success": True,
            "message": "odontograma.error.this-tooth-not-exist-in-the-odontogram",
            "error": None
        }
    
    try:
        # We initiated a transaction to ensure integrity.
        with transaction.atomic():
            try:
                tooth = Tooth.objects.get(id=tooth_id)
            except ObjectDoesNotExist:
                return {
                    "success": False,
                    "message": "odontograma.error.tooth_not_found",
                    "error": f"No se encontró el diente con ID {tooth_id}."
                }

            # update the input of the model
            allowed_fields = [
                "status", "surfaces", "caries_depth",
                "status_gum", "mobility", "diagnosis", "notes",
                "treatments", "svg_state", "last_checkup"
            ]

            for field, value in data.items():
                if field in allowed_fields:
                    setattr(tooth, field, value)

            # save the user that do the update
            tooth.last_updated_by = user
            tooth.has_tartar=Plus.to_bool(data.get('has_tartar'))
            # save the change
            tooth.save()

        return {
            "success": True,
            "message": "odontograma.success.tooth_updated",
            "error": None
        }

    except ValidationError as e:
        return {
            "success": False,
            "message": "odontograma.error.validation",
            "error": str(e)
        }

    except Exception as e:
        return {
            "success": False,
            "message": "odontograma.error.unexpected-tooth",
            "error": str(e)
        }
    

def update_setting_odontogram(user,data):
    PROTECTED_FIELDS = {"company", "branch", "doctor", "id"}
    """
    Updates the OdontogramSetting of the given doctor dynamically from form_data.
    Ignores protected fields.
    """

    try:
        settings = OdontogramSetting.objects.get(doctor=user)
    except ObjectDoesNotExist:
        settings = OdontogramSetting.objects.create(
            doctor=user,
            company=user.company,
            branch=user.branch
        )
    
    # Iterate over the form data
    for field, value in data.items():
        # Skip protected fields
        if field in PROTECTED_FIELDS:
            continue

        # Check if the field exists in the model
        if hasattr(settings, field):
            setattr(settings, field, value)

    settings.save()
    return {
        "success": True,
        "message": "",
        "error": "",
    }