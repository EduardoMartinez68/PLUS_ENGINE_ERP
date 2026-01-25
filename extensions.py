import os
import glob
import json
import shutil

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
        # Get filename without extension for matching (e.g., 'home')
        view_name, _ = os.path.splitext(filename)

        # Read the primary content from the core view
        with open(file_path, 'r', encoding='utf-8') as f:
            final_html_content = f.read()

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
                        final_html_content += "\n" + fe.read()

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
        with open(final_output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(optimized_html)


    #Now we will to create the locale files merging the core with the plugins locale files
    create_the_file_locale(app_path, core_folder, plugins_base_folder)

def load_plugins_and_extensions():
    #1. Create the folder templates if not exist and when exist delete all the subfolder of the apps in the views folder
    output_folder = os.path.join("templates")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    shutil.rmtree(output_folder) #delete all the subfolder of the apps in the views folder

    # --- Execution ---
    # Set the root path of your application module
    folders_apps=get_plugin_directories('apps')
    for app in folders_apps:
        build_app_views(app) 

    print('All the plugins was upload with success')
