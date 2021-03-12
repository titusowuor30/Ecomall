from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Vendor
from apps.product.models import Product

from .forms import ProductForm

def become_vendor(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            vendor = Vendor.objects.create(name=user.username, created_by=user)

            return redirect('frontpage')
    else:
        form = UserCreationForm()

    return render(request, 'vendor/become_vendor.html', {'form': form})

@login_required
def vendor_admin(request):
    vendor = request.user.vendor
    products = vendor.products.all()
    orders = vendor.orders.all()

    for order in orders:
        order.vendor_amount = 0
        order.vendor_paid_amount = 0
        order.fully_paid = True

        for item in order.items.all():
            if item.vendor == request.user.vendor:
                if item.vendor_paid:
                    order.vendor_paid_amount += item.get_total_price()
                else:
                    order.vendor_amount += item.get_total_price()
                    order.fully_paid = False

    return render(request, 'vendor/vendor_admin.html', {'vendor': vendor, 'products': products, 'orders': orders})

@login_required()
def add_product(request,id=0):
    vendor=request.user.vendor

    if request.method=='GET':
        if id==0:
            form=ProductForm()
        else:
            prdct=vendor.products.get(pk=id)
            form=ProductForm(instance=prdct)
        return render(request,'vendor/add_product.html',{'form':form})
    else:
        if id==0:
            form=ProductForm(request.POST,request.FILES)              #Explain
            messages.success(request,'Product added successfully')
        else:
            prdct = request.user.vendor.products.get(pk=id)
            form= ProductForm(request.POST,request.FILES,instance=prdct)
            messages.success(request,'Product updated successfully')

        if form.is_valid():
            prdct = form.save(commit=False)
            prdct.vendor = request.user.vendor
            prdct.slug = slugify(prdct.title)
            prdct.save()

        return redirect('vendor_admin')


@login_required
def delete_product(request,id):
    prdct = request.user.vendor.products.get(pk=id)
    prdct.delete()
    messages.success(request,'Product deleted successfully')
    return redirect('vendor_admin')

@login_required
def edit_vendor(request):
    vendor = request.user.vendor

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')

        if name:
            vendor.created_by.email = email
            vendor.created_by.save()

            vendor.name = name
            vendor.save()
            messages.success(request, 'Vendor account details edited successfully')
            return redirect('vendor_admin')

    return render(request, 'vendor/edit_vendor.html', {'vendor': vendor})

def vendors(request):
    vendors = Vendor.objects.all()

    return render(request, 'vendor/vendors.html', {'vendors': vendors})

def vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)

    return render(request, 'vendor/vendor.html', {'vendor': vendor})