from django.urls import path, include
from . import views
from core.readApps import APPS_FOLDER

urlpatterns = [
    path('', views.home, name='home'), #this is the home of the ERP
]

#We dynamically add the includes for each app
for app_path in APPS_FOLDER:
    #get the name of the app (last folder)
    app_name = app_path.name  # if it is Path, if it is string use os.path.basename()
    
    # We build the string to include, e.g. 'apps.cases.urls'
    include_path = f'apps.{app_name}.urls'
    
    #We add to urlpatterns
    urlpatterns.append(path(f'{app_name}/', include(include_path)))