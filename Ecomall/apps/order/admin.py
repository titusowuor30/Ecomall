from django.contrib import admin

from .models import Order, OrderItem,Payment_method

admin.site.register(Order)
admin.site.register(OrderItem)

class PaymentMethodAdmin(admin.ModelAdmin):
    fields = ('title','slug')
admin.site.register(Payment_method,PaymentMethodAdmin)