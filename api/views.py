from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics,filters
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from .filters import *
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets




# Create your views here.

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send OTP email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {user.otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "User registered successfully. OTP sent to email."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
                if user.otp == otp:
                    # OTP is correct, you can now mark the user as verified, etc.
                    user.is_verified = True
                    user.save()
                    return Response({"message": "OTP verified successfully."},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid OTP."},
                                    status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "User not found."},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone_number = serializer.validated_data.get('phone_number')
            password = serializer.validated_data.get('password')

            try:
                if email:
                    user = User.objects.get(email=email)
                elif phone_number:
                    user = User.objects.get(phone_number=phone_number)
                else:
                    return Response({'error': 'Email or phone number required'}, status=status.HTTP_400_BAD_REQUEST)


                if user.password != password:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

                # Set user_id in session
                request.session['user_id'] = user.user_id

                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                user.otp = otp
                user.otp_created_at = datetime.datetime.now()
                user.save()

                # Send OTP email
                send_mail(
                    'Your OTP Code for Password Change',
                    f'Your OTP code is {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def post(self, request):
        # Clear the session data
        request.session.flush()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_users(request):
    users = User.objects.all()
    serializer = UserDetailSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_detail_get(request, user_id):
    user = User.objects.get(user_id=user_id)
    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

@api_view([ 'PUT'])
def user_detail_update(request, user_id):
    user = User.objects.get(user_id=user_id)
    if request.method == 'PUT':
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def user_detail_delete(request, user_id):
    user = User.objects.get(user_id=user_id)
    if request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Address

@api_view(['GET'])
def list_addresses(request):
    addresses = Address.objects.all()
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_address(request):
    if request.method == 'POST':
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    serializer = AddressSerializer(address)
    return Response(serializer.data)

@api_view(['PUT'])
def update_address(request, address_id):
    try:
        address = Address.objects.get(pk=address_id)
    except Address.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    if request.method == 'DELETE':
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MainCategoryListCreateView(generics.ListCreateAPIView):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer

class MainCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class BrandListByMainCategoryView(generics.ListAPIView):
    serializer_class = BrandSerializer

    def get_queryset(self):
        main_category_id = self.kwargs['main_category_id']
        return Brand.objects.filter(main_category_id=main_category_id)
    
class VehicleListByBrandAndCategoryView(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        main_category_id = self.kwargs['main_category_id']
        brand_id = self.kwargs['brand_id']
        return Vehicle.objects.filter(brand_id=brand_id, brand__main_category_id=main_category_id)
    
class VehicleListByBrandView(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        brand_id = self.kwargs['brand_id']
        return Vehicle.objects.filter(brand_id=brand_id)

class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]

class VehicleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class QualityListView(generics.ListCreateAPIView):
    queryset = Quality.objects.all()
    serializer_class = QualitySerializer

class QualityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quality.objects.all()
    serializer_class = QualitySerializer


@api_view(['GET'])
def product_categories_by_vehicle(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response({"error": "Vehicle not found."}, status=404)

    products = Product.objects.filter(vehicle=vehicle)
    categories = Category.objects.filter(products__in=products).distinct()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        main_category_id = self.request.query_params.get('main_category_id', None)
        brand_name = self.request.query_params.get('brand', None)
        subvehicle_type = self.request.query_params.get('subvehicle_type', None)
        subvehicle_id = self.request.query_params.get('subvehicle_id', None)

        if main_category_id:
            queryset = queryset.filter(main_category_id=main_category_id)
        if brand_name:
            queryset = queryset.filter(brand__name=brand_name)
        if subvehicle_type and subvehicle_id:
            queryset = queryset.filter(subvehicle_type__model=subvehicle_type, subvehicle_id=subvehicle_id)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save()

class ProductListCreateByMainCategoryView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        main_category_id = self.kwargs['main_category_id']
        return Product.objects.filter(main_category_id=main_category_id)

    def perform_create(self, serializer):
        main_category_id = self.kwargs['main_category_id']
        main_category = MainCategory.objects.get(id=main_category_id)
        serializer.save(main_category=main_category)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]


class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()

class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class ProductDetailByFiltersView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_object(self):
        vehicle_id = self.kwargs['vehicle_id']
        subvehicle_type = self.kwargs['subvehicle_type']
        subvehicle_id = self.kwargs['subvehicle_id']
        category_id = self.kwargs['category_id']

        content_type = ContentType.objects.get(model=subvehicle_type)
        
        # Filtering the product based on the provided parameters
        return Product.objects.get(
            main_vehicle_id=vehicle_id,
            subvehicle_type=content_type,
            subvehicle_id=subvehicle_id,
            category_id=category_id
        )
    
class ProductdetailByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category_id=category_id)


class VehicleListByMainCategoryAndBrand(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        main_category_id = self.kwargs['main_category_id']
        brand_id = self.kwargs['brand_id']
        
        queryset = Vehicle.objects.filter(
            vehicle_category_id=main_category_id,
            brand_id=brand_id
        )
        return queryset
    

class VehicleListByMainCategory(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        main_category_id = self.kwargs['main_category_id']
        
        queryset = Vehicle.objects.filter(
            vehicle_category_id=main_category_id,
        )
        return queryset


@api_view(['GET'])
def products_by_vehicle_and_category(request, vehicle_id, category_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response({"error": "Vehicle not found."}, status=404)

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"error": "Category not found."}, status=404)

    products = Product.objects.filter(vehicle=vehicle, category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)

class CartListCreateView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemListCreateView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class UserCartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        return Cart.objects.get(user_id=user_id)
    
# Filter

@api_view(['GET'])
def products_by_vehicle(request, vehicle_id):
    try:
        products = Product.objects.filter(vehicle=vehicle_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"message": "Products not found for this vehicle"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def products_by_brand(request, brand_id):
    try:
        products = Product.objects.filter(brand=brand_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"message": "Products not found for this brand"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def products_by_category(request, category_id):
    try:
        products = Product.objects.filter(category=category_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"message": "Products not found for this category"}, status=status.HTTP_404_NOT_FOUND)

# order

@api_view(['GET'])
def get_user_orders(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    orders = Order.objects.filter(user_id=user)
    if not orders.exists():
        return Response({'message': 'No orders found for this user'}, status=status.HTTP_200_OK)

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_order(request):
    serializer = CreateOrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_order(request, order_id):
    order = Order.objects.get(order_id=order_id)
    order.delete()
    return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class AccessoryProductsListCreateView(generics.ListCreateAPIView):
    serializer_class = AccessoryProductsSerializer
    def get_queryset(self):
        accessory_type = self.request.query_params.get('accessory_type')
        if accessory_type:
            return AccessoryProducts.objects.filter(accessory_type=accessory_type)
        else:
            return AccessoryProducts.objects.all()

class AccessoryProductsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessoryProducts.objects.all()
    serializer_class = AccessoryProductsSerializer

class FilteredAccessoryView(APIView):
    def get(self, request, accessory_type):
        if accessory_type not in ['Car', 'Bike']:
            return Response({"error": "Invalid accessory type. Valid types are 'Car' and 'Bike'."}, status=status.HTTP_400_BAD_REQUEST)
        
        accessories = AccessoryProducts.objects.filter(accessory_type=accessory_type)
        serializer = AccessoryProductsSerializer(accessories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class SubvehicleBikeListCreateView(generics.ListCreateAPIView):
    queryset = Subvehicle_bike.objects.all()
    serializer_class = SubvehicleBikeSerializer

class SubvehicleBikeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subvehicle_bike.objects.all()
    serializer_class = SubvehicleBikeSerializer

class SubvehicleCarListCreateView(generics.ListCreateAPIView):
    queryset = SubVehicle_car.objects.all()
    serializer_class = SubvehicleCarSerializer

class SubvehicleCarRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubVehicle_car.objects.all()
    serializer_class = SubvehicleCarSerializer

class CarouselImageView(generics.ListCreateAPIView):
    queryset=CarouselImage.objects.all()
    serializer_class=CarouselImageSerializer

class CarouselImageViewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer

class SubvehiclecarByMainvehicle(generics.ListAPIView):
    serializer_class = SubvehicleCarSerializer
    def get_queryset(self):
        vehicle_id = self.kwargs['vehicle_id']
        
        queryset = SubVehicle_car.objects.filter(
            vehicle_id=vehicle_id
        )
        return queryset
    
class SubvehicleBikeByMainvehicle(generics.ListAPIView):
    serializer_class = SubvehicleBikeSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs['vehicle_id']
        return Subvehicle_bike.objects.filter(vehicle_id=vehicle_id)
    
class FilterSubVehiclecarByYearView(APIView):
    def get(self, request, year):
        sub_vehicles = SubVehicle_car.objects.filter(model_year=year)
        serializer = SubvehicleCarSerializer(sub_vehicles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FilterSubVehiclebikeByYearView(APIView):
    def get(self, request, year):
        sub_vehicles = Subvehicle_bike.objects.filter(model_year=year)
        serializer = SubvehicleBikeSerializer(sub_vehicles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)