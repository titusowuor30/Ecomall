from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from decimal import Decimal
from .mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment
import random,math
import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .cart import Cart
from .forms import CheckoutForm
from apps.order.utilities import checkout, notify_customer, notify_vendor

def cart_detail(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY

            stripe_token = form.cleaned_data['stripe_token']

            try:
                charge = stripe.Charge.create(
                    amount=int(cart.get_total_cost() * 100),
                    currency='USD',
                    description='Charge from Interiorshop',
                    source=stripe_token
                )

                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data['address']
                postal_code = form.cleaned_data['postal_code']
                city = form.cleaned_data['city']

                order = checkout(request, first_name, last_name, email, address, postal_code, city, phone,
                                 cart.get_total_cost())

                cart.clear()

                notify_customer(order)
                notify_vendor(order)

                return redirect('success')
            except Exception:
                messages.error(request, 'There was something wrong with the payment')
    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout-page.html', {'form': form, 'stripe_pub_key': settings.STRIPE_PUB_KEY})

def show_cart(request):
    cart=Cart(request)

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)

        return redirect('cart')

    if change_quantity:
        cart.add(change_quantity, quantity, True)

        return redirect('cart')
    return render(request, 'cart/cart.html')

def success(request):
    return render(request, 'cart/success.html')


def payment(request):
    return render(request, 'cart/payment.html')

def getAccessToken(request):
    consumer_key = 'cHnkwYIgBbrxlgBoneczmIJFXVm0oHky'
    consumer_secret = '2nHEyWSD4VjpNh2g'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request):
    cart=Cart(request)
    print(cart.get_total_cost())

    if request.method=='POST':
        phone=request.POST.get('phone','')

        if phone:
           phone_no=(int)(phone)
    print(phone,phone_no)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount":cart.get_total_cost(),
        "PartyA": phone_no,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone_no,  # replace with your phone number to get stk push
        "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": "Ecomall",
        "TransactionDesc": "Charge from Ecomall"
    }

    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('Payment Sucess!')


@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://79372821.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://79372821.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],

    )
    payment.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))

