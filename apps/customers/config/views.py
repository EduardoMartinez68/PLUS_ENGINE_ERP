#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from database.models import Customer
from django.shortcuts import render, redirect
@login_required(login_url='login')
def customers_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        id_branch = request.user.id_branch
    
        # Traer los primeros 20 resultados de ese branch ordenados por ID
        customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})
    else:
        id_branch = request.user.id_branch
    
        # Traer los primeros 20 resultados de ese branch ordenados por ID
        customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})

@login_required(login_url='login')
def add_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            name = request.POST.get('name', '').strip() #the name not can is null
            email = request.POST.get('email')
            is_company = request.POST.get('this_customer_is_a_company') == 'on'
            company_name = request.POST.get('company_name')
            rfc = request.POST.get('rfc')
            curp = request.POST.get('curp')
            phone = request.POST.get('phone')
            cellphone = request.POST.get('cellphone')
            website = request.POST.get('website')
            country = request.POST.get('country')
            status = request.POST.get('status') == 'on'
    
    
            if not name:
                messages.error(request, 'El nombre del cliente es obligatorio.')
                return render(request, 'addCustomer.html')
            
    
            #get the if of the user
            id_branch = request.user.id_branch
            creation_date=datetime.now()
            #her we will save the new customer with the model of Django 
            try:
                customer = Customer(
                    id_branch=id_branch,
                    name=name,
                    email=email,
                    this_customer_is_a_company=is_company,
                    company_name=company_name,
                    rfc=rfc,
                    curp=curp,
                    phone=phone,
                    cellphone=cellphone,
                    website=website,
                    country=country,
                    status=status,
                    creation_date=creation_date
                )
    
                customer.save()
                #now send to the user to other path
                messages.success(request, 'El cliente fue agregado exitosamente.')
                return redirect('/')
            except Exception as e:
                print('---------------------have a error when the user add a customer:')
                print(e)
                messages.error(request, f'Error al guardar el cliente: {str(e)}')
                return redirect('/')
    
    
        return render(request, 'addCustomer.html')
    else:
        if request.method == 'POST':
            name = request.POST.get('name', '').strip() #the name not can is null
            email = request.POST.get('email')
            is_company = request.POST.get('this_customer_is_a_company') == 'on'
            company_name = request.POST.get('company_name')
            rfc = request.POST.get('rfc')
            curp = request.POST.get('curp')
            phone = request.POST.get('phone')
            cellphone = request.POST.get('cellphone')
            website = request.POST.get('website')
            country = request.POST.get('country')
            status = request.POST.get('status') == 'on'
    
    
            if not name:
                messages.error(request, 'El nombre del cliente es obligatorio.')
                return render(request, 'addCustomer.html')
            
    
            #get the if of the user
            id_branch = request.user.id_branch
            creation_date=datetime.now()
            #her we will save the new customer with the model of Django 
            try:
                customer = Customer(
                    id_branch=id_branch,
                    name=name,
                    email=email,
                    this_customer_is_a_company=is_company,
                    company_name=company_name,
                    rfc=rfc,
                    curp=curp,
                    phone=phone,
                    cellphone=cellphone,
                    website=website,
                    country=country,
                    status=status,
                    creation_date=creation_date
                )
    
                customer.save()
                #now send to the user to other path
                messages.success(request, 'El cliente fue agregado exitosamente.')
                return redirect('/')
            except Exception as e:
                print('---------------------have a error when the user add a customer:')
                print(e)
                messages.error(request, f'Error al guardar el cliente: {str(e)}')
                return redirect('/')
    
    
        return render(request, 'addCustomer.html')

