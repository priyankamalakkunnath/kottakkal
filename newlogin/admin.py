from django.contrib import admin

from .models import Cart, Category, Item, ItemMedia, OnlineOrderItem, PurchaseOrder, PurchaseOrderItem, Supplier, UserProfile


class OnlineOrderItemInline(admin.TabularInline):
    model = OnlineOrderItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_no', 'date', 'time', 'ccode', 'delivery_status', 'payment_mode', 'discount', 'net_amount']
    list_filter = ['delivery_status']
    search_fields = ['order_no', 'ccode', 'inv_no']
    inlines = [OnlineOrderItemInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'customer_code', 'name', 'phone']
    search_fields = ['name', 'customer_code', 'user__email']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['purchase_order_no', 'date', 'supplier', 'emp', 'status', 'remarks']
    list_filter = ['date', 'status']
    search_fields = ['purchase_order_no']
    inlines = [PurchaseOrderItemInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'company', 'mob', 'email']
    search_fields = ['supplier_code', 'name', 'company']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['catcode', 'name']
    search_fields = ['catcode', 'name']


class ItemMediaInline(admin.StackedInline):
    model = ItemMedia
    extra = 0
    fk_name = 'item'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_code', 'sku_code', 'sku_name', 'category', 'mrp', 'updated_at']
    search_fields = ['sku_code', 'sku_name', 'category']
    inlines = [ItemMediaInline]
