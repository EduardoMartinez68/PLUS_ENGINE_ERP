import openpyxl
from openpyxl import Workbook
import tempfile
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO
import os 
import json

def create_excel(user):
    '''
    this script is for create a excel and send to the frontend for that the 
    user can upload most speed the information of his customers
    '''
    language=user.language

    #here we will to create the book of excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Plus"

    #Now we will to create the header of excel in the language of the user
    headers = get_header_of_excel(language)
    ws.append(headers)

    #save in memory the excel
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # Prepare the HTTP response for download
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="plantilla_clientes.xlsx"'
    return response

def get_header_of_excel(language):
    '''
    return the header of the excel for upload customer
    with help of the language that need the user
    '''
    #get the path of the file of translate 
    translate_data=get_file_translate(language)

    #this be the key of the name that exist in the <translate.json>
    EXCEL_KEYS = [
        "customers.excel.name",
        "customers.excel.email",
        "customers.excel.phone",
        "customers.excel.cellphone",
        "customers.excel.date_of_birth",
        "customers.excel.gender",
        "customers.excel.country",
        "customers.excel.address",
        "customers.excel.city",
        "customers.excel.state",
        "customers.excel.postal_code",
        "customers.excel.num_ext",
        "customers.excel.num_int",
        "customers.excel.reference",
        "customers.excel.is_company",
        "customers.excel.company_name",
        "customers.excel.contact_name",
        "customers.excel.contact_email",
        "customers.excel.contact_phone",
        "customers.excel.contact_cellphone",
        "customers.excel.website",
        "customers.excel.note",
        "customers.excel.points",
        "customers.excel.credit",
        "customers.excel.tags",
        "customers.excel.customer_type",
        "customers.excel.customer_source",
        "customers.excel.priority",
        "customers.excel.price_list_number"
    ]



    #return the language that the user need, if not exist we will to return the Spanish for default
    headers_list = [translate_data.get(key) for key in EXCEL_KEYS]
    return headers_list

def get_file_translate(language):
    #create the path of the file <translate.json> for read the translate
    current_dir = os.path.dirname(__file__) #get the path current of the script
    file_path = os.path.join(current_dir, '..', 'locale', language, 'translate.json') #We get the path where the translation file is located.
    print(file_path)
    #now we will see if this file exist and if not exist we will to return all the language in spanish
    if not os.path.exists(file_path):
        return  {
        "customers.excel.name": "Nombre",
        "customers.excel.email": "Correo",
        "customers.excel.phone": "Teléfono",
        "customers.excel.cellphone": "Celular",
        "customers.excel.date_of_birth": "Fecha de Nacimiento",
        "customers.excel.gender": "Género",
        "customers.excel.country": "País",
        "customers.excel.address": "Dirección",
        "customers.excel.city": "Ciudad",
        "customers.excel.state": "Estado",
        "customers.excel.postal_code": "Código Postal",
        "customers.excel.num_ext": "Número Exterior",
        "customers.excel.num_int": "Número Interior",
        "customers.excel.reference": "Referencia",
        "customers.excel.is_company": "¿Es Empresa?",
        "customers.excel.company_name": "Nombre de la Empresa",
        "customers.excel.contact_name": "Nombre del Contacto",
        "customers.excel.contact_email": "Correo del Contacto",
        "customers.excel.contact_phone": "Teléfono del Contacto",
        "customers.excel.contact_cellphone": "Celular del Contacto",
        "customers.excel.website": "Sitio Web",
        "customers.excel.note": "Nota",
        "customers.excel.points": "Puntos",
        "customers.excel.credit": "Crédito",
        "customers.excel.tags": "Etiquetas (JSON o separadas por coma)",
        "customers.excel.customer_type": "Tipo de Cliente (ID o Nombre)",
        "customers.excel.customer_source": "Fuente del Cliente (ID o Nombre)",
        "customers.excel.priority": "Prioridad",
        "customers.excel.price_list_number": "Número de Lista de Precio"
    }


    #if exist now we will read all the information of the json for after search the information of translate
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data