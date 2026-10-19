#here we will to get the plugins of the views that need users
from django.db import transaction
from core.plugins.registry import plugins

class DashboardService:
    @staticmethod
    @transaction.atomic

    #-------------------------------------------------------------------------#
    # here we will to create all the logic to handle the create of a customer
    #1. Get all the forms of the plugins
    #2. Validate the main form of customer and the forms of the plugins
    #3. Save the customer and the plugins data
    #-------------------------------------------------------------------------#
    def get_information(request, data=None):
        information_list=[] #here we will to save all the information from the plugins
        #first we will get all the plugins for get information in the dashboard
        for plugin in plugins.get_plugins(module="dashboard",action="view_information_dashboard",request=request,data=data):
            #get the information of the plugin use the method 
            information=plugin.get_information(request, data)

            #when get the information of the plugin we will to save in the list his the name of the plugin and the information
            #this for that afther we can to show the information in the dashboard use the key of the plugin
            information_list.append(information)

        return information_list
    

    def get_information_of_a_plugin(request, plugin_name, data=None):
        information_list=[] #here we will to save all the information from the plugins
        #first we will get all the plugins for get information in the dashboard
        for plugin in plugins.get_plugins(module="dashboard",action="view_information_dashboard",request=request,data=data):
            if plugin.name == plugin_name:
                #get the information of the plugin use the method 
                information=plugin.get_information(request, data)

                #when get the information of the plugin we will to save in the list his the name of the plugin and the information
                #this for that afther we can to show the information in the dashboard use the key of the plugin
                information_list.append({plugin.name: information})
                return information_list

        return information_list