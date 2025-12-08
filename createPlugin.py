import os

def create_plugin(app_name, plugin_app):
    base_path = os.path.join('apps', app_name, plugin_app)

    # create folders
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, 'config'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'links'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'locale'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'services'), exist_ok=True)

    os.makedirs(os.path.join(base_path, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'static', 'img'), exist_ok=True)

    os.makedirs(os.path.join(base_path, 'views',f'partials_{app_name}_{plugin_app}'), exist_ok=True)
    index_html_path = os.path.join(base_path, 'views', f'home_{plugin_app}.html')

    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(create_web_html(plugin_app))

    # Crear config.yaml
    config_content = f"""
name: "{plugin_app}"
appName: "{app_name}_{plugin_app}"
icon: "/{app_name}/{plugin_app}/icon.webp"
path: "/{app_name}/{plugin_app}/"
dbInit: true
permissionsFile: 'permissions.json'
    """
    with open(os.path.join(base_path, 'config.yaml'), 'w', encoding='utf-8') as f:
        f.write(config_content)

    # create models.py for that the programmer can do a database
    with open(os.path.join(base_path, 'models.py'), 'w', encoding='utf-8') as f:
        f.write("#here you can create the body of the database \n")

    # create icon.webp (you can then replace the real file)
    with open(os.path.join(base_path, 'static','icon.webp'), 'wb') as f:
        pass

    # Crear urls.py con el nombre de la app adaptado
    urls_content = f"""from django.urls import path
from . import views

urlpatterns = [
    path('', views.{app_name}_home, name='{app_name}_home'),
]
"""
    
    
    with open(os.path.join(base_path, 'urls.py'), 'w', encoding='utf-8') as f:
        f.write(urls_content)

    # create views.py with the function adjusted
    views_content = f"""from django.shortcuts import render

def {app_name}_home(request):
    return render(request, 'home_{app_name}.html')
"""
    fileLink=os.path.join(base_path, 'links')
    with open(os.path.join(fileLink, 'views.py'), 'w', encoding='utf-8') as f:
        f.write(views_content)

    print(f"App '{app_name}' create with success in {base_path}.")

def create_web_html(plugin_app):
    return f"""
        <title>Welcome to {plugin_app}</title>
        <style>
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
        <h1>Welcome to your plugin <span class="highlight">{plugin_app}</span> in PLUS</h1>
        <p>Thank you for choosing our platform. This app is designed to help you manage your <strong>{plugin_app}</strong> efficiently and effortlessly.</p>
        <p>Explore the features and enjoy a seamless experience!</p>
    """

if __name__ == '__main__':
    appName = input("What is the the name of the app?: ").strip()
    pluginName = input("What is the the name of the plugin?: ").strip()
    if appName and pluginName:
        create_plugin(appName, pluginName)
    else:
        print("The name of the plugin not can be empty.")
