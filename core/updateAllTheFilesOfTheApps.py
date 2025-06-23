
'''
    firt we will to convert all the path and links that have all tha apps
'''
import os
from core.readApps import APPS_FOLDER
import ast

def generate_views_and_urls(app_path):
    #get the path of the files and of the folder in where the programer have all his links
    links_path = os.path.join(app_path,'links') #this is the folder where the programmer have all his links, urls for that the user visit the web
    views_path = os.path.join(app_path,'config', 'views.py') #this is for update the file because after, we will to load all his views
    urls_path = os.path.join(app_path,'config', 'urls.py') #this is for update the file because after, we will to load all his urls

    function_blocks = []
    urlpatterns = []

    views_header = "#PLUS Power by {ED} Software Developer\nfrom django.contrib.auth.decorators import login_required\n"

    for filename in os.listdir(links_path):
        if filename.endswith('.py'):
            file_path = os.path.join(links_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Parse the source code to obtain functions
            tree = ast.parse(source)

            # Traverse all nodes to find functions
            for node in tree.body:
                lines = source.splitlines()

                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_line = lines[node.lineno - 1]
                    function_blocks.insert(0, import_line + "\n")
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    
                    #we will see the variable that need the function
                    args = [arg.arg for arg in node.args.args]

                    # Extract the function's source code (simple, with ast)
                    # This is a bit complex, here's a quick way:
                    func_lines = lines[node.lineno-1 : node.end_lineno]

                    # Original indentation (we assume it starts at column 0)
                    func_code = '\n'.join(func_lines)

                    #Now we generate the extended function with the AJAX if
                    args_str = ', '.join(args)
                    new_func = f"@login_required(login_url='login')\ndef {func_name}({args_str}):\n"
                    new_func += "    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':\n"

                    # We indented the original code one level higher for AJAX
                    for line in func_code.splitlines()[1:]:  # we remove the def line
                        new_func += "    " + line + "\n"
                    new_func += "    else:\n"

                    # We indented the original code one level higher for normal navigation
                    for line in func_code.splitlines()[1:]:
                        new_func += "    " + line + "\n"
                    new_func += "\n"

                    function_blocks.append(new_func)

                    # Generate URL path
                    url_path = func_name.replace('_home', '')

                    #her we will save all the parameters of the function
                    # For simplicity, we assume all parameters are integers
                    param_parts = []
                    for arg in args[1:]:  # Ignore 'request'
                        # For simplicity, I put all of them as <int:param>
                        param_parts.append(f"<int:{arg}>")


                    # Build the URL part
                    if param_parts:
                        param_url = '/' + '/'.join(param_parts)
                    else:
                        param_url = ''

                    if url_path == '':
                        url_path = ''
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
