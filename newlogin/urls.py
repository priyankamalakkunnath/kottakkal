from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AddItemToCartAPIView,
    AdminLoginAPIView,
    AdminOrderDetailAPIView,
    AdminOrderListAPIView,
    BranchViewSet,
    CartViewSet,
    ConfirmOrderAPIView,
    CouponViewSet,
    DecrementCartItemAPIView,
    DeleteCartItemAPIView,
    IncrementCartItemAPIView,
    CategoryViewSet,
    CompanyViewSet,
    CustomerAddressAPIView,
    DoctorViewSet,
    ForgotPasswordAPIView,
    IdentifyCustomerAPIView,
    MedicalItemViewSet,
    SendOtpAPIView,
    VerifyOtpAPIView,
    LoginAPIView,
    OrderSummaryAPIView,
    PatientViewSet,
    PurchaseOrderViewSet,
    RegisterAPIView,
    RegisterDeleteAPIView,
    ResetPasswordAPIView,
    StaffViewSet,
    SupplierViewSet,
    VerifyPasswordAPIView,
)

router = DefaultRouter(trailing_slash='/?')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'medicalitems', MedicalItemViewSet, basename='medicalitem')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/item/add/', AddItemToCartAPIView.as_view(), name='cart-item-add'),
    path('cart/item/add', AddItemToCartAPIView.as_view(), name='cart-item-add-no-slash'),
    path('cart/item/increment/', IncrementCartItemAPIView.as_view(), name='cart-item-increment'),
    path('cart/item/increment', IncrementCartItemAPIView.as_view(), name='cart-item-increment-no-slash'),
    path('cart/item/decrement/', DecrementCartItemAPIView.as_view(), name='cart-item-decrement'),
    path('cart/item/decrement', DecrementCartItemAPIView.as_view(), name='cart-item-decrement-no-slash'),
    path('cart/item/delete/', DeleteCartItemAPIView.as_view(), name='cart-item-delete'),
    path('cart/item/delete', DeleteCartItemAPIView.as_view(), name='cart-item-delete-no-slash'),
    path('cart/summary/', OrderSummaryAPIView.as_view(), name='cart-summary'),
    path('cart/summary', OrderSummaryAPIView.as_view(), name='cart-summary-no-slash'),
    path('customer/address/', CustomerAddressAPIView.as_view(), name='customer-address'),
    path('customer/address', CustomerAddressAPIView.as_view(), name='customer-address-no-slash'),
    path('orders/confirm/', ConfirmOrderAPIView.as_view(), name='orders-confirm'),
    path('orders/confirm', ConfirmOrderAPIView.as_view(), name='orders-confirm-no-slash'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin-login'),
    path('admin/login', AdminLoginAPIView.as_view(), name='admin-login-no-slash'),
    path('admin/orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('admin/orders', AdminOrderListAPIView.as_view(), name='admin-order-list-no-slash'),
    path('admin/orders/<str:order_id>/', AdminOrderDetailAPIView.as_view(), name='admin-order-detail'),
    path('admin/orders/<str:order_id>', AdminOrderDetailAPIView.as_view(), name='admin-order-detail-no-slash'),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/register', RegisterAPIView.as_view(), name='register-no-slash'),
    path('auth/register-delete/', RegisterDeleteAPIView.as_view(), name='register-delete'),
    path('auth/register-delete', RegisterDeleteAPIView.as_view(), name='register-delete-no-slash'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/login', LoginAPIView.as_view(), name='login-no-slash'),
    path('auth/login/%20', LoginAPIView.as_view(), name='login-trailing-space-encoded'),
    path('auth/login/%20/', LoginAPIView.as_view(), name='login-trailing-space-encoded-slash'),
    path('auth/login/ ', LoginAPIView.as_view(), name='login-trailing-space'),
    path('auth/login/ /', LoginAPIView.as_view(), name='login-trailing-space-slash'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('auth/forgot-password', ForgotPasswordAPIView.as_view(), name='forgot-password-no-slash'),
    path('auth/identify-customer/', IdentifyCustomerAPIView.as_view(), name='identify-customer'),
    path('auth/identify-customer', IdentifyCustomerAPIView.as_view(), name='identify-customer-no-slash'),
    path('auth/send-otp/', SendOtpAPIView.as_view(), name='send-otp'),
    path('auth/send-otp', SendOtpAPIView.as_view(), name='send-otp-no-slash'),
    path('auth/verify-otp/', VerifyOtpAPIView.as_view(), name='verify-otp'),
    path('auth/verify-otp', VerifyOtpAPIView.as_view(), name='verify-otp-no-slash'),
    path('auth/verify-password/', VerifyPasswordAPIView.as_view(), name='verify-password'),
    path('auth/verify-password', VerifyPasswordAPIView.as_view(), name='verify-password-no-slash'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('auth/reset-password', ResetPasswordAPIView.as_view(), name='reset-password-no-slash'),
]
