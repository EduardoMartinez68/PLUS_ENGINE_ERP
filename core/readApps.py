import os
from dotenv import load_dotenv
import yaml
from pathlib import Path

APPS_CACHE = []
APPS_FOLDER=[]
APPS_NAME=[]

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def read_all_my_apps():
    apps_dir = os.path.join(os.getcwd(), 'apps')
    apps = []

    #if exist the app folder, we will read all the apps in his inside
    if os.path.exists(apps_dir):
        for name in os.listdir(apps_dir):
            path_app = os.path.join(apps_dir, name)
            
            if os.path.isdir(path_app):
                #get the file of config
                pathFile=os.path.join(path_app, 'config.yaml')
                config=read_the_config_of_the_app(pathFile) #her we will read the file of config and get his data
                apps.append(config) #save the data of the app
                APPS_NAME.append(f'apps.{name}')
                APPS_FOLDER.append(path_app)

    sortApps=sort_all_apps_based_on_their_dependencies(apps)

    print(f"{len(apps)} apps load was success")
    
    return apps



def sort_all_apps_based_on_their_dependencies(apps):
    # Filtramos None y preparamos dict para acceso rápido
    apps = [app for app in apps if app]
    app_dict = {app['name']: app for app in apps}

    # Grafo de dependencias: clave = app, valores = apps que dependen de ella
    from collections import defaultdict, deque

    graph = defaultdict(list)
    indegree = {app['name']: 0 for app in apps}

    # Construimos grafo e indegrees
    for app in apps:
        for dep in app.get('depends', []):
            if dep not in app_dict:
                raise ValueError(f"Dependencia '{dep}' de '{app['name']}' no existe.")
            graph[dep].append(app['name'])
            indegree[app['name']] += 1

    # Cola para apps sin dependencias (indegree 0)
    queue = deque([name for name, deg in indegree.items() if deg == 0])

    sorted_apps = []
    while queue:
        current = queue.popleft()
        sorted_apps.append(app_dict[current])

        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    # Si no se procesaron todas, hay ciclo
    if len(sorted_apps) != len(apps):
        raise ValueError("Error: Dependencias cíclicas detectadas.")

    return sorted_apps

def read_the_config_of_the_app(pathFile):
    #her we will read the file of config
    if os.path.exists(pathFile):
        with open(pathFile) as f:
            config = yaml.safe_load(f)
            return {
                'name': config.get('name', ''),
                'appName': config.get('appName', ''),
                'icon': config.get('icon', ''),
                'path': config.get('path', ''),
                'depends': config.get('depends', [])
            }

def get_order_apps():
    path_file=os.path.join('apps', 'ordering.yaml')
    if not os.path.exists(path_file):
        return []

    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
            # get the list of order apps
            return data.get("app_order", [])
    except Exception as e:
        print(f"Error to read the YAML: {e}")
        return []
    
def sort_apps_by_order(original_list, order_list):
    # 1. We created a priority map for quick search
    # We assigned an index: schedule=0, employees=1, patients=2
    priority_map = {name: index for index, name in enumerate(order_list)}
    
    # 2. We define a "key" function for sorting
    def sort_key(app):
        name = app.get('name')
        # If the app is on the order list, we return its index (0, 1, 2...)
        # If it's NOT on the list, we return a very high number to send it to the end.
        return priority_map.get(name, float('inf'))

    # 3. We sort the original list using that key
    # `sorted()` creates a new list, `.sort()` sorts the same list.
    return sorted(original_list, key=sort_key)

#save all the apps in cache for not read forever all the apps. Only read all the apps when run the server
APPS_CACHE = sort_apps_by_order(read_all_my_apps(), get_order_apps())
APPS_FOLDER = [Path(folder) for folder in APPS_FOLDER] #her we will conver the string to path