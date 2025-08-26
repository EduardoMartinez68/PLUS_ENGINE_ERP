import psycopg2
import os
from dotenv import load_dotenv
import yaml
from pathlib import Path

APPS_CACHE = []
APPS_FOLDER=[]
APPS_NAME=[]

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
conn_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS')
}

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
    create_the_body_of_the_database_of_the_erp()
    run_the_sql_of_the_database_of_all_the_apps(sortApps,apps_dir)

    print(f"{len(apps)} apps load was success")
    
    return apps


def create_the_body_of_the_database_of_the_erp():
    #connect with the DB
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    #get the body of the database
    sql_path = os.path.join(os.getcwd(),'database', 'database.sql')

    #we will see if exist the file database
    if os.path.exists(sql_path):
        print(f"Run the body of the database")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        try:
            cur.execute(sql)
            conn.commit()
            print(f"Body of the database run with success.")
        except Exception as e:
            conn.rollback()
            print(f"Error to run the body of the SQL {e}")
    else:
        print(f"Not exist the file SQL for create the body of the database")

    cur.close()
    conn.close()

def run_the_sql_of_the_database_of_all_the_apps(sorted_apps, base_dir):
    """
    run all the file SQL of all the apps in sort

    Args:
        sorted_apps (list): ordered list of apps (dictionaries).
        base_dir (str): base path where the app folders are located.
        conn_params (dict): parameters for connecting to PostgreSQL.
    

    #connect with the DB
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    for app in sorted_apps:
        app_name = app['name']

        #Assuming the sql file is in base_dir/app_name/init.sql
        sql_path = os.path.join(base_dir, app_name.lower(), 'db.sql')

        #we will see if exist the file database
        if os.path.exists(sql_path):
            print(f"Ejecutando SQL para {app_name} desde {sql_path}")
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql = f.read()

            try:
                cur.execute(sql)
                conn.commit()
                print(f"SQL of {app_name} run with success.")
            except Exception as e:
                conn.rollback()
                print(f"Error to run the SQL of {app_name}: {e}")
        else:
            print(f"Not exist the file SQL for {app_name} in {sql_path}")

    cur.close()
    conn.close()
    """

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


#save all the apps in cache for not read forever all the apps. Only read all the apps when run the server
APPS_CACHE = read_all_my_apps()
APPS_FOLDER = [Path(folder) for folder in APPS_FOLDER] #her we will conver the string to path