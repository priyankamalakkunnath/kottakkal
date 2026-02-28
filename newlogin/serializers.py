from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Branch,
    Cart,
    Category,
    Company,
    Coupon,
    CustomerAddress,
    Doctor,
    Item,
    ItemMedia,
    MedicalItem,
    MedicalItemMedia,
    Medicine,
    MedicineMedia,
    OnlineOrderItem,
    Patient,
    PurchaseOrder,
    PurchaseOrderItem,
    PasswordResetToken,
    Staff,
    Supplier,
    UserProfile,
)

User = get_user_model()


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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'catcode', 'name', 'description', 'image']
        read_only_fields = ['id', 'catcode']


class CategoryCatcodeSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing all catcodes (id + catcode only)."""
    class Meta:
        model = Category
        fields = ['id', 'catcode']
        read_only_fields = ['id', 'catcode']


class MedicineMediaSerializer(serializers.ModelSerializer):
    """Read-only medicine media with full URLs for file fields."""

    class Meta:
        model = MedicineMedia
        fields = ['id', 'img1', 'img2', 'img3', 'img4', 'video']
        read_only_fields = ['id']

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        for key in ['img1', 'img2', 'img3', 'img4', 'video']:
            val = getattr(instance, key, None)
            if val:
                data[key] = request.build_absolute_uri(val.url) if request else val.url
        return data


class OptionalMedicineMediaSerializer(MedicineMediaSerializer):
    """For read: return media object or null if no MedicineMedia row."""

    def get_attribute(self, instance):
        try:
            return instance.media
        except MedicineMedia.DoesNotExist:
            return None

    def to_representation(self, instance):
        if instance is None:
            return None
        return super().to_representation(instance)


class MedicineSerializer(serializers.ModelSerializer):
    """List/detail serializer for Medicine (e.g. medicines by category)."""
    catcode = serializers.CharField(source='category.catcode', allow_null=True, read_only=True)
    media = OptionalMedicineMediaSerializer(required=False, read_only=True)

    class Meta:
        model = Medicine
        fields = [
            'id',
            'medicine_code',
            'sku_name',
            'sku_code',
            'unit',
            'unit_prefix',
            'prefix_qty',
            'catcode',
            'package_count',
            'reorder_level',
            'mrp',
            'sell_discount',
            'location1',
            'location2',
            'hsn_code',
            'description',
            'dosage',
            'ingredients',
            'status',
            'media',
        ]
        read_only_fields = ['id', 'medicine_code']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'name',
            'promo_start',
            'promo_end',
            'discount_pct',
            'status',
            'type',
        ]
        read_only_fields = ['id']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_code',
            'name',
            'position',
            'company',
            'address',
            'post',
            'pin',
            'district',
            'state',
            'country',
            'mob',
            'email',
        ]
        read_only_fields = ['id', 'supplier_code']


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


# ---- Item API (parent Item + child ItemMedia) ----


class FileOrPathField(serializers.Field):
    """Accept either an uploaded file or a path string for item media fields."""
    def to_internal_value(self, data):
        if data is None or data == '':
            return None
        if hasattr(data, 'read'):
            return data
        if isinstance(data, str):
            return data.strip() or None
        raise serializers.ValidationError('Expected a file upload or a path string.')
    def to_representation(self, value):
        return value


class ItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMedia
        fields = ['id', 'img1', 'img2', 'img3', 'img4', 'video_url', 'created_at']
        read_only_fields = ['id', 'created_at']


def _media_url(value, request):
    """Return full URL for a stored media path (e.g. item_images/abc.jpg)."""
    if not value or not isinstance(value, str) or not value.strip():
        return value
    if value.startswith(('http://', 'https://')):
        return value
    from django.conf import settings
    base = getattr(settings, 'PUBLIC_MEDIA_BASE_URL', None)
    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    path = value if value.startswith('/') else f"{media_url.rstrip('/')}/{value}"
    if base:
        return f"{base.rstrip('/')}{path}" if path.startswith('/') else f"{base.rstrip('/')}/{path}"
    if request and hasattr(request, 'build_absolute_uri'):
        return request.build_absolute_uri(path)
    return path


class OptionalItemMediaSerializer(ItemMediaSerializer):
    """For read: return media object or null if no ItemMedia row."""

    def get_attribute(self, instance):
        try:
            return instance.media
        except ItemMedia.DoesNotExist:
            return None

    def to_representation(self, instance):
        if instance is None:
            return None
        request = self.context.get('request')
        return {
            'img1': _media_url(instance.img1, request),
            'img2': _media_url(instance.img2, request),
            'img3': _media_url(instance.img3, request),
            'img4': _media_url(instance.img4, request),
            'video_url': _media_url(instance.video_url, request),
        }


def _save_media_file(file_or_path, subdir='item_images'):
    """If value is an uploaded file, save to storage and return path string; else return as-is."""
    if file_or_path is None:
        return None
    if hasattr(file_or_path, 'read'):
        from django.core.files.storage import default_storage
        import uuid
        import os
        name = getattr(file_or_path, 'name', 'upload') or 'upload'
        ext = os.path.splitext(name)[1] or '.bin'
        path = default_storage.save(f'{subdir}/{uuid.uuid4().hex}{ext}', file_or_path)
        return path
    return file_or_path if isinstance(file_or_path, str) else None


class MedicalItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalItemMedia
        fields = ['id', 'img1', 'img2', 'img3', 'img4', 'video_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class OptionalMedicalItemMediaSerializer(MedicalItemMediaSerializer):
    """For read: return media object or null if no MedicalItemMedia row."""

    def get_attribute(self, instance):
        try:
            return instance.media
        except MedicalItemMedia.DoesNotExist:
            return None

    def to_representation(self, instance):
        if instance is None:
            return None
        request = self.context.get('request')
        return {
            'img1': _media_url(instance.img1, request),
            'img2': _media_url(instance.img2, request),
            'img3': _media_url(instance.img3, request),
            'img4': _media_url(instance.img4, request),
            'video_url': _media_url(instance.video_url, request),
        }


class MedicalItemSerializer(serializers.ModelSerializer):
    media = OptionalMedicalItemMediaSerializer(required=False, read_only=True)
    img1 = FileOrPathField(required=False, allow_null=True, write_only=True)
    img2 = FileOrPathField(required=False, allow_null=True, write_only=True)
    img3 = FileOrPathField(required=False, allow_null=True, write_only=True)
    img4 = FileOrPathField(required=False, allow_null=True, write_only=True)
    video_url = FileOrPathField(required=False, allow_null=True, write_only=True)
    catcode = serializers.CharField(
        source='category.catcode',
        allow_null=True,
        required=False,
    )

    class Meta:
        model = MedicalItem
        fields = [
            'id',
            'mcode',
            'sku_name',
            'sku_code',
            'unit',
            'unit_prefix',
            'prefix_qty',
            'catcode',
            'package_count',
            'reorder_level',
            'mrp',
            'sell_discount',
            'storage_location1',
            'storage_location2',
            'hsn_code',
            'description',
            'dosage_instructions',
            'basic_prize',
            'gst',
            'created_at',
            'updated_at',
            'media',
            'img1',
            'img2',
            'img3',
            'img4',
            'video_url',
        ]
        read_only_fields = ['id', 'mcode', 'created_at', 'updated_at']

    def create(self, validated_data):
        from django.db import transaction
        media_fields = ['img1', 'img2', 'img3', 'img4', 'video_url']
        media_data = {k: validated_data.pop(k, None) for k in media_fields}
        for k in ['img1', 'img2', 'img3', 'img4']:
            if media_data.get(k) is not None:
                media_data[k] = _save_media_file(media_data[k], 'medicalitem_images')
        if media_data.get('video_url') is not None:
            media_data['video_url'] = _save_media_file(media_data['video_url'], 'medicalitem_videos')
        # Resolve catcode into Category FK (if provided)
        catcode = None
        category_data = validated_data.pop('category', None)
        if isinstance(category_data, dict):
            catcode = category_data.get('catcode')
        if catcode:
            category = Category.objects.filter(catcode=catcode).first()
            validated_data['category'] = category

        with transaction.atomic():
            medical_item = MedicalItem.objects.create(**validated_data)
            MedicalItemMedia.objects.create(medical_item=medical_item, **media_data)
        return medical_item

    def update(self, instance, validated_data):
        media_fields = ['img1', 'img2', 'img3', 'img4', 'video_url']
        media_data = {k: validated_data.pop(k, None) for k in media_fields if k in validated_data}
        for k in ['img1', 'img2', 'img3', 'img4']:
            if media_data.get(k) is not None:
                media_data[k] = _save_media_file(media_data[k], 'medicalitem_images')
        if media_data.get('video_url') is not None:
            media_data['video_url'] = _save_media_file(media_data['video_url'], 'medicalitem_videos')
        # Resolve catcode into Category FK (if provided)
        category_data = validated_data.pop('category', None)
        if isinstance(category_data, dict):
            catcode = category_data.get('catcode')
            if catcode:
                category = Category.objects.filter(catcode=catcode).first()
                validated_data['category'] = category

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if media_data:
            media, _ = MedicalItemMedia.objects.get_or_create(medical_item=instance)
            for k, v in media_data.items():
                setattr(media, k, v)
            media.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            'id',
            'order_no',
            'date',
            'time',
            'ccode',
            'inv_no',
            'total_amount',
            'courier_amount',
            'net_amount',
            'despatch_no',
            'courier',
            'delivery_status',
            'payment_mode',
        ]
        read_only_fields = ['id', 'order_no']


class CustomerAddressSerializer(serializers.ModelSerializer):
    customer_code = serializers.CharField(source='profile.customer_code', read_only=True)

    class Meta:
        model = CustomerAddress
        fields = [
            'id',
            'customer_code',
            'name',
            'prefix',
            'address',
            'post',
            'district',
            'state',
            'pin',
            'country',
        ]
        read_only_fields = ['id', 'customer_code']


class CustomerAddressInputSerializer(serializers.Serializer):
    """Input for customer address API – identifies customer by customer_code (when not authenticated)."""
    customer_code = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    prefix = serializers.ChoiceField(choices=CustomerAddress.PREFIX_CHOICES)
    address = serializers.CharField()
    post = serializers.CharField(max_length=255)
    district = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    pin = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=255)


class CustomerAddressAuthenticatedInputSerializer(serializers.Serializer):
    """Input for customer address API when authenticated – no customer_code; backend uses logged-in user."""
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    prefix = serializers.ChoiceField(choices=CustomerAddress.PREFIX_CHOICES)
    address = serializers.CharField()
    post = serializers.CharField(max_length=255)
    district = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    pin = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=255)


PAYMENT_MODE_CHOICES = [
    ('COD', 'COD'),
    ('ONLINE', 'ONLINE'),
    ('CARD', 'CARD'),
    ('UPI', 'UPI'),
]


class ConfirmOrderSerializer(serializers.Serializer):
    """Input for POST /api/orders/confirm/ – frontend does NOT send totals or ccode."""
    order_no = serializers.CharField(max_length=20)
    address_id = serializers.IntegerField(min_value=1)
    payment_mode = serializers.ChoiceField(choices=PAYMENT_MODE_CHOICES)


class AddItemToCartSerializer(serializers.Serializer):
    """Input for POST /api/cart/item/add/"""
    order_no = serializers.CharField(max_length=20)
    mcode = serializers.CharField(max_length=20)
    qty = serializers.IntegerField(min_value=1)


class CartItemIdentifySerializer(serializers.Serializer):
    """Input for cart item increment / decrement / delete."""
    order_no = serializers.CharField(max_length=20)
    mcode = serializers.CharField(max_length=20)


class OnlineOrderItemSerializer(serializers.ModelSerializer):
    """Cart line item; exposes stored product code as mcode (same as Add Item to Cart input)."""
    mcode = serializers.CharField(source='item_code', read_only=True)

    class Meta:
        model = OnlineOrderItem
        fields = ['id', 'cart', 'mcode', 'qty', 'rate', 'amt']
        read_only_fields = ['id', 'mcode', 'rate', 'amt']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id',
            'item_code',
            'sku_code',
            'sku_name',
            'item_type',
            'unit',
            'full_quantity',
            'actual_quantity',
        ]
        read_only_fields = ['id']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    supplier_code = serializers.CharField(source='supplier.supplier_code', read_only=True)
    emp_code = serializers.SerializerMethodField(read_only=True)

    def get_emp_code(self, obj):
        return obj.emp.pcode if obj.emp else None

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'purchase_order_no',
            'date',
            'supplier',
            'supplier_code',
            'emp',
            'emp_code',
            'status',
            'remarks',
            'items',
        ]
        read_only_fields = ['id', 'purchase_order_no']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
        return instance


# ---- Auth (Register, Login, Forgot / Verify / Reset password) ----

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    mobile = serializers.CharField(max_length=20, required=False)
    mobileNumber = serializers.CharField(max_length=20, required=False)
    phoneNumber = serializers.CharField(max_length=20, required=False)

    def to_internal_value(self, data):
        # Accept phone, mobile, mobileNumber, or phoneNumber and normalize to 'phone'
        phone_value = None
        for field_name in ['phone', 'mobile', 'mobileNumber', 'phoneNumber']:
            if field_name in data:
                phone_value = data[field_name]
                break
        
        if not phone_value:
            raise serializers.ValidationError({
                'phone': ['This field is required. Send "phone", "mobile", "mobileNumber", or "phoneNumber".']
            })
        
        # Normalize to 'phone' for internal processing
        data = data.copy()
        data['phone'] = phone_value
        # Remove other phone field variations to avoid confusion
        for field_name in ['mobile', 'mobileNumber', 'phoneNumber']:
            data.pop(field_name, None)
        
        return super().to_internal_value(data)

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate_phone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Phone number cannot be empty.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this mobile number already exists.')
        return value

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        email = validated_data['email']
        name = validated_data['name']
        phone = validated_data['phone']
        password = get_random_string(12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789')
        user = User.objects.create_user(
            username=phone,
            email=email,
            password=password,
        )
        UserProfile.objects.create(user=user, name=name, phone=phone)
        return {'user': user, 'password': password}


class RegisterDetailSerializer(serializers.Serializer):
    """Output for GET /api/auth/register/ – current logged-in user's registration details."""
    customer_code = serializers.CharField(allow_blank=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    username = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class AdminLoginSerializer(serializers.Serializer):
    """Input for POST /api/admin/login/ – username and password; user must be staff or superuser."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(
        max_length=128, write_only=True, style={'input_type': 'password'}
    )


class RegisterDeleteSerializer(serializers.Serializer):
    """Optional password confirmation for account deletion."""
    password = serializers.CharField(
        max_length=128, write_only=True, required=False, style={'input_type': 'password'}
    )


class IdentifyCustomerSerializer(serializers.Serializer):
    """Input for POST /api/auth/identify-customer/ – identify if a mobileNumber belongs to an existing customer."""
    mobileNumber = serializers.CharField(max_length=20)


class SendOtpSerializer(serializers.Serializer):
    """Input for POST /api/auth/send-otp/ – send an OTP to mobileNumber/email."""
    mobileNumber = serializers.CharField(max_length=20)
    email = serializers.EmailField()


class VerifyOtpSerializer(serializers.Serializer):
    """Input for POST /api/auth/verify-otp/ – verify an OTP using reference ID and code."""
    otpReferenceId = serializers.CharField(max_length=32)
    otp = serializers.CharField(max_length=6)
