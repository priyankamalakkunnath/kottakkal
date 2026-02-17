from rest_framework import serializers

from .models import (
    Branch,
    Company,
    Doctor,
    Medicine,
    MedicineMedia,
    Patient,
    PurchaseBill,
    PurchaseBillItem,
    Staff,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'company_code',
            'company_name',
            'address',
            'post',
            'dist',
            'state',
            'pin',
            'country',
            'logo',
            'gst',
            'reg_date',
            'exp_date',
        ]

        read_only_fields = ['id', 'company_code']


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            'id',
            'branch_code',
            'name',
            'address',
            'post',
            'dist',
            'state',
            'pin',
            'country',
            'reg_date',
            'exp_date',
        ]

        read_only_fields = ['id', 'branch_code']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id',
            'doctor_code',
            'name',
            'qualification',
            'address',
            'post',
            'dist',
            'state',
            'country',
            'pin',
            'joining_date',
            'resign_date',
            'specialization',
            'status',
            'biodata',
            'photo',
            'email',
        ]

        read_only_fields = ['id', 'doctor_code']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            'id',
            'pcode',
            'name',
            'address',
            'post',
            'dist',
            'state',
            'country',
            'pin',
            'joining_date',
            'resign_date',
            'status',
            'biodata',
            'photo',
            'qualification',
            'email',
        ]

        read_only_fields = ['id', 'pcode']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_code',
            'name',
            'mobile',
            'address',
            'post',
            'dist',
            'state',
            'country',
            'email',
            'date_of_birth',
            'photo',
            'adhar_number',
            'reg_date',
            'referred_by',
            'sex',
        ]

        read_only_fields = ['id', 'patient_code']


class MedicineMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineMedia
        fields = ['id', 'img1', 'img2', 'img3', 'img4', 'video']
        read_only_fields = ['id']


class OptionalMedicineMediaSerializer(MedicineMediaSerializer):
    """Handles Medicine with no MedicineMedia (OneToOne reverse raises DoesNotExist)."""

    def get_attribute(self, instance):
        try:
            return instance.media
        except MedicineMedia.DoesNotExist:
            return None


class MedicineSerializer(serializers.ModelSerializer):
    media = OptionalMedicineMediaSerializer(required=False, allow_null=True)

    class Meta:
        model = Medicine
        fields = [
            'id',
            'medicine_code',
            'name',
            'unit',
            'location1',
            'location2',
            'description',
            'dosage',
            'ingredients',
            'status',
            'hsn_code',
            'reorder_level',
            'media',
        ]
        read_only_fields = ['id', 'medicine_code']

    def create(self, validated_data):
        media_data = validated_data.pop('media', None)
        medicine = Medicine.objects.create(**validated_data)
        if media_data:
            MedicineMedia.objects.create(medicine=medicine, **media_data)
        return medicine

    def update(self, instance, validated_data):
        media_data = validated_data.pop('media', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if media_data is not None:
            media, _ = MedicineMedia.objects.get_or_create(medicine=instance)
            for attr, value in media_data.items():
                setattr(media, attr, value)
            media.save()
        return instance


class PurchaseBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseBillItem
        fields = [
            'id',
            'medicine_name',
            'qty',
            'batch_no',
            'gst',
            'purchasing_amount',
            'remarks',
        ]
        read_only_fields = ['id']


class PurchaseBillSerializer(serializers.ModelSerializer):
    items = PurchaseBillItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseBill
        fields = [
            'id',
            'supplier_name',
            'date',
            'lr_no',
            'bill_number',
            'items',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase_bill = PurchaseBill.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseBillItem.objects.create(purchase_bill=purchase_bill, **item_data)
        return purchase_bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseBillItem.objects.create(purchase_bill=instance, **item_data)
        return instance
