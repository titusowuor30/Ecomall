from django.shortcuts import render,redirect
from  django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from apps.product.models import Product

def home(request):
    products=Product.objects.all()
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'core/home.html',{'products':products,'page_obj':page_obj})

def user_register(request):
    if request.method=='GET':
        form=UserCreationForm()
        return render(request,'core/user-register.html',{'form':form})
    else:
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,'user registration successfull!')
            return redirect('frontpage')