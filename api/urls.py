from django.urls import path
from .views import *

urlpatterns = [

    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('verify-otp/', OTPVerificationView.as_view(), name='otp-verification'),


    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),

#USERS

    path('users/', list_users, name='user-list'),
    path('user_get/<int:user_id>/', user_detail_get, name='user-detail_get'),
    path('user_update/<int:user_id>/', user_detail_update, name='user-detail_update'),
    path('user_delete/<int:user_id>/', user_detail_delete, name='user-detail_delete'),

#CHANGE PASS

    path('change_password/', ChangePasswordView.as_view(), name='change-password'),

#ADDRESS

    path('address/', list_addresses, name='list-addresses'),
    path('address_create/', create_address, name='create-address'),
    path('address/<int:address_id>/', get_address, name='get-address'),
    path('addresses_update/<int:address_id>/', update_address, name='update-address'),
    path('addresses_delete/<int:address_id>/', delete_address, name='delete-address'),

#MAIN CATEGORIES

    path('main-categories/', MainCategoryListCreateView.as_view(), name='main-category-list-create'),
    path('main-categories/<int:pk>/', MainCategoryDetailView.as_view(), name='main-category-detail'),

#BRAND

    path('brands/', BrandListCreateView.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', BrandRetrieveUpdateDestroyView.as_view(), name='brand-retrieve-update-destroy'),
    path('brands/main-categories/<int:main_category_id>/', BrandListByMainCategoryView.as_view(), name='brand-list-by-main-category'),

#VEHICLES

    path('vehicles/', VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('vehicles/<int:pk>/', VehicleRetrieveUpdateDestroyView.as_view(), name='vehicle-retrieve-update-destroy'),
    path('vehicles/brands/<int:brand_id>/', VehicleListByBrandView.as_view(), name='vehicles-list-by-brand'),
    path('vehicles/main-category/<int:main_category_id>/brands/<int:brand_id>/', VehicleListByBrandAndCategoryView.as_view(), name='vehicles-list-by-brand-and-category'),
    path('main_category/<int:main_category_id>/brand/<int:brand_id>/vehicles/', VehicleListByMainCategoryAndBrand.as_view(), name='vehicle-list-by-main-category-brand'),
    path('main_category/vehicles/<int:main_category_id>/', VehicleListByMainCategory.as_view(), name='vehicle-list-by-main-category-brand'),


#cATEGORIES

    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),

#PRODUCTS

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/main_category/<int:main_category_id>/', ProductListCreateByMainCategoryView.as_view(), name='product-list-create-by-main-category'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:vehicle_id>/<str:subvehicle_type>/<int:subvehicle_id>/<int:category_id>/', ProductDetailByFiltersView.as_view(), name='product-detail-by-filters'),
    path('product-images/', ProductImageListCreateView.as_view(), name='product-image-list-create'),
    path('product-images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),
    

    path('qualities/', QualityListView.as_view(), name='quality-list'),
    path('qualities/<int:pk>/', QualityDetailView.as_view(), name='quality-detail'),


        path('product/<int:category_id>/',ProductdetailByCategoryView.as_view(), name='products-detail-by-category'),

#Review

    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/products/<int:product_id>/', ProductReviewListView.as_view(), name='product-review-list'),

#cart

    path('carts/', CartListCreateView.as_view(), name='cart-list-create'),
    path('carts/<int:pk>/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/items/', CartItemListCreateView.as_view(), name='cart-item-list-create'),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('cart/user/<int:user_id>/', UserCartView.as_view(), name='user-cart'),

#orders

    path('orders/<int:user_id>/', get_user_orders, name='get-user-orders'),
    path('orders_create/', create_order, name='create-order'),
    path('orders_delete/<str:order_id>/', delete_order, name='delete-order'),

#Accessories

    path('accessory/', AccessoryProductsListCreateView.as_view(), name='accessory-products-list-create'),
    path('accessory/<int:pk>/', AccessoryProductsDetailView.as_view(), name='accessory-products-detail'),
    path('accessory/<str:accessory_type>/', FilteredAccessoryView.as_view(), name='filtered-accessories'),

#Sub Vehicle Bike

    path('subvehicles_bike/', SubvehicleBikeListCreateView.as_view(), name='subvehicle_bike-list-create'),
    path('subvehicles_bike/<int:pk>/', SubvehicleBikeRetrieveUpdateDestroyView.as_view(), name='subvehicle_bike-detail'),

    path('Subvehicle-vehicle-Bike/<int:vehicle_id>/',SubvehicleBikeByMainvehicle.as_view(),name='SubvehicleBikeByMainvehicle'),
    path('subvehicles_bike/year/<int:year>/', FilterSubVehiclebikeByYearView.as_view(), name='filter-subvehicles-bike-by-year'),


#Sub Vehicle Car,

    path('subvehicles_car/', SubvehicleCarListCreateView.as_view(), name='subvehicle_car-list-create'),
    path('subvehicles_car/<int:pk>/', SubvehicleCarRetrieveUpdateDestroyView.as_view(), name='subvehicle_car-detail'), 

    path('Subvehicle-vehicle-car/<int:vehicle_id>/',SubvehiclecarByMainvehicle.as_view(),name='SubvehiclecarByMainvehicle'),
    path('subvehicles_car/year/<int:year>/', FilterSubVehiclecarByYearView.as_view(), name='filter-subvehicles-car-by-year'),


#Carousel

    path('CarouselImage/',CarouselImageView.as_view(),name='CarouselImageView-create'),
    path('CarouselImage/<int:pk>/',CarouselImageViewRetrieveUpdateDestroyView.as_view(),name='CarouselImageView-detail'),

    
]
