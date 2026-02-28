from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from datetime import timedelta

class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    post = models.CharField(max_length=255, null=True, blank=True)
    pin = models.CharField(max_length=20, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mob = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"SUP{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Supplier.objects.filter(supplier_code=candidate).exists():
                    self.supplier_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    catcode = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='category_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate a simple natural-number catcode (1, 2, 3, ...).
        Keeps existing non-numeric codes (like 'CAT2602273603') as they are.
        """
        if not self.catcode:
            # Look at the latest created category and, if its catcode is numeric,
            # increment it; otherwise start from 1.
            last_category = Category.objects.order_by('-id').first()
            if last_category and str(last_category.catcode).isdigit():
                next_code = int(last_category.catcode) + 1
            else:
                next_code = 1
            self.catcode = str(next_code)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Company(models.Model):
    company_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    company_name = models.CharField(max_length=255)
    address = models.TextField()
    post = models.CharField(max_length=255)
    dist = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    logo = models.FileField(upload_to='company_logos/', null=True, blank=True)
    gst = models.CharField(max_length=50)
    reg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.company_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"C{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Company.objects.filter(company_code=candidate).exists():
                    self.company_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.company_name


class Branch(models.Model):
    branch_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    post = models.CharField(max_length=255)
    dist = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    reg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.branch_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"B{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Branch.objects.filter(branch_code=candidate).exists():
                    self.branch_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Patient(models.Model):
    SEX_MALE = 'male'
    SEX_FEMALE = 'female'
    SEX_OTHER = 'other'
    SEX_CHOICES = [
        (SEX_MALE, 'Male'),
        (SEX_FEMALE, 'Female'),
        (SEX_OTHER, 'Other'),
    ]

    patient_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    address = models.TextField()
    post = models.CharField(max_length=255)
    dist = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.FileField(upload_to='patient_photos/', null=True, blank=True)
    adhar_number = models.CharField(max_length=20, null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
    referred_by = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.patient_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"PT{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Patient.objects.filter(patient_code=candidate).exists():
                    self.patient_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Staff(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    pcode = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    post = models.CharField(max_length=255)
    dist = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    joining_date = models.DateField(null=True, blank=True)
    resign_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    biodata = models.FileField(upload_to='staff_biodata/', null=True, blank=True)
    photo = models.FileField(upload_to='staff_photos/', null=True, blank=True)
    qualification = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pcode:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"P{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Staff.objects.filter(pcode=candidate).exists():
                    self.pcode = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Doctor(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    doctor_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    address = models.TextField()
    post = models.CharField(max_length=255)
    dist = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    joining_date = models.DateField(null=True, blank=True)
    resign_date = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    biodata = models.FileField(upload_to='doctor_biodata/', null=True, blank=True)
    photo = models.FileField(upload_to='doctor_photos/', null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.doctor_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"D{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Doctor.objects.filter(doctor_code=candidate).exists():
                    self.doctor_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Medicine(models.Model):
    STATUS_IN_STOCK = 'in stock'
    STATUS_OUT_OF_STOCK = 'out of stock'
    STATUS_CHOICES = [
        (STATUS_IN_STOCK, 'In Stock'),
        (STATUS_OUT_OF_STOCK, 'Out of Stock'),
    ]

    medicine_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    sku_name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100, null=True, blank=True)
    unit_prefix = models.CharField(max_length=50, null=True, blank=True)
    prefix_qty = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicines'
    )
    package_count = models.PositiveIntegerField(default=1)
    mrp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sell_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50)
    location1 = models.CharField(max_length=255, null=True, blank=True)
    location2 = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dosage = models.CharField(max_length=255, null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_STOCK)
    hsn_code = models.CharField(max_length=20, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.medicine_code:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"MED{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Medicine.objects.filter(medicine_code=candidate).exists():
                    self.medicine_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.sku_name


class MedicineMedia(models.Model):
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE, related_name='media')
    img1 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img2 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img3 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img4 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    video = models.FileField(upload_to='medicine_videos/', null=True, blank=True)

    def __str__(self) -> str:
        return f"Media for {self.medicine.name}"


class MedicalItem(models.Model):
    """
    Parent table for Medical Item API.
    mcode is a sequential natural number (1, 2, 3, ...).
    """
    mcode = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    sku_name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)
    unit_prefix = models.CharField(max_length=50, null=True, blank=True)
    prefix_qty = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_items'
    )
    package_count = models.PositiveIntegerField(default=1)
    reorder_level = models.PositiveIntegerField(default=0)
    mrp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sell_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    storage_location1 = models.CharField(max_length=255, null=True, blank=True)
    storage_location2 = models.CharField(max_length=255, null=True, blank=True)
    hsn_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dosage_instructions = models.TextField(null=True, blank=True)
    basic_prize = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gst = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        """
        Auto-generate a simple natural-number mcode (1, 2, 3, ...).
        """
        if not self.mcode:
            last = MedicalItem.objects.order_by('-id').first()
            if last and str(last.mcode).isdigit():
                next_code = int(last.mcode) + 1
            else:
                next_code = 1
            self.mcode = str(next_code)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.sku_name


class MedicalItemMedia(models.Model):
    """Child table: media for MedicalItem (on_delete CASCADE)."""
    medical_item = models.OneToOneField(
        MedicalItem, on_delete=models.CASCADE, related_name='media'
    )
    img1 = models.CharField(max_length=500, null=True, blank=True)
    img2 = models.CharField(max_length=500, null=True, blank=True)
    img3 = models.CharField(max_length=500, null=True, blank=True)
    img4 = models.CharField(max_length=500, null=True, blank=True)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Media for MedicalItem {self.medical_item_id}"


class PurchaseOrder(models.Model):
    STATUS_ISSUED = 'issued'
    STATUS_PARTIALLY_DELIVED = 'partially delived'
    STATUS_FULL_DELIVED = 'full delived'
    STATUS_CHOICES = [
        (STATUS_ISSUED, 'Issued'),
        (STATUS_PARTIALLY_DELIVED, 'Partially Delived'),
        (STATUS_FULL_DELIVED, 'Full Delived'),
    ]

    purchase_order_no = models.CharField(
        max_length=20, unique=True, editable=False, blank=True
    )
    date = models.DateField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='purchase_orders'
    )
    emp = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name='purchase_orders', null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ISSUED
    )
    remarks = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.purchase_order_no:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"PO{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not PurchaseOrder.objects.filter(purchase_order_no=candidate).exists():
                    self.purchase_order_no = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.purchase_order_no} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    TYPE_PNP = 'p&p'
    TYPE_SCHEDULE1 = 'shedule1'
    TYPE_CHOICES = [
        (TYPE_PNP, 'P&P'),
        (TYPE_SCHEDULE1, 'Shedule1'),
    ]

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='items'
    )
    item_code = models.CharField(max_length=50, null=True, blank=True)
    sku_code = models.CharField(max_length=100, null=True, blank=True)
    sku_name = models.CharField(max_length=255, null=True, blank=True)
    item_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, null=True, blank=True
    )
    unit = models.CharField(max_length=50, null=True, blank=True)
    full_quantity = models.PositiveIntegerField(default=0)
    actual_quantity = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.sku_name or self.sku_code} x {self.actual_quantity}"


class Item(models.Model):
    """Parent table for Item API."""
    item_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    sku_name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)
    unit_prefix = models.CharField(max_length=50, null=True, blank=True)
    prefix_qty = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    package_count = models.PositiveIntegerField(default=1)
    reorder_level = models.PositiveIntegerField(default=0)
    mrp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sell_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    storage_location1 = models.CharField(max_length=255, null=True, blank=True)
    storage_location2 = models.CharField(max_length=255, null=True, blank=True)
    hsn_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dosage_instructions = models.TextField(null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        """
        Auto-generate a simple natural-number item_code (1, 2, 3, ...).
        Keeps existing non-numeric codes (like 'ITM2602270179') as they are.
        """
        if not self.item_code:
            # Use latest created item; if its item_code is numeric, increment it;
            # otherwise start from 1.
            last_item = Item.objects.order_by('-id').first()
            if last_item and str(last_item.item_code).isdigit():
                next_code = int(last_item.item_code) + 1
            else:
                next_code = 1
            self.item_code = str(next_code)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.sku_name


class ItemMedia(models.Model):
    """Child table: media for Item (on_delete CASCADE)."""
    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name='media'
    )
    img1 = models.CharField(max_length=500, null=True, blank=True)
    img2 = models.CharField(max_length=500, null=True, blank=True)
    img3 = models.CharField(max_length=500, null=True, blank=True)
    img4 = models.CharField(max_length=500, null=True, blank=True)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Media for Item {self.item_id}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    customer_code = models.CharField(
        max_length=20, unique=True, editable=False, blank=True, null=True
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not (self.customer_code or '').strip():
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"CUST{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not UserProfile.objects.filter(customer_code=candidate).exists():
                    self.customer_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CustomerAddress(models.Model):
    """Address for a customer (UserProfile), identified by customer_code."""
    PREFIX_MR = 'Mr'
    PREFIX_MRS = 'Mrs'
    PREFIX_MISS = 'Miss'
    PREFIX_ADV = 'Adv'
    PREFIX_DR = 'Dr'
    PREFIX_CHOICES = [
        (PREFIX_MR, 'Mr'),
        (PREFIX_MRS, 'Mrs'),
        (PREFIX_MISS, 'Miss'),
        (PREFIX_ADV, 'Adv'),
        (PREFIX_DR, 'Dr'),
    ]

    profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='address'
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=10, choices=PREFIX_CHOICES)
    address = models.TextField()
    post = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    country = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.profile.customer_code} - {self.address[:30]}"


class Coupon(models.Model):
    """
    Coupon / promo code.
    Fields:
      - name: coupon name or code
      - promo_start / promo_end: validity period (dates)
      - discount_pct: percentage discount (e.g. 5.00 for 5%)
      - status: active / inactive
      - type: existing / new
    """
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    TYPE_EXISTING = 'existing'
    TYPE_NEW = 'new'
    TYPE_CHOICES = [
        (TYPE_EXISTING, 'Existing'),
        (TYPE_NEW, 'New'),
    ]

    name = models.CharField(max_length=100)
    promo_start = models.DateField(null=True, blank=True)
    promo_end = models.DateField(null=True, blank=True)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_NEW)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reset_tokens'
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        if not self.expires_at:
            self.expires_at = now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        return now() < self.expires_at

    def __str__(self) -> str:
        return f"Reset token for {self.user.username}"


class OneTimePassword(models.Model):
    """One-time password (OTP) for mobile/email verification."""
    PURPOSE_REGISTER = 'register'
    PURPOSE_LOGIN = 'login'
    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, 'Register'),
        (PURPOSE_LOGIN, 'Login'),
    ]

    mobile_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, null=True, blank=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default=PURPOSE_REGISTER)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    customer_code = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Default: OTP valid for 5 minutes (300 seconds)
            self.expires_at = now() + timedelta(seconds=300)
        super().save(*args, **kwargs)

    @property
    def is_valid(self) -> bool:
        return self.verified_at is None and now() < self.expires_at

    def __str__(self) -> str:
        return f"OTP for {self.mobile_number} ({self.purpose})"

class Cart(models.Model):
    """Cart / order with auto-generated order_no. delivery_status default 'CART'."""
    order_no = models.CharField(
        max_length=20, unique=True, editable=False, blank=True
    )
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    ccode = models.CharField(max_length=50, null=True, blank=True)
    inv_no = models.CharField(max_length=100, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    courier_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    net_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    despatch_no = models.CharField(max_length=100, null=True, blank=True)
    courier = models.CharField(max_length=255, null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20, default='CART'
    )
    discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Cart-level discount amount (e.g. applied at checkout).'
    )
    payment_mode = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='e.g. COD, ONLINE; set on order confirm.'
    )

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if not self.order_no:
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"ORD{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not Cart.objects.filter(order_no=candidate).exists():
                    self.order_no = candidate
                    break
        if self.date is None:
            self.date = now().date()
        if self.time is None:
            self.time = now().time()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.order_no} ({self.delivery_status})"


class OnlineOrderItem(models.Model):
    """Line item for a cart (order). Unique per cart + item_code; qty/rate/amt."""
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items'
    )
    item_code = models.CharField(max_length=100)
    qty = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    class Meta:
        ordering = ['id']
        unique_together = [['cart', 'item_code']]

    def __str__(self) -> str:
        return f"{self.cart.order_no} / {self.item_code} x {self.qty}"
