# PLUS ERP - Sistema Mexicano para Mexicanos 🇲🇽.
![PLUS ERP company](web_git/companies.webp)

**PLUS** es un ERP moderno, minimalista y elegante, inspirado en soluciones como Odoo, pero adaptado a las necesidades reales en México y América Latina.

PLUS está diseñado para resolver los problemas cotidianos que enfrentan abogados y despachos legales: gestión de clientes, organización de casos, manejo de documentos, facturación, agenda y reportes — todo en una interfaz clara, profesional y de uso sencillo.

Tecnología con un toque de magia ❤️
---
## 👤 Sobre el autor

**Nombre:** Martínez Ortiz Eduardo Antonio  
**Nacionalidad:** Mexicano 🇲🇽  
**Perfil:** Desarrollador Full Stack apasionado por el software para negocios reales.

Inicié este proyecto porque quería usar Odoo para crear un software ERP para abogados en 🇲🇽 México. Pensé: “esto va a ser pan comido”. Spoiler: NO LO FUE. 😅
Había muchísimas incompatibilidades, no entendía el código que escribían otros programadores 👨🏻‍💻, y cada vez que surgía un error, tenía que restaurar archivos completos 🤯.

Pasé días — sí, días enteros — intentando cambiar el nombre del módulo "Proyectos" por "Casos" ⚖️... ¿el resultado? ¡Jamás lo logré! 😂

Así que me harté, respiré profundo, y decidí crear mi propio ENGINE ERP... with blackjack and hookers 🃏🍸 — bueno, en realidad, con código limpio y pensado para que cualquier negocio en México pudiera usarlo sin dolores de cabeza 🙌.
![PLUS ERP momo](web_git/momo.webp)

👉 Nota personal:

No tengo absolutamente nada en contra de Odoo — de hecho, ¡lo admiro mucho! 👏
Me parece una plataforma impresionante, bien diseñada y además hecha en mi lenguaje favorito: Python 🐍❤️.

Pero hay algo que siempre me pasa como programador: cuando uso una herramienta, siempre pienso... "yo podría hacer esto mejor (o al menos, más a mi manera)" 😅. No necesariamente "mejor" para todo el mundo, sino mejor para mí y para otros frikis como yo y que quieran ayudar a otros de esta manera.

Así nació este proyecto: no como un "competidor" de Odoo, sino como una alternativa más simple, más enfocada, hecha desde cero con mucho cariño por alguien que quería entender cada línea de su propio ERP. Ahora El plan es crear un ENGINE super facil, creado para que incluso programadores inexpertos puedan crear sus propias apps para empresas. Ahora en mi ENGINE es super facil cambiar el nombre de las apps ya que solo necesitas un solo clic jaja tambien queria que las dependencias fueran extremadamente facil de agregar y que fuera mas facil de personalizar para otras personas. 

El objetivo de PLUS es ser un **engine abierto** y extensible para que otros programadores, despachos y estudios jurídicos puedan adaptarlo a su realidad, aportar mejoras y evolucionarlo en comunidad.
![PLUS ERP login](web_git/login.webp)
![PLUS ERP supplies](web_git/supplies.webp)
---

## ✨ Características principales (planes a futuro)
- Gestión de clientes
- Gestión de casos jurídicos
- Plantillas de documentos legales
- Control de facturación y pagos
- Agenda de audiencias y tareas
- Reportes dinámicos
- Soporte multi-usuario y control de permisos
- UI moderna y elegante (inspirada en Odoo y otras apps líderes)

---

## 🚀 Roadmap de funcionalidades (planes a futuro)

- ✅ Agenda avanzada con notificaciones
- ✅ Plantillas de documentos personalizables
- 🚧 Portal para clientes (self-service)
- 🚧 Firma electrónica integrada
- 🚧 Chat interno para abogados
- 🚧 Integración con calendario Google/Outlook

---
![PLUS ERP dashboard](web_git/dashboard.webp)

## 📜 Condiciones de Uso y Filosofía de Código Abierto

**PLUS ERP** es un proyecto **de código abierto** porque creo firmemente en el poder de la comunidad, la colaboración y el aprendizaje compartido 🌎💻.

El software libre y abierto nos permite:

✅ Aprender unos de otros  
✅ Adaptar las herramientas a nuestras necesidades  
✅ Mejorar el software entre todos  
✅ Democratizar el acceso a tecnología de calidad  

**PLUS ERP** es gratuito para que cualquier empresa, programador o persona interesada pueda estudiarlo, modificarlo y usarlo. Lo único que pido a cambio es que se respeten estas pequeñas condiciones para que la comunidad crezca de forma sana y respetuosa:

1. **Atribución**  
   Si usas **PLUS ERP** o alguna parte de su código en tus proyectos, por favor incluye el crédito al creador original:  
   `Creado por Martínez Ortiz Eduardo Antonio (México)` 🙋🏻‍♂️

2. **Compartir mejoras**  
   Si haces modificaciones o mejoras interesantes, sería genial que las compartas de vuelta a la comunidad mediante Pull Requests o publicando tu fork. Así todos aprendemos y el proyecto sigue mejorando 🚀.

3. **No cierres el código**  
   No está permitido tomar este engine y convertirlo en un producto cerrado o privativo. La idea es que siga siendo abierto para siempre, accesible y transparente 🔓.

4. **Respeto en la comunidad**  
   Si se genera una comunidad en torno a **PLUS ERP** (foros, Discord, GitHub Issues), te pido que siempre participes con respeto, apertura y buen rollo 🤝.

---

### 👉 ¿Por qué hacerlo abierto?

Porque la magia del código abierto es la colaboración. Al compartir tu conocimiento y tu trabajo, ayudas a que otros mejoren el software, aprendan y creen soluciones increíbles que quizá ni imaginábamos.  

Espero que **PLUS ERP** inspire a otros desarrolladores mexicanos y latinoamericanos a crear más herramientas pensadas para nuestro contexto, idioma, empresas y necesidades 🎉. Siempre he pensado que nuestro proposito como programadores es crear Tecnología con un toque de magia ❤️



---

## 📦 Instalación técnica

### Requisitos

- Python  
- PostgreSQL  
- Git

### Instrucciones

```bash
git clone https://github.com/EduardoMartinez68/PLUS_ENGINE_ERP   
cd plus-erp
npm install

## 👨‍💻 Apartado técnico para desarrolladores

PLUS ERP es un sistema modular, basado en python :

- **Frontend:** HTML + CSS (sin Bootstrap)
- **Backend:** PYTHON
- **Base de datos:** PostgreSQL
- **Arquitectura:** MVC ligera
- **Estilo:** CSS propio con prefijos `sub-menu-app-` para evitar colisiones
```
---
## 🚀 Crear una nueva app
Ejecuta el siguiente comando en la terminal del proyecto:

```bash
python createApp.py
```
Te preguntara por el nombre de tu nueva app y python la va a crear dentro de la carpeta llamada apps. 

### 📁 Estructura del proyecto
```plaintext
PLUS ERP/
├── createApp.py
├── apps/
│   │ 
│   ├── my_app/
│       └── config.yamal
│       └── config/
│       └── links/      
│       └── locale/   
│       └── static/   
│       └── views/   
│       └── db.sql   
├── core/
├── database/
├── media/
├── static/
├── .env
├── manager.py
```

### 📁 Configuración de la App
Una de las cosas más importantes es tu archivo de configuración, donde vendrán las características de las vistas de tu app. Aquí te recomiendo que lo dejes como lo creaste y que solo cambies el ícono si quieres, y las dependencias que te servirán si es que tu app depende de otras apps de tu ERP. 

```yamal
name: "my_app"
icon: "/my_app/static/icon.webp"
path: "/my_app"
depends: ["other_app"]
dbInit: true
permissionsFile: 'permissions.json'
```

Si tu app no depende de ninguna otra elimina el campo. 
```yamal
name: "my_app"
icon: "/my_app/static/icon.webp"
path: "/my_app"
dbInit: true
permissionsFile: 'permissions.json'
```
## BASE DE DATOS
Este ERP usa PostgreSQL como base de datos principal.  
En todas tus apps tendrás un archivo `db.sql` donde crearás la estructura básica de la tabla de esa app; incluso puedes crear tu propio schema si lo deseas.  
Ten en cuenta que este archivo se volverá a cargar cada vez que se reinicie el servidor, así que aquí puedes agregar actualizaciones y cláusulas para evitar errores.


### EJEMPLO
```sql
-- Crear esquema si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'customer') THEN
        EXECUTE 'CREATE SCHEMA customer';
    END IF;
END$$;

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS customer.customer (
    id bigserial NOT NULL,
    id_branch bigint,
    name varchar(300) NOT NULL,
    email text,
    this_customer_is_a_company boolean NOT NULL DEFAULT false,
    company_name varchar(255),
    rfc varchar(50),
    curp varchar(50),
    phone varchar(50),
    cellphone varchar(50),
    website text,
    creation_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    country varchar(100),
    status boolean NOT NULL DEFAULT true,
    CONSTRAINT id_key_customer PRIMARY KEY (id)
);

-- Agregar la FK solo si no existe (esto es más elegante)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'branch_fk'
          AND table_schema = 'customer'
          AND table_name = 'customer'
    ) THEN
        ALTER TABLE customer.customer
        ADD CONSTRAINT branch_fk FOREIGN KEY (id_branch)
        REFERENCES company.branch (id)
        MATCH FULL
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END$$;
```


## RUTAS/LINKS/URLS
Lo más importante sera donde vas a programar tus rutas y eso sera dentro de la carpeta **links**. Este ERP tiene un esqueleto usando Django pero para automatizar la carga de las urls, views y models construir scripts que las crean automaticamente. Mis scripts leen todos los archivos que estan dentro de la carpeta **links** de todas las apps y construyen el archivo completo de las urls.py y views.py para guardarlas en la carpeta **config** de tu app. 

### Ejemplo
Esto es un archivo que se guarda dentro de la carpeta **links**
```py
from django.shortcuts import render

def cases_home(request):
    return render(request, 'index.html')


def left_out(request):
    return render(request, 'index.html')


def case_home_2(request):
    return render(request, 'index.html')
```

Cuando se recarga el servidor este va a leer completamente de nuevo todos los archivos, modelos, vistas y bases de datos y crearlas en tu carpeta **config** de tu app.
### urls.py
```py
from django.urls import path
from . import views

urlpatterns = [
    path('cases', views.cases_home, name='cases_home'),
    path('left_out', views.left_out, name='left_out'),
    path('case_2', views.case_home_2, name='case_home_2'),
]

```
### views.py
```py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required(login_url='login')
def cases_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

@login_required(login_url='login')
def left_out(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

@login_required(login_url='login')
def case_home_2(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')
```

Como puedes ver, los archivos se reescribieron, incluso ya con la cláusula de que el usuario debe tener una sesión iniciada en el ERP para poder acceder al resto de las características.  
También, si no quieres que cierta app necesite que estés logueado para verla, puedes desactivar esa función en el archivo **config.yaml** de tu app.


---
---
---
---
---
# Manual de funciones
## ⚠️ show_alert()

Función JavaScript para mostrar ventanas emergentes (popups) de alerta en la interfaz.  
Permite mostrar diferentes tipos de mensajes al usuario: **información, éxito, error, pregunta**, etc.

`show_alert()` actualiza dinámicamente una ventana de alerta personalizada en el HTML, cambiando su texto, íconos, colores y botones, según el tipo de mensaje que deseamos mostrar.

### ⚙️ Parámetros

```js
show_alert(
    type,           // (string) Tipo de alerta: 'info', 'success', 'alert', 'question'
    title,          // (string) Título que se mostrará en la alerta
    description,    // (string) Texto descriptivo del mensaje
    readmoreText    // (string, opcional) Texto adicional para mostrar más detalles (por ejemplo: errores técnicos)
)
```
---
## 🔔 show_notification()

Función JavaScript para mostrar notificaciones flotantes de tipo *toast*.  
Ideal para informar rápidamente al usuario sobre el resultado de una acción: éxito, error, advertencia, etc.

`show_notification()` crea dinámicamente una pequeña tarjeta de notificación que aparece en la interfaz durante unos segundos, con iconos y estilos personalizados según el tipo de mensaje.


### ⚙️ Parámetros

```js
show_notification(
    type = 'info',    // (string) Tipo de notificación: 'success', 'error', 'warning', 'info'
    message = '',     // (string) Texto a mostrar en la notificación
    duration = 4000   // (int) Tiempo en milisegundos que se mostrará (default: 4000 ms)
)
```
---
## 🔍 update_table_with_seeker()
### 👉 ¿Cómo actualizar tablas con la ayuda de un motor de búsqueda?

Función JavaScript para actualizar una tabla HTML en tiempo real a medida que el usuario escribe en un campo de búsqueda (input), obteniendo datos dinámicos desde el servidor.


`update_table_with_seeker` permite mejorar la experiencia de usuario permitiendo búsquedas en tiempo real sobre una tabla, sin necesidad de recargar la página.

Ideal para integraciones tipo CRM, sistemas administrativos, buscadores de clientes, productos, empleados, etc.

### ⚙️ Parámetros

```js
update_table_with_seeker(
    inputId,      // (string) ID del campo de búsqueda (input)
    tableId,      // (string) ID de la tabla HTML que se actualizará
    columns,      // (array) Lista de columnas a mostrar, en el mismo orden que la tabla
    searchUrl,    // (string) URL de la API o endpoint que devolverá los resultados
    delay = 500   // (opcional, int) Tiempo de espera en ms antes de enviar la búsqueda (default: 500)
)
```

### 🔍 Ejemplo completo: Búsqueda en tiempo real en tabla HTML

Ejemplo de cómo implementar una búsqueda en tiempo real en una tabla HTML, con conexión a un servidor en Python (Django), utilizando la función `update_table_with_seeker()`.

### 🖥️ 1️⃣ Código HTML

```html
<input type="text" class="search-input-in-form" id="serach-customers"
    placeholder="Buscar clientes por email o nombre...">

<table id="table-customer">
    <thead>
        <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Celular</th>
            <th>Nombre Empresa</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        <!-- Los resultados se insertarán automáticamente aquí -->
    </tbody>
</table>
```

### 🖥️ 1️⃣ Código JS para llamar a la función
```js
update_table_with_seeker(
    'serach-customers', // ID del input (campo de búsqueda)
    'table-customer',   // ID de la tabla HTML
    ['name', 'email', 'phone', 'cellphone', 'company_name'], // columnas que se mostrarán
    'customers/search_customers' // URL del endpoint en el servidor
);
```

### 🖥️ 1️⃣ Código Python en tu servidor
```py
@csrf_exempt
def search_customers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '').strip()

        # Filtrar los clientes cuyo nombre o email contengan la consulta (insensible a mayúsculas/minúsculas)
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        ).order_by('name')[:20]  # Limitar a 20 resultados

        # Construir la respuesta
        result_list = []
        for c in customers:
            result_list.append({
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'cellphone': c.cellphone,
                'company_name': c.company_name
            })

        return JsonResponse({'success': True, 'results': result_list})
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
```
---

## 🔔 update_field_with_seeker()
Función JavaScript para actualizar campos con tarjetas en tu HTML.  
Ideal automatizar las actualizaciones de campos en tu html. Se debera programar el Backend. 

```js
update_field_with_seeker(
    inputsId,      // (array) ID de los campo de búsqueda (input, select, etc.). inputsId[0] is the id of the search inpu
    fieldId,      // (string) the field id that we will update
    divHtml,      // (string) El codigo en html que se remplazara en el campo. 
    searchUrl,    // (string) URL de la API o endpoint que devolverá los resultados
    delay = 500   // (opcional, int) Tiempo de espera en ms antes de enviar la búsqueda (default: 500)
)
```


### 🔍 Ejemplo completo: Búsqueda en tiempo real para actualizar campos en tabla HTML
Ejemplo de cómo implementar una búsqueda en tiempo real en un campo en HTML, con conexión a un servidor en Python (Django), utilizando la función `update_field_with_seeker()`.

### 🖥️ 1️⃣ Código HTML

```html

  <div class="row">
    <div class="col-10">
        <!--Este es el buscador-->
      <input type="text" class="search-input-in-form" id="search-contracts"
        placeholder="Buscar contratos por título...">
    </div>
    <div class="col">
      <!--Este es un select-->
      <select id="select-status">
        <option value="true">Activo</option>
        <option value="false">Desactivados</option>
        <option value="">todos</option>
      </select>
    </div>
  </div>
  <br>


  <div class="grid-files" aria-label="Lista de archivos" id="field-contracts">
        <!--aqui estaran todos los divs que traeras desde el servidor-->
  </div>
```

### 🖥️ 1️⃣ Código JS para llamar a la función
```js
(() => {
  const divHtml = `
    <div class="card-file" tabindex="0">
      <div class="file-info">
        <i class="fi fi-sr-document-signed" aria-hidden="true"></i>
        <span>{ title }</span>
      </div>
      <div class="buttons">
        <button class="button" type="button" onclick="nextWeb('/contracts/form_contract/{ id }')">Usar</button>
        <button class="button" type="button" onclick="nextWeb('/contracts/edit_contract/{ id }')">Editar</button>
      </div>
    </div>`;

  update_field_with_seeker(
    ['search-contracts', 'select-status'], // id of the input of the seeker
    'field-contracts',  // id of the container to update
    divHtml,            // template with placeholders
    'contracts/search_contracts/' // url for the search
  );
})();
```

### 🖥️ 1️⃣ Código Python en tu servidor
```py
@csrf_exempt
def search_contracts(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        all_filters = data.get('allFilters', [])
        query = all_filters[0].strip() if len(all_filters) > 0 else ''
        status = all_filters[1].strip().lower() if len(all_filters) > 1 else ''

        contracts = Contracts.objects.filter(
            Q(title__icontains=query) | Q(content_html__icontains=query)
        )

        # add the filter for status
        if status == 'true':
            contracts = contracts.filter(active=True)
        elif status == 'false':
            contracts = contracts.filter(active=False)

        # We order and limit results
        contracts = contracts.order_by('title')[:20]

        # We generate the response
        result_list = [
            {
                'id': c.id,
                'title': c.title,
                'creation_date': c.creation_date
            }
            for c in contracts
        ]

        return JsonResponse({'success': True, 'results': result_list})
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
```

![PLUS ERP update_field_with_seeker](web_git/update_field_with_seeker.webp)
---