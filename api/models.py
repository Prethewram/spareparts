from django.db import models
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

# Custom user manager

class User(models.Model):
    user_id=models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=12)
    email = models.EmailField(max_length=100, unique=True)
    phone_number=models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users_table"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    class Meta:
        db_table = "users_table"

# Address model
class Address(models.Model):
    address_id=models.AutoField(primary_key=True)
    user_id= models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)
    address = models.TextField()
    pin_code = models.CharField(max_length=10)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True)

# Vehicle related models

class MainCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=50)
    main_category=models.ForeignKey(MainCategory,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='brand_images/')
    is_electric= models.BooleanField(null=False,blank=False)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicle_images/')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='vehicle_brand')  
    vehicle_category=models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    electric= models.BooleanField(null=True,blank=True)
    def __str__(self):
        return self.name
    

class SubVehicle_car(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='sub_vehicles_car', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_images/')
    name = models.CharField(max_length=100)
    version_fuel_type = models.CharField(max_length=100, null=False)
    model_year = models.IntegerField()
    electric= models.BooleanField(null=True,blank=True)

class Subvehicle_bike(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='sub_vehicles_bike', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_images/')
    name = models.CharField(max_length=100)
    model_year = models.IntegerField()
    electric= models.BooleanField(null=True,blank=True)
    def __str__(self):
        return self.name

# Product related model
class Category(models.Model):
    image = models.ImageField(upload_to='category_images/')
    name = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(MainCategory, on_delete=models.CASCADE, null=False, blank=False)
    subvehicle_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    subvehicle_id = models.PositiveIntegerField(null=True, blank=True)
    subvehicle = GenericForeignKey('subvehicle_type', 'subvehicle_id')
    def __str__(self):
        return self.name
    

class Quality(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='products')
    main_vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='vehicles',default=1)
    subvehicle_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    subvehicle_id = models.PositiveIntegerField(null=True, blank=True)
    subvehicle = GenericForeignKey('subvehicle_type', 'subvehicle_id')
    created_at = models.DateTimeField(auto_now_add=True)
    product_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  
    product_offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=False, blank=False)

    def save(self, *args, **kwargs):
        discount_percentage = Decimal(self.product_discount_percentage)
        price = Decimal(self.price)
        self.product_offer_price = price * (1 - discount_percentage / Decimal('100'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
   
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.title} Image"
    


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

# Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.firstname

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product.title} ({self.quantity})'

# Order Model
class Order(models.Model):
    order_id = models.CharField(max_length=20,unique=True)
    cart_id= models.ForeignKey(Cart, on_delete=models.CASCADE)
    address_id= models.ForeignKey(Address, on_delete=models.CASCADE)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

    class Meta:
        db_table = "order_table"

# Payment Model
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=255, choices=(
        ('UPI Payment', 'UPI Payment'),
        ('Card', 'Credit/Debit Cards'),
        ('COD','Cash On Delivery'),
    ))
    payment_status = models.CharField(max_length=20, choices=[
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.order_id


class AccessoryProducts(models.Model):
    ACCESSORY_TYPE_CHOICES = [
        ('Bike', 'Bike Accessory'),
        ('Car', 'Car Accessory'),
    ]
    accessory_type = models.CharField(max_length=20, choices=ACCESSORY_TYPE_CHOICES)
    accessory_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False,null=True)

    def _str_(self):
        return self.accessory_name

class AccessoryImages(models.Model):
    accessory = models.ForeignKey(AccessoryProducts, on_delete=models.CASCADE, related_name='accessory_images')
    image = models.ImageField(upload_to='accessory_images/')

    def _str_(self):
        return f"{self.accessory.accessory_name}Image"
    


class CarouselImage(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(upload_to='carousel_images/')
    caption = models.TextField(blank=True, null=True)