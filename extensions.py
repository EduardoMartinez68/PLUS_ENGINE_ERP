import os
import glob
import minify_html

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

def build_app_views(app_path):
    """
    Main function to merge core HTML files with plugin extensions.
    It reads base views from 'core' and appends extra HTML from each plugin's 'extensions'.
    """
    # 1. Define base paths
    core_folder = os.path.join(app_path, "core")
    plugins_base_folder = os.path.join(app_path, "plugins")
    output_folder = os.path.join(app_path, "views")
    
    # 2. Get all available plugin directories
    available_plugins = get_plugin_directories(plugins_base_folder) 

    # 3. Locate all base HTML files in the core folder
    # We use normpath to prevent issues with mixed slashes (/ vs \)
    core_search_pattern = os.path.normpath(os.path.join(core_folder, "*.html"))
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
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        try:
            optimized_html = minify_html.minify(
                final_html_content,
                minify_js=True,
                minify_css=True,
                remove_processing_instructions=True
            )
        except Exception as e:
            print(f"Error minifying: {e}")
            optimized_html = final_html_content # if not can Minification the new code use the origin

        final_output_path = os.path.join(output_folder, filename)
        with open(final_output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(optimized_html)
            
        print(f"Successfully built view: {view_name} -> {final_output_path}")

# --- Execution ---
# Set the root path of your application module
app_root = "apps/customers"
build_app_views(app_root)