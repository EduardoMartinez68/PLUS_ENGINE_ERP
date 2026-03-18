#here we will to get the plugins of the views that need users
from django.db import transaction
from apps.customers.services.forms import CustomerForm

class CustomerService:
    @staticmethod
    @transaction.atomic

    #-------------------------------------------------------------------------#
    # here we will to create all the logic to handle the create of a customer
    #1. Get all the forms of the plugins
    #2. Validate the main form of customer and the forms of the plugins
    #3. Save the customer and the plugins data
    #-------------------------------------------------------------------------#
    def handle_create(request):
        #first we will get all the form of the plugins
        plugin_forms = [
            (plugin, plugin.get_form(request)) 
            for plugin in plugins.get_plugins()
        ]

        if request.method == 'POST' and CustomerForm.is_valid():
            #save the customer in the form
            #customer=customer.save()

            #now we will to read all the plugins and save their data
            for plugin, form in plugin_forms:
                if form and form.is_valid():
                    #if the form is valid we will to save the data using the plugin
                    plugin.process_create(request, form.cleaned_data)
