from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now

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
    name = models.CharField(max_length=255)
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
        return self.name


class MedicineMedia(models.Model):
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE, related_name='media')
    img1 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img2 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img3 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    img4 = models.FileField(upload_to='medicine_images/', null=True, blank=True)
    video = models.FileField(upload_to='medicine_videos/', null=True, blank=True)

    def __str__(self) -> str:
        return f"Media for {self.medicine.name}"


class PurchaseBill(models.Model):
    supplier_name = models.CharField(max_length=255)
    date = models.DateField()
    lr_no = models.CharField(max_length=100, null=True, blank=True)
    bill_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.bill_number or 'Bill'} - {self.supplier_name}"


class PurchaseBillItem(models.Model):
    purchase_bill = models.ForeignKey(
        PurchaseBill, on_delete=models.CASCADE, related_name='items'
    )
    medicine_name = models.CharField(max_length=255)
    qty = models.PositiveIntegerField(default=1)
    batch_no = models.CharField(max_length=100, null=True, blank=True)
    gst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchasing_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.medicine_name} x {self.qty}"
