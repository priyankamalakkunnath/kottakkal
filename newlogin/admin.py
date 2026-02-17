from django.contrib import admin

from .models import Medicine, MedicineMedia, PurchaseBill, PurchaseBillItem


class PurchaseBillItemInline(admin.TabularInline):
    model = PurchaseBillItem
    extra = 0


@admin.register(PurchaseBill)
class PurchaseBillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'supplier_name', 'date', 'lr_no']
    list_filter = ['date']
    search_fields = ['supplier_name', 'bill_number', 'lr_no']
    inlines = [PurchaseBillItemInline]


class MedicineMediaInline(admin.StackedInline):
    model = MedicineMedia
    extra = 0


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_code', 'name', 'unit', 'status', 'reorder_level']
    list_filter = ['status']
    search_fields = ['medicine_code', 'name']
    inlines = [MedicineMediaInline]
