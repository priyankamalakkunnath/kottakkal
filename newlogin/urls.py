from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    CompanyViewSet,
    DoctorViewSet,
    MedicineViewSet,
    PatientViewSet,
    PurchaseBillViewSet,
    StaffViewSet,
)

router = DefaultRouter(trailing_slash='/?')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'purchase-bills', PurchaseBillViewSet, basename='purchasebill')

urlpatterns = [
    path('', include(router.urls)),
]
