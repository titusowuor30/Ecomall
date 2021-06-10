from django.contrib import admin

from .models import Category, Product,Product_Images

admin.site.register(Category)

class ProductImageAdmin(admin.StackedInline):
    model = Product_Images
admin.site.register(Product)

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

    class Meta:
        model=Product
admin.site.register(Product_Images)