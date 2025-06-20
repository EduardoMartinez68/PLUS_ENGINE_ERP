import os

def create_app(app_name):
    base_path = os.path.join('apps', app_name)

    # Crear carpetas
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, 'config'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'links'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'locale'), exist_ok=True)


    os.makedirs(os.path.join(base_path, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'static', 'img'), exist_ok=True)

    os.makedirs(os.path.join(base_path, 'views',f'partials_{app_name}'), exist_ok=True)
    index_html_path = os.path.join(base_path, 'views', f'home_{app_name}.html')

    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(create_web_html(app_name))

    # Crear config.yaml
    config_content = f"""name: "{app_name}"
appName: "{app_name}"
icon: "{app_name}/icon.webp"
path: "/{app_name}"
dbInit: true
permissionsFile: 'permissions.json'
"""
    with open(os.path.join(base_path, 'config.yaml'), 'w', encoding='utf-8') as f:
        f.write(config_content)

    # Crear db.sql vacío
    with open(os.path.join(base_path, 'db.sql'), 'w', encoding='utf-8') as f:
        f.write("-- SQL statements for database setup go here\n")

    # Crear icon.webp vacío (puedes reemplazar luego el archivo real)
    with open(os.path.join(base_path, 'static','icon.webp'), 'wb') as f:
        pass
    
    base_path_config = os.path.join(base_path, 'config')
    # Crear models.py vacío
    with open(os.path.join(base_path_config, 'models.py'), 'w', encoding='utf-8') as f:
        f.write("# Model definitions go here\n")

    # Crear urls.py con el nombre de la app adaptado
    urls_content = f"""from django.urls import path
from . import views

urlpatterns = [
    path('', views.{app_name}_home, name='{app_name}_home'),
]
"""
    
    
    with open(os.path.join(base_path, 'urls.py'), 'w', encoding='utf-8') as f:
        f.write(urls_content)

    # Crear views.py con la función ajustada
    views_content = f"""from django.shortcuts import render

def {app_name}_home(request):
    return render(request, 'home_{app_name}.html')
"""
    fileLink=os.path.join(base_path, 'links')
    with open(os.path.join(fileLink, 'views.py'), 'w', encoding='utf-8') as f:
        f.write(views_content)

    print(f"App '{app_name}' creada con éxito en {base_path}.")




def create_web_html(app_name):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Welcome to {app_name}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f0f4f8;
                color: #333;
                text-align: center;
                padding: 50px;
            }}
            h1 {{
                color: #007ACC;
                margin-bottom: 20px;
            }}
            p {{
                font-size: 18px;
                line-height: 1.6;
                max-width: 600px;
                margin: 0 auto;
                color: #555;
            }}
            .highlight {{
                color: #ff6600;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to your app <span class="highlight">{app_name}</span> in PLUS</h1>
        <p>Thank you for choosing our platform. This app is designed to help you manage your <strong>{app_name}</strong> efficiently and effortlessly.</p>
        <p>Explore the features and enjoy a seamless experience!</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    nombre = input("Escribe el nombre de la app: ").strip()
    if nombre:
        create_app(nombre)
    else:
        print("El nombre no puede estar vacío.")
