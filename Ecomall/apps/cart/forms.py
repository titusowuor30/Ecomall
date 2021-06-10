from django import forms

PAYMENT_CHOICES=(('M','M-pesa'),('P','Paypal'),('S','Stripe'))
class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)
    phone = forms.CharField(max_length=255)
    address = forms.CharField(max_length=255)
    postal_code = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    stripe_token = forms.CharField(max_length=255,required=False)