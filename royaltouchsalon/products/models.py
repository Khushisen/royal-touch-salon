from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User



class Category(models.Model):
    category_name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length=200,blank=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category,self).save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name    
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=False,blank=False)
    product_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.product_name
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'
    
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    address = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"