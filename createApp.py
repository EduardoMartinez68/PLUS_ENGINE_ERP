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

    os.makedirs(os.path.join(base_path, 'views'), exist_ok=True)
    index_html_path = os.path.join(base_path, 'views', 'index.html')

    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write("""<h1>Welcome To your app in PLUS</h1>""")

    # Crear config.yaml
    config_content = f"""name: "{app_name}"
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
    with open(os.path.join(base_path_config, 'urls.py'), 'w', encoding='utf-8') as f:
        f.write(urls_content)

    # Crear views.py con la función ajustada
    views_content = f"""from django.shortcuts import render

def {app_name}_home(request):
    return render(request, '{app_name}/index.html')
"""
    with open(os.path.join(base_path_config, 'views.py'), 'w', encoding='utf-8') as f:
        f.write(views_content)

    print(f"App '{app_name}' creada con éxito en {base_path}.")



if __name__ == '__main__':
    nombre = input("Escribe el nombre de la app: ").strip()
    if nombre:
        create_app(nombre)
    else:
        print("El nombre no puede estar vacío.")
