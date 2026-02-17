from rest_framework import viewsets

from .models import Branch, Company, Doctor, Medicine, Patient, PurchaseBill, Staff
from .serializers import (
    BranchSerializer,
    CompanySerializer,
    DoctorSerializer,
    MedicineSerializer,
    PatientSerializer,
    PurchaseBillSerializer,
    StaffSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all().order_by('-id')
    serializer_class = BranchSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by('-id')
    serializer_class = DoctorSerializer


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().order_by('-id')
    serializer_class = StaffSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-id')
    serializer_class = PatientSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all().order_by('-id').select_related('media')
    serializer_class = MedicineSerializer


class PurchaseBillViewSet(viewsets.ModelViewSet):
    queryset = PurchaseBill.objects.all().order_by('-id').prefetch_related('items')
    serializer_class = PurchaseBillSerializer
