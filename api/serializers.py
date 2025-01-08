from rest_framework import serializers
from.models import *
import random
import datetime
from django.contrib.auth.hashers import make_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'phone_number', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))
        otp_created_at = datetime.datetime.now()

        user = User(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            otp=otp,
            otp_created_at=otp_created_at
        )
        user.save()
        return user
    

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=10, required=False)
    password = serializers.CharField(max_length=100)


    def validate(self, data):
        email = data.get('email')
        phone_number = data.get('phone_number')
        if not email and not phone_number:
            raise serializers.ValidationError("Either email or phone number is required")
        return data

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'firstname', 'lastname','email','phone_number']


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    otp = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self):
        email = self.validated_data['email']
        otp = self.validated_data['otp']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        # Hash the new password before saving
        user.password = new_password
        user.save()
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'firstname', 'lastname', 'email', 'phone_number']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = ['id', 'name']

class BrandSerializer(serializers.ModelSerializer):
    main_category = MainCategorySerializer(read_only=True)  
    main_category_id = serializers.PrimaryKeyRelatedField(queryset=MainCategory.objects.all(), source='main_category', write_only=True) 

    class Meta:
        model = Brand
        fields = ['id', 'name', 'main_category', 'main_category_id', 'image', 'is_electric']


class VehicleSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source='brand', write_only=True)
    vehicle_category = MainCategorySerializer(read_only=True)
    vehicle_category_id = serializers.PrimaryKeyRelatedField(queryset=MainCategory.objects.all(), source='vehicle_category', write_only=True)
    electric = serializers.BooleanField(required=True)

    class Meta:
        model = Vehicle
        fields = ['id' ,'name', 'image', 'brand','brand_id', 'vehicle_category', 'vehicle_category_id', 'electric']


class SubvehicleBikeSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.SerializerMethodField()
    electric = serializers.BooleanField()

    class Meta:
        model = Subvehicle_bike
        fields = ['id', 'vehicle','vehicle_name','image', 'name', 'model_year', 'electric']

    
    def get_vehicle_name(self, obj):
        return obj.vehicle.name

class SubvehicleCarSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.SerializerMethodField()
    electric = serializers.BooleanField()


    class Meta:
        model = SubVehicle_car
        fields = ['id', 'vehicle', 'vehicle_name', 'image', 'name', 'model_year', 'version_fuel_type', 'electric']

    def get_vehicle_name(self, obj):
        return obj.vehicle.name



class CategorySerializer(serializers.ModelSerializer):
    subvehicle_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(), slug_field='model'
    )
    subvehicle_id = serializers.IntegerField()
    subvehicle = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'image', 'name', 'vehicle_type', 'subvehicle_type', 'subvehicle_id', 'subvehicle']

    def get_subvehicle(self, obj):
        if obj.subvehicle:
            if obj.subvehicle_type.model == 'subvehicle_car':
                return SubvehicleCarSerializer(obj.subvehicle).data
            elif obj.subvehicle_type.model == 'subvehicle_bike':
                return SubvehicleBikeSerializer(obj.subvehicle).data
        return None


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quality
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','product','image']

class ProductSerializer(serializers.ModelSerializer):
    subvehicle_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(), slug_field='model'
    )
    subvehicle_id = serializers.IntegerField()
    subvehicle = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    brand = serializers.SlugRelatedField(queryset=Brand.objects.all(), slug_field='name')
    quality = serializers.SlugRelatedField(queryset=Quality.objects.all(), slug_field='name', required=True, allow_null=True)


    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'description', 'category', 'main_category', 'brand', 'subvehicle_type', 'subvehicle_id', 'subvehicle', 'images','quality','created_at']

    def get_subvehicle(self, obj):
        if obj.subvehicle:
            if obj.subvehicle_type.model == 'subvehicle_car':
                return SubvehicleCarSerializer(obj.subvehicle).data
            elif obj.subvehicle_type.model == 'subvehicle_bike':
                return SubvehicleBikeSerializer(obj.subvehicle).data
        return None


class ReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    product = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product_id', 'product', 'user_id', 'user', 'rating', 'comment', 'created_at']

# Cart related serializers

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product', 'quantity', 'cart']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_id', 'updated_at', 'items']

class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer(source='cart_id')
    address = AddressSerializer(source='address_id') 

    class Meta:
        model = Order
        fields = ['order_id', 'cart', 'address', 'user_id', 'total_amount', 'delivery_charges', 'coupon_discount', 'created_at']

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['cart_id', 'address_id', 'user_id', 'total_amount', 'delivery_charges', 'coupon_discount']


class AccessoryImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessoryImages
        fields = ['id', 'image']

class AccessoryProductsSerializer(serializers.ModelSerializer):
    discount_percentage=serializers.CharField(required=True) 
    offer_price = serializers.DecimalField(required=True,max_digits=10, decimal_places=2)
    accessory_images = AccessoryImagesSerializer(many=True, read_only=True)
    accessory_image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True
    )

    class Meta:
        model = AccessoryProducts
        fields = ['id', 'accessory_type', 'accessory_name', 'price', 'description', 'offer_price', 'accessory_images', 'accessory_image_files','discount_percentage']

    def create(self, validated_data):
        accessory_image_files = validated_data.pop('accessory_image_files')
        accessory_product = AccessoryProducts.objects.create(**validated_data)
        for image_file in accessory_image_files:
            AccessoryImages.objects.create(accessory=accessory_product, image=image_file)
        return accessory_product   

    def update(self, instance, validated_data):
        accessory_image_files = validated_data.pop('accessory_image_files', [])
        instance = super().update(instance, validated_data)
        
        instance.accessory_images.all().delete()
        
        for image in accessory_image_files:
            AccessoryImages.objects.create(accessory=instance, image=image)
        return instance
    




class CarouselImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=CarouselImage
        fields='__all__'