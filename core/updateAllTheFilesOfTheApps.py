'''
    firt we will to convert all the path and links that have all tha apps
'''
import os
from core.readApps import APPS_FOLDER
import ast
from pathlib import Path
import json

# 1. get the path of the file cache_files.json
cacheFiles = Path(__file__).resolve().parent.parent / 'cache_files.json'

# if not exist the file of the cache we will to create, if exist load his information
if not cacheFiles.exists():
    container_files_cache = {}
    print("The file cache_files not exist.")
else:
    with open(cacheFiles, 'r', encoding='utf-8') as file:
        container_files_cache = json.load(file) #read the file of the cache

def this_file_have_change(file_path):
    modified_timestamp = os.path.getmtime(file_path) #get the new time of the file for save in the cache

    #here we will see the old modification of the file 
    value_in_cache = container_files_cache.get(file_path) #get the value of the cache

    #now we will see if the date are equals or exist a change 
    return not (modified_timestamp==value_in_cache)


def update_cache_file(file_path, newValue=None):
    new_date_of_creation = os.path.getmtime(file_path) #get the new time of the file for save in the cache
    container_files_cache[file_path] = new_date_of_creation 
    print(f'➤ the file {file_path} was updated')



def generate_views_and_urls(app_path):
    links_path = os.path.join(app_path, 'links')
    #if the folder links not exist in this app, we will to up this app
    if not os.path.exists(links_path):
        print(f"Skipping {app_path}: 'links' folder not found.")
        return
    
    #see if exist files .py that was change 
    files_list=[]
    for filename in os.listdir(links_path):
        if filename.endswith('.py'):
            file_path = os.path.join(links_path, filename)
            if not this_file_have_change(file_path):
                continue

            files_list.append(filename)
    
    #create the variable 
    views_path = os.path.join(app_path, 'config', 'views.py')
    urls_path = os.path.join(app_path, 'config', 'urls.py')
    function_blocks = []
    urlpatterns = []
    views_header  = "#PLUS Power by {ED} Software Developer\nfrom django.contrib.auth.decorators import login_required\nfrom django.views.decorators.clickjacking import xframe_options_exempt\nfrom django.views.decorators.csrf import csrf_exempt\n"

    for filename in files_list:
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

                if is_public:
                    new_func += "@xframe_options_exempt\n@csrf_exempt\n"
                else:
                    new_func += "@login_required(login_url='login')\n"

                new_func += f"def {func_name}({args_str}):\n"
                #new_func += "    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':\n"
                body_lines = clean_func_lines[1:]

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


        #save the change in the cache 
        update_cache_file(file_path)

# Uso
for app_folder in APPS_FOLDER:
    generate_views_and_urls(app_folder)

#update all the cache of the date of the files
with open(cacheFiles, 'w', encoding='utf-8') as file:
    json.dump(container_files_cache, file, indent=4)