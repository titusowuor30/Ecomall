from io import BytesIO
from PIL import Image

from django.core.files import File
from django.db import models

from apps.vendor.models import Vendor

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordering']
    
    def __str__(self):
        return self.title

class Product_Images(models.Model):
    image=models.ImageField(upload_to='media/uploads/')

    def __str__(self):
        return self.image.url

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    product_images=models.ForeignKey(Product_Images,related_name='products',on_delete=models.CASCADE, blank=True, null=True)
    #thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    @property
    def getImageURL(self):
        if self.image.url and hasattr(self.image,'url'):
            return self.image.url
        else:
            return 'media/uploads/gallery-6.jpg'

    class Meta:
        ordering = ['-date_added']
    
    def __str__(self):
        return self.title


