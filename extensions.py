import os
import glob
import json
import shutil
from pathlib import Path
import json
import re

# 1. get the path of the file cache_files.json
cacheFiles = Path(__file__).resolve().parent / 'cache_files.json'

# if not exist the file of the cache we will to create, if exist load his information
if not cacheFiles.exists():
    container_files_cache = {}
    print("The file cache_files not exist.")
else:
    with open(cacheFiles, 'r', encoding='utf-8') as file:
        container_files_cache = json.load(file) #read the file of the cache

def replace_keyword(texto, valor):
    clave="plus"
    # 1. Limpiamos el valor de la ruta:
    # - Eliminamos la extensión .html del final
    valor_limpio = re.sub(r'\.[^/.]+$', '', valor)

    # - Reemplazamos cualquier barra diagonal (normal o invertida) por '_'
    valor_limpio = re.sub(r'[\\/]+', '_', valor_limpio)

    """
    Busca una clave en formato de llaves (ej. {clave}) dentro del texto
    y la reemplaza por el valor proporcionado.
    """
    # Construimos la estructura exacta que queremos buscar, por ejemplo: "{plus}"
    objetivo = f"{{{clave}}}"
    
    # Reemplazamos todas las ocurrencias en el texto
    texto_modificado = texto.replace(objetivo, valor_limpio)
    
    return texto_modificado

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

def get_folder_mtime(folder_path):
    """
    It scans the folder and returns the modification date
    of the most recently found file within it.
    """
    max_mtime = 0
    
    # os.walk read all the folder , subfolder and files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > max_mtime:
                    max_mtime = mtime
            except FileNotFoundError:
                # this is the file is delete of the memory while we is reading
                continue
    
    return max_mtime

def get_plugin_directories(plugins_base_path):
    """
    Scans the plugins folder and returns a list of paths for each plugin found.
    """
    plugin_folders = [] 
    
    if os.path.exists(plugins_base_path):
        # Iterate through items in the plugins directory
        for item_name in os.listdir(plugins_base_path):
            full_path = os.path.join(plugins_base_path, item_name)
            
            # Ensure we only add directories, ignoring loose files
            if os.path.isdir(full_path):
                plugin_folders.append(full_path)
                
    return plugin_folders

def create_the_file_locale(app_path, core_folder, plugins_base_folder):
    # path to save the final locale files
    target_locale_folder = os.path.join(app_path, 'config', 'locale') #target_locale_folder = os.path.join(app_path, "locale")
    core_locale_folder = os.path.join(core_folder, "locale")
    available_plugins = get_plugin_directories(plugins_base_folder)

    if not os.path.exists(target_locale_folder):
        os.makedirs(target_locale_folder)

    # 1. Identify all available languages ​​(both in the core and plugins)
    # This creates a unique list of folders such as ['es', 'pl', 'en']
    languages = set()
    if os.path.exists(core_locale_folder):
        languages.update([d.name for d in os.scandir(core_locale_folder) if d.is_dir()])

    for plugin in available_plugins:
        p_locale = os.path.join(plugin, 'locale')
        if os.path.exists(p_locale):
            languages.update([d.name for d in os.scandir(p_locale) if d.is_dir()])

    # 2. Process each language
    for lang in languages:
        merged_data = {}

        # --- PART A: Read the CORE (Base) ---
        core_file = os.path.join(core_locale_folder, lang, 'translate.json')

        #here we will see in the cache of the files is exist change in the translate, if not exist we not create the new file
        if not this_file_have_change(core_file):
            continue

        if os.path.exists(core_file):
            with open(core_file, 'r', encoding='utf-8') as f:
                merged_data.update(json.load(f))

        # --- PART B: Mix with PLUGINS ---
        for plugin in available_plugins:
            plugin_file = os.path.join(plugin, 'locale', lang, 'translate.json')
            if os.path.exists(plugin_file):
                with open(plugin_file, 'r', encoding='utf-8') as f:
                    try:
                        plugin_json = json.load(f)
                        # The update replaces existing keys or adds new ones
                        merged_data.update(plugin_json)
                    except json.JSONDecodeError:
                        print(f"Error leyendo JSON en: {plugin_file}")

        # --- PART C: Save the result in the final folder ---
        final_lang_folder = os.path.join(target_locale_folder, lang)
        
        # Create the destination folder if it doesn't exist (es, pl, etc)
        os.makedirs(final_lang_folder, exist_ok=True)
        
        final_file_path = os.path.join(final_lang_folder, 'translate.json')
        with open(final_file_path, 'w', encoding='utf-8') as f_out:
            json.dump(merged_data, f_out, indent=4, ensure_ascii=False)

        update_cache_file(core_file) #update the cache of the file

def build_app_views(app_path):
    """
    Main function to merge core HTML files with plugin extensions.
    It reads base views from 'core' and appends extra HTML from each plugin's 'extensions'.
    """
    # 1. Define base paths
    core_folder = os.path.join(app_path)

    #here we will to create the path of the folder of the views and locale that exist in the core of the app
    views_folder = os.path.join(core_folder, "views")

    plugins_base_folder = os.path.join(app_path, "plugins")
    #output_folder = os.path.join(app_path, "views")
    
    
    # 2. Get all available plugin directories
    available_plugins = get_plugin_directories(plugins_base_folder) 

    # 3. Locate all base HTML files in the core folder
    # We use normpath to prevent issues with mixed slashes (/ vs \)
    core_search_pattern = os.path.normpath(os.path.join(views_folder, "*.html"))
    core_files = glob.glob(core_search_pattern)

    for file_path in core_files:
        # Get filename with extension (e.g., 'home.html')
        filename = os.path.basename(file_path)
        
        #here we will see the old modification of the file 
        if not this_file_have_change(file_path):
            continue

        # Get filename without extension for matching (e.g., 'home')
        view_name, _ = os.path.splitext(filename)

        # Read the primary content from the core view
        with open(file_path, 'r', encoding='utf-8') as f:
            final_html_content = f.read()
            final_html_content=replace_keyword(final_html_content, file_path)

        # 4. Search for extensions within each plugin for the current view
        for plugin_path in available_plugins:
            # Path structure: plugins/plugin_name/extensions/view_name
            extension_dir = os.path.join(plugin_path, "extensions", view_name)
            
            if os.path.isdir(extension_dir):
                # Look for any .html files inside the extension folder
                ext_pattern = os.path.normpath(os.path.join(extension_dir, "*.html"))
                
                for ext_file_path in glob.glob(ext_pattern):
                    with open(ext_file_path, 'r', encoding='utf-8') as fe:
                        # Append the plugin HTML content to the base content
                        new_html= fe.read()
                        final_html_content+="\n" +replace_keyword(new_html, extension_dir)

        # 5. Save the merged result into the 'views' folder
        output_folder = os.path.join("templates")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        
        #now we will to create the folder of the app in the views folder if not exist 
        output_folder = os.path.join("templates", os.path.basename(app_path))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        optimized_html=final_html_content
        final_output_path = os.path.join(output_folder, filename)

        #here we will see if exist a change in the template for after save in the cache
        with open(final_output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(optimized_html)

            #save the file in the cache 
        update_cache_file(file_path)



    #Now we will to create the locale files merging the core with the plugins locale files
    create_the_file_locale(app_path, core_folder, plugins_base_folder)

def migrate_partials_to_templates2(app):
    app_name = os.path.basename(os.path.normpath(app))
    folder_views = os.path.join(app, "views")
    target_folder = os.path.join("templates", app_name)

    #if not exist the folder views we return
    if not os.path.exists(folder_views):
        return
    
    os.makedirs(target_folder, exist_ok=True)

    for item in os.listdir(folder_views):
        source_path = os.path.join(folder_views, item)

        # only folders
        if os.path.isdir(source_path):
            destination_path = os.path.join(target_folder, item)
            
            #here we will see if the folder have change 
            if os.path.isdir(destination_path):
                shutil.rmtree(destination_path) #if exist a change we will to delete all the folder of the partials
            shutil.copytree(source_path, destination_path)


def migrate_partials_to_templates(app):
    app_name = os.path.basename(os.path.normpath(app))

    folder_views = os.path.join(app, "views")
    target_folder = os.path.join("templates", app_name)

    # Folder does not exist
    if not os.path.exists(folder_views):
        return

    os.makedirs(target_folder, exist_ok=True)

    for item in os.listdir(folder_views):

        source_root = os.path.join(folder_views, item)

        if not os.path.isdir(source_root):
            continue

        destination_root = os.path.join(target_folder, item)

        # Remove previous version
        if os.path.exists(destination_root):
            shutil.rmtree(destination_root)

        # Walk through all folders/files
        for root, dirs, files in os.walk(source_root):

            # Relative path from the source folder
            rel_path = os.path.relpath(root, source_root)

            current_destination = os.path.join(destination_root, rel_path)
            os.makedirs(current_destination, exist_ok=True)

            for file in files:

                source_file = os.path.join(root, file)
                destination_file = os.path.join(current_destination, file)

                # HTML files
                if file.endswith(".html"):

                    with open(source_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Generate namespace from the file path
                    namespace = os.path.relpath(source_file, app)
                    namespace = os.path.splitext(namespace)[0]
                    namespace = namespace.replace(os.sep, "_")

                    namespace = f"apps_{app_name}_{namespace}"

                    content = replace_keyword(content, namespace)

                    with open(destination_file, "w", encoding="utf-8") as f:
                        f.write(content)

                else:
                    shutil.copy2(source_file, destination_file)

def load_plugins_and_extensions():
    #1. Create the folder templates if not exist and when exist delete all the subfolder of the apps in the views folder
    output_folder = os.path.join("templates")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    #shutil.rmtree(output_folder) #delete all the subfolder of the apps in the views folder

    # --- Execution ---
    # Set the root path of your application module
    folders_apps=get_plugin_directories('apps')
    for app in folders_apps:
        build_app_views(app) 

        #---now we will to migrate the partials to the templates folder---
        migrate_partials_to_templates(app)


    #update all the cache of the date of the files
    with open(cacheFiles, 'w', encoding='utf-8') as file:
        #final_html_content+="\n" +replace_keyword(new_html, extension_dir)
        json.dump(container_files_cache, file, indent=4)

    print('All the plugins was upload with success')

