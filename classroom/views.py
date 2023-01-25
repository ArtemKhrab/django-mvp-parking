from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView 
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from .forms import CustomerForm, UserForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from .models import Customer,User, Place
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.hashers import make_password
from bootstrap_modal_forms.generic import (
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    return render(request, 'dashboard/login.html')


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    return render(request, 'dashboard/login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('home')    
    total_it = Customer.objects.aggregate(Sum("total_cost"))

    print(total_it.get("total_cost__sum"))
    total_it = total_it.get("total_cost__sum")

    total_cost = total_it

    cars = Customer.objects.all().count()
    users = User.objects.all().count()


    context = {'total_cost':total_cost, 'users':users, 'cars':cars}
    return render(request, 'dashboard/dashboard.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_cashier:
                return redirect('dashboard')
            else:
                return redirect('login')
        else:
            messages.error(request, 'Wrong Username or Password')
            return redirect('home')    
    return redirect('home')    

def logout_view(request):
    logout(request)
    return redirect('/')                


def add_vehicle(request):
    if not request.user.is_authenticated:
        return redirect('home') 
    return render(request, 'dashboard/add_vehicle.html')


def save_vehicle(request):
    if not request.user.is_authenticated:
        return redirect('home') 
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        card_number = request.POST['card_number']
        car_model = request.POST['car_model']
        car_color = request.POST['car_color']
        phone_number = request.POST['phone_number']
        comment = request.POST['comment']
        device = request.POST.get('device', '')
        cost_per_day = request.POST.get('cost_per_day', 50)
        register_name = request.POST['register_name']
        current_time = datetime.now()
        date_time = current_time.strftime("%Y,%m,%d")
        place = Place.objects.filter(booked=False).first()
        a = Customer(first_name=first_name, last_name=last_name, card_number=card_number, car_model=car_model, car_color=car_color, reg_date=date_time,register_name=register_name,comment=comment, cost_per_day=cost_per_day, device=device, place=place, phone_number=phone_number)
        place.booked = True
        place.save()
        a.save()
        messages.success(request, 'Vehicle Registered Successfully')
        return redirect('vehicle')


class ListVehicle(ListView):
    model = Customer
    template_name = 'dashboard/vehicles.html'
    context_object_name = 'customers'
    paginate_by = 2

    def get_queryset(self):
        return Customer.objects.filter(is_payed="True")


class UserView(ListView):
    model = User
    template_name = 'dashboard/list_user.html'
    context_object_name = 'users'
    paginate_by = 5

    def get_queryset(self):
        return User.objects.order_by('-id')



class Vehicle(ListView):
    model = Customer
    template_name = 'dashboard/list_vehicle.html'
    context_object_name = 'customers'
    paginate_by = 2

    def get_queryset(self):
        return Customer.objects.filter(is_payed="False")



class UserUpdateView(BSModalUpdateView):
    model = User
    template_name = 'dashboard/u_update.html'
    form_class = UserForm
    success_message = 'Success: Data was updated.'
    success_url = reverse_lazy('users')



class VehicleReadView(BSModalReadView):
    model = Customer
    template_name = 'dashboard/view_vehicle.html'


class CarReadView(BSModalReadView):
    model = Customer
    template_name = 'dashboard/view_vehicle2.html'

class UserReadView(BSModalReadView):
    model = User
    template_name = 'dashboard/view_user.html'

class VehicleUpdateView(BSModalUpdateView):
    model = Customer
    template_name = 'dashboard/update_vehicle.html'
    form_class = CustomerForm
    success_url = reverse_lazy('vehicle')


class CarUpdateView(BSModalUpdateView):
    model = Customer
    template_name = 'dashboard/update_vehicle2.html'
    form_class = CustomerForm
    success_url = reverse_lazy('listvehicle')



class VehicleDeleteView(BSModalDeleteView):
    model = Customer
    template_name = 'dashboard/delete_vehicle.html'
    form_class = CustomerForm
    success_url = reverse_lazy('vehicle')



class CarDeleteView(BSModalDeleteView):
    model = Customer
    template_name = 'dashboard/delete_vehicle2.html'
    form_class = CustomerForm
    success_url = reverse_lazy('listvehicle')
    success_message = 'Success: Data was deleted.'



def Pay(request, pk):
    if not request.user.is_authenticated:
        return redirect('home') 
    customer = Customer.objects.filter(id = pk).first()
    customer.exit_date = timezone.now()
    customer.is_payed = True
    myTime = datetime.strptime(str(customer.reg_date), "%Y-%m-%d %H:%M:%S.%f")
    myTime2 = datetime.strptime(str(customer.exit_date), "%Y-%m-%d %H:%M:%S.%f")

    d2 = myTime2.date()
    d1 = myTime.date()

    delta = d2 - d1
    mo = delta.days

    if mo == 0:
        mo =1
    else:
        mo = mo

    customer.days_spent = mo
    place = Place.objects.filter(id = customer.place.id).first()
    place.booked = False
    total_cost = customer.cost_per_day * mo
    customer.total_cost = total_cost
    customer.place.booked = False
    customer.save()
    place.save()
    messages.success(request, 'Payment Was Finished Successfully')
    
    return redirect('listvehicle')
  

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GeneratePdf(ListView):
    def get(self, request, pk, *args, **kwargs):
        infos = Customer.objects.filter(id=pk).values('id','first_name','last_name','total_cost','days_spent', 'reg_date', 'exit_date', 'card_number', 'place')
        context = {
        "data": {
            'location': 'Parking 1',
            'address': 'Kyiv, Peremohy ave, 71',
            'email': 'info@kyivparking.com',
        },
        "infos": infos,
        }

        pdf = render_to_pdf('dashboard/invoice.html', context)
        return HttpResponse(pdf, content_type='application/pdf')


class GeneratePDF(LoginRequiredMixin,ListView):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        context = {}
        pdf = render_to_pdf('dashboard/invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class DeleteUser(BSModalDeleteView):
    model = User
    template_name = 'dashboard/delete_user.html'
    success_message = 'Success: Data was deleted.'
    success_url = reverse_lazy('users')


def create(request):
    if not request.user.is_authenticated:
        return redirect('home') 
    choice = ['1', '0', 5000, 10000, 15000, 'Register', 'Admin', 'Cashier']
    choice = {'choice': choice}
    if request.method == 'POST':
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            username=request.POST['username']
            userType=request.POST['userType']
            email=request.POST['email']
            password=request.POST['password']
            password = make_password(password)
            print("User Type")
            print(userType)
            if userType == "Register":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_register=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('users')
            elif userType == "Cashier":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_cashier=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('users')
            elif userType == "Admin":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_admin=True)
                a.save()
                messages.success(request, 'Member was created successfully!')
                return redirect('users')    
            else:
                messages.success(request, 'Member was not created')
                return redirect('users')
    














































































































































   



