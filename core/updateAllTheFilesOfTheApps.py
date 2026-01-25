
'''
    firt we will to convert all the path and links that have all tha apps
'''
import os
from core.readApps import APPS_FOLDER
import ast

def generate_views_and_urls(app_path):
    links_path = os.path.join(app_path, 'links')
    views_path = os.path.join(app_path, 'config', 'views.py')
    urls_path = os.path.join(app_path, 'config', 'urls.py')

    #if the folder links not exist in this app, we will to up this app
    if not os.path.exists(links_path):
            print(f"Skipping {app_path}: 'links' folder not found.")
            return
    
    function_blocks = []
    urlpatterns = []

    views_header = "#PLUS Power by {ED} Software Developer\nfrom django.contrib.auth.decorators import login_required\n"

    for filename in os.listdir(links_path):
        if filename.endswith('.py'):
            file_path = os.path.join(links_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            lines = source.splitlines()

            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_line = lines[node.lineno - 1]
                    function_blocks.insert(0, import_line + "\n")
                
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    
                    # --- NUEVA LÓGICA DE DECORADORES ---
                    is_public = False
                    # Revisamos los decoradores de la función
                    for decorator in node.decorator_list:
                        # Si es un decorador simple como @public
                        if isinstance(decorator, ast.Name) and decorator.id == 'public':
                            is_public = True
                        # Si es un decorador con llamada como @public()
                        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'public':
                            is_public = True

                    # Extraer argumentos
                    args = [arg.arg for arg in node.args.args]
                    func_lines = lines[node.lineno-1 : node.end_lineno]
                    
                    # Limpiamos el código original: quitamos los decoradores de la copia para que no se repitan
                    # Buscamos dónde empieza realmente la definición 'def'
                    actual_start_index = 0
                    for i, line in enumerate(func_lines):
                        if line.strip().startswith('def '):
                            actual_start_index = i
                            break
                    
                    clean_func_lines = func_lines[actual_start_index:]
                    func_code = '\n'.join(clean_func_lines)

                    # Generar la nueva función
                    args_str = ', '.join(args)
                    
                    # Solo añadir login_required si NO es pública
                    new_func = ""
                    if not is_public:
                        new_func += "@login_required(login_url='login')\n"
                    
                    new_func += f"def {func_name}({args_str}):\n"
                    new_func += "    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':\n"

                    # Indentar cuerpo para AJAX y Normal
                    body_lines = clean_func_lines[1:] # quitamos el 'def...'
                    for line in body_lines:
                        new_func += "    " + line + "\n"
                    new_func += "    else:\n"
                    for line in body_lines:
                        new_func += "    " + line + "\n"
                    new_func += "\n"

                    function_blocks.append(new_func)

                    # --- LÓGICA DE URL ---
                    url_path = func_name.replace('_home', '')
                    param_parts = []
                    for arg in args[1:]:
                        # Mejora: Si el argumento es 'slug', lo ponemos como slug, si no como int
                        type_str = "slug" if arg == "slug" else "int"
                        param_parts.append(f"<{type_str}:{arg}>")

                    param_url = '/' + '/'.join(param_parts) if param_parts else ''
                    urlpatterns.append(f"    path('{url_path}{param_url}/', views.{func_name}, name='{func_name}'),\n")

    # save all the data of the vies in the file views.py
    with open(views_path, 'w', encoding='utf-8') as f_views:
        f_views.write(views_header)
        for func in function_blocks:
            f_views.write(func)

    # save all the data of the urls in the file urls.py
    with open(urls_path, 'w', encoding='utf-8') as f_urls:
        f_urls.write("from django.urls import path\n")
        f_urls.write("from . import views\n\n")
        f_urls.write("urlpatterns = [\n")
        for urlp in urlpatterns:
            f_urls.write(urlp)
        f_urls.write("]\n")

# Uso
for app_folder in APPS_FOLDER:
    generate_views_and_urls(app_folder)
