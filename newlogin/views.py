import json
from decimal import Decimal
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q, Sum
from datetime import datetime
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication


class PlainTextJSONParser(JSONParser):
    """Accept Content-Type: text/plain and parse as JSON (e.g. Postman raw body)."""
    media_type = 'text/plain'

from .models import (
    Branch,
    Cart,
    Category,
    Company,
    Coupon,
    CustomerAddress,
    Doctor,
    Item,
    MedicalItem,
    Medicine,
    OnlineOrderItem,
    OneTimePassword,
    Patient,
    PasswordResetToken,
    PurchaseOrder,
    Staff,
    Supplier,
    UserProfile,
)
from .serializers import (
    AddItemToCartSerializer,
    BranchSerializer,
    CartItemIdentifySerializer,
    CartSerializer,
    CategoryCatcodeSerializer,
    CategorySerializer,
    CompanySerializer,
    ConfirmOrderSerializer,
    CustomerAddressAuthenticatedInputSerializer,
    CustomerAddressInputSerializer,
    CustomerAddressSerializer,
    CouponSerializer,
    DoctorSerializer,
    ForgotPasswordSerializer,
    MedicalItemSerializer,
    MedicineSerializer,
    AdminLoginSerializer,
    IdentifyCustomerSerializer,
    LoginSerializer,
    OnlineOrderItemSerializer,
    PatientSerializer,
    PurchaseOrderSerializer,
    RegisterDeleteSerializer,
    RegisterDetailSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SendOtpSerializer,
    VerifyOtpSerializer,
    StaffSerializer,
    SupplierSerializer,
    VerifyPasswordSerializer,
)

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer

    @action(detail=False, methods=['get'], url_path='catcodes')
    def catcodes(self, request):
        """GET /api/categories/catcodes/ – list all category id and catcode."""
        qs = Category.objects.all().order_by('id')
        serializer = CategoryCatcodeSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='medicines')
    def medicines(self, request, pk=None):
        """GET /api/categories/{id}/medicines/ – list all medicines for this category."""
        category = self.get_object()
        qs = Medicine.objects.filter(category=category).select_related('media').order_by('-id')
        serializer = MedicineSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


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


class MedicalItemViewSet(viewsets.ModelViewSet):
    queryset = MedicalItem.objects.all().order_by('-id').select_related('media')
    serializer_class = MedicalItemSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-id')
    serializer_class = SupplierSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-id').prefetch_related('items').select_related('supplier', 'emp')
    serializer_class = PurchaseOrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('-id')
    serializer_class = CartSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all().order_by('-id')
    serializer_class = CouponSerializer
    parser_classes = [JSONParser, PlainTextJSONParser]


class AddItemToCartAPIView(APIView):
    """POST /api/cart/item/add/ - Add or update item in cart. Rate from medical item master (MedicalItem)."""
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = AddItemToCartSerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        order_no = serializer.validated_data['order_no']
        mcode = serializer.validated_data['mcode']
        qty = serializer.validated_data['qty']

        cart = Cart.objects.filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        product = MedicalItem.objects.filter(mcode=mcode).first()
        if not product:
            return Response(
                {'error': f'Medical item with mcode "{mcode}" not found in medical item master.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Use MRP minus sell_discount% as the effective selling price so that
        # cart item amounts, order summary, and admin order totals all align.
        mrp = product.mrp or Decimal('0')
        discount_pct = product.sell_discount or Decimal('0')
        if discount_pct:
            rate = mrp - (mrp * discount_pct / Decimal('100'))
        else:
            rate = mrp
        rate = rate.quantize(Decimal('0.01'))
        amt = qty * rate

        line, created = OnlineOrderItem.objects.update_or_create(
            cart=cart,
            item_code=mcode,
            defaults={'qty': qty, 'rate': rate, 'amt': amt},
        )
        return Response(
            {
                'message': 'Updated item in cart.' if not created else 'Item added to cart.',
                'item': OnlineOrderItemSerializer(line).data,
            },
            status=status.HTTP_200_OK,
        )


def _parse_post_json(request):
    """Use request.data; if empty, parse request.body as JSON (handles missing Content-Type)."""
    if request.data:
        return request.data
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            pass
    return {}


def _resolve_cart_line(cart, mcode):
    """
    Resolve mcode to a medical item, then find the corresponding cart line.
    Cart stores the mcode value in OnlineOrderItem.item_code.
    """
    product = MedicalItem.objects.filter(mcode=mcode).first()
    if not product:
        return None, 'product'
    line = OnlineOrderItem.objects.filter(cart=cart, item_code=mcode).first()
    return line, None if line else 'cart'


class IncrementCartItemAPIView(APIView):
    """POST /api/cart/item/increment/ - Increase qty of an item in cart by 1."""
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = CartItemIdentifySerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        order_no = serializer.validated_data['order_no']
        mcode = serializer.validated_data['mcode']

        cart = Cart.objects.filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        line, reason = _resolve_cart_line(cart, mcode)
        if reason == 'product':
            return Response(
                {'error': f'Medical item with mcode "{mcode}" not found in medical item master.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if reason == 'cart':
            return Response(
                {'error': f'Item with mcode "{mcode}" not found in cart.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        line.qty += 1
        line.amt = line.qty * line.rate
        line.save()
        return Response(
            {'message': 'Item quantity increased.', 'item': OnlineOrderItemSerializer(line).data},
            status=status.HTTP_200_OK,
        )


class DecrementCartItemAPIView(APIView):
    """POST /api/cart/item/decrement/ - Decrease qty of an item in cart by 1 (min 1)."""
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = CartItemIdentifySerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        order_no = serializer.validated_data['order_no']
        mcode = serializer.validated_data['mcode']

        cart = Cart.objects.filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        line, reason = _resolve_cart_line(cart, mcode)
        if reason == 'product':
            return Response(
                {'error': f'Medical item with mcode "{mcode}" not found in medical item master.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if reason == 'cart':
            return Response(
                {'error': f'Item with mcode "{mcode}" not found in cart.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if line.qty <= 1:
            return Response(
                {'error': 'Quantity is already 1. Use delete API to remove item from cart.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        line.qty -= 1
        line.amt = line.qty * line.rate
        line.save()
        return Response(
            {'message': 'Item quantity decreased.', 'item': OnlineOrderItemSerializer(line).data},
            status=status.HTTP_200_OK,
        )


class DeleteCartItemAPIView(APIView):
    """POST /api/cart/item/delete/ - Remove an item from cart. GET with query params also supported."""
    parser_classes = [JSONParser, PlainTextJSONParser]

    def _delete_item(self, order_no, mcode):
        cart = Cart.objects.filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        line, reason = _resolve_cart_line(cart, mcode)
        if reason == 'product':
            return Response(
                {'error': f'Medical item with mcode "{mcode}" not found in medical item master.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if reason == 'cart':
            return Response(
                {'error': f'Item with mcode "{mcode}" not found in cart.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        line.delete()
        return Response(
            {'message': 'Item removed from cart.'},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CartItemIdentifySerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        return self._delete_item(
            serializer.validated_data['order_no'],
            serializer.validated_data['mcode'],
        )

    def get(self, request):
        """Allow GET with ?order_no=...&mcode=... for clients that send GET (e.g. browser)."""
        serializer = CartItemIdentifySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return self._delete_item(
            serializer.validated_data['order_no'],
            serializer.validated_data['mcode'],
        )


class OrderSummaryAPIView(APIView):
    """GET /api/cart/summary/ – Order summary for a cart: subtotal, discount, total."""
    def get(self, request):
        order_no = request.query_params.get('order_no')
        if not order_no and request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
                order_no = data.get('order_no')
            except (ValueError, UnicodeDecodeError, AttributeError):
                pass
        if not order_no:
            return Response(
                {'error': 'Query parameter order_no is required, or send JSON body with order_no.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart = Cart.objects.prefetch_related('items').filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        subtotal = cart.items.aggregate(s=Sum('amt'))['s'] or Decimal('0')
        discount = getattr(cart, 'discount', None) or Decimal('0')
        total = subtotal - discount
        return Response(
            {
                'order_no': cart.order_no,
                'items': OnlineOrderItemSerializer(cart.items.all(), many=True).data,
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        data = _parse_post_json(request)
        order_no = data.get('order_no')
        if not order_no:
            return Response(
                {'error': 'Body field order_no is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart = Cart.objects.prefetch_related('items').filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        subtotal = cart.items.aggregate(s=Sum('amt'))['s'] or Decimal('0')
        discount = getattr(cart, 'discount', None) or Decimal('0')
        total = subtotal - discount
        return Response(
            {
                'order_no': cart.order_no,
                'items': OnlineOrderItemSerializer(cart.items.all(), many=True).data,
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
            },
            status=status.HTTP_200_OK,
        )


# ---- Auth API views ----


class CustomerAddressAPIView(APIView):
    """Get or create/update customer address. When authenticated, customer_code is taken from backend (logged-in user)."""
    authentication_classes = [TokenAuthentication]
    permission_classes = []  # optional auth: support both with and without token
    parser_classes = [JSONParser, PlainTextJSONParser]

    def _get_profile_from_request(self, request):
        """If authenticated, return profile and None; else return None and error response or (None, None)."""
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                return None, Response(
                    {'error': 'User profile not found. Please complete registration.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            customer_code = getattr(profile, 'customer_code', None)
            if not customer_code:
                return None, Response(
                    {'error': 'Customer code not found. Please log in again or contact support.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return profile, None
        return None, None

    def get(self, request):
        # Authenticated: use logged-in user's profile (customer_code from backend)
        profile, err = self._get_profile_from_request(request)
        if err is not None:
            return err
        if profile is not None:
            try:
                address = profile.address
            except CustomerAddress.DoesNotExist:
                return Response(
                    {'error': 'Address not found. Add your address first.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(CustomerAddressSerializer(address).data, status=status.HTTP_200_OK)
        # Not authenticated: require customer_code in query
        customer_code = request.query_params.get('customer_code')
        if not customer_code:
            return Response(
                {'error': 'Query parameter customer_code is required, or log in and send Authorization: Token <token>.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = UserProfile.objects.filter(customer_code=customer_code).first()
        if not profile:
            return Response(
                {'error': f'Customer with customer_code "{customer_code}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            address = profile.address
        except CustomerAddress.DoesNotExist:
            return Response(
                {'error': f'Address not found for customer_code "{customer_code}".'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CustomerAddressSerializer(address).data, status=status.HTTP_200_OK)

    def post(self, request):
        data = _parse_post_json(request) or {}
        # If body has no customer_code and user is not authenticated, require login (clear error)
        has_customer_code = bool(data.get('customer_code', ''))
        profile, err = self._get_profile_from_request(request)
        if err is not None:
            return err
        if profile is not None:
            # Authenticated: customer_code from backend; body does not need customer_code
            input_serializer = CustomerAddressAuthenticatedInputSerializer(data=data)
            input_serializer.is_valid(raise_exception=True)
            address, _created = CustomerAddress.objects.update_or_create(
                profile=profile,
                defaults=input_serializer.validated_data,
            )
            return Response(CustomerAddressSerializer(address).data, status=status.HTTP_200_OK)
        if not has_customer_code:
            return Response(
                {
                    'error': 'Authorization required. Send header: Authorization: Token <your-token> to add address (customer_code is taken from backend), or include customer_code in the body.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Not authenticated but customer_code provided in body
        input_serializer = CustomerAddressInputSerializer(data=data)
        input_serializer.is_valid(raise_exception=True)
        customer_code = input_serializer.validated_data.pop('customer_code')
        profile = UserProfile.objects.filter(customer_code=customer_code).first()
        if not profile:
            return Response(
                {'error': f'Customer with customer_code "{customer_code}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        address, _created = CustomerAddress.objects.update_or_create(
            profile=profile,
            defaults=input_serializer.validated_data,
        )
        return Response(CustomerAddressSerializer(address).data, status=status.HTTP_200_OK)


class ConfirmOrderAPIView(APIView):
    """POST /api/orders/confirm/ – Confirm cart as order. Authenticated; validates cart, address; recalculates totals; locks cart."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        # 1. Get or create logged-in user's profile and customer_code.
        # For legacy/test users created without going through the Register API,
        # automatically create a UserProfile so checkout can still work.
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=request.user,
                name=getattr(request.user, "username", "") or "Customer",
                phone=getattr(request.user, "username", None),
            )
        customer_code = (getattr(profile, 'customer_code', None) or '').strip()
        if not customer_code:
            profile.save()  # triggers auto-generation of customer_code
            customer_code = (getattr(profile, 'customer_code', None) or '').strip()
        if not customer_code:
            return Response(
                {'error': 'Customer code not found for this user.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = _parse_post_json(request)
        serializer = ConfirmOrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order_no = serializer.validated_data['order_no']
        address_id = serializer.validated_data['address_id']
        payment_mode = serializer.validated_data['payment_mode']

        # 2. Fetch cart by order_no (must be CART to confirm; if already ORDERED, return existing order info)
        cart = Cart.objects.prefetch_related('items').filter(order_no=order_no).first()
        if not cart:
            return Response(
                {'error': f'Cart with order_no "{order_no}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if cart.delivery_status != 'CART':
            # Already confirmed – return existing order so frontend can show success and clear cart
            return Response(
                {
                    'message': 'Order was already confirmed.',
                    'order_no': cart.order_no,
                    'invoice_no': cart.inv_no or '',
                    'total_amount': cart.total_amount,
                    'courier_amount': cart.courier_amount,
                    'net_amount': cart.net_amount,
                    'payment_mode': cart.payment_mode or payment_mode,
                    'delivery_status': cart.delivery_status,
                },
                status=status.HTTP_200_OK,
            )

        # 3. Ensure cart belongs to this customer (ccode empty or match).
        # Normalize ccode (trim spaces) before comparing so minor formatting issues
        # don't incorrectly trigger "belongs to another customer".
        existing_ccode = (cart.ccode or '').strip()
        normalized_customer_code = (customer_code or '').strip()
        if existing_ccode and existing_ccode != normalized_customer_code:
            return Response(
                {'error': 'This cart belongs to another customer.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        cart.ccode = normalized_customer_code

        # 4. Ensure cart has items
        if not cart.items.exists():
            return Response(
                {'error': 'Cart has no items. Add items before confirming.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5. Ensure address belongs to user
        try:
            address = CustomerAddress.objects.get(id=address_id)
        except CustomerAddress.DoesNotExist:
            return Response(
                {'error': f'Address with id {address_id} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if address.profile_id != profile.pk:
            return Response(
                {'error': 'This address does not belong to you.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 6. Recalculate totals (backend only)
        subtotal = cart.items.aggregate(s=Sum('amt'))['s'] or Decimal('0')
        discount = getattr(cart, 'discount', None) or Decimal('0')
        total_amount = subtotal - discount
        courier_amount = Decimal('0')
        net_amount = total_amount + courier_amount

        # 7. Generate inv_no
        date_part = now().strftime('%y%m%d')
        while True:
            inv_no = f"INV{date_part}{get_random_string(4, allowed_chars='0123456789')}"
            if not Cart.objects.filter(inv_no=inv_no).exists():
                break

        # 8. Lock cart: update inv_no, delivery_status, amounts, ccode, payment_mode, and timestamp
        cart.inv_no = inv_no
        cart.delivery_status = 'ORDERED'
        cart.total_amount = total_amount
        cart.courier_amount = courier_amount
        cart.net_amount = net_amount
        cart.payment_mode = payment_mode
        # Ensure the admin views show the exact confirmation time.
        cart.date = now().date()
        cart.time = now().time()
        cart.save()

        return Response(
            {
                'message': 'Order confirmed successfully',
                'order_no': cart.order_no,
                'invoice_no': inv_no,
                'total_amount': total_amount,
                'courier_amount': courier_amount,
                'net_amount': net_amount,
                'payment_mode': payment_mode,
                'delivery_status': cart.delivery_status,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminOrderListAPIView(APIView):
    """GET /api/admin/orders/ – List all orders (confirmed orders only, i.e. delivery_status != 'CART'). Requires authentication for customer recognition."""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only list confirmed orders (exclude carts still in progress)
        carts = (
            Cart.objects
            .exclude(delivery_status='CART')
            .exclude(order_no='')
            .prefetch_related('items')
            .order_by('-date', '-time', '-id')
        )
        # Optional filter by status (e.g. ?status=ordered)
        status_filter = request.query_params.get('status', '').strip().lower()
        if status_filter:
            carts = carts.filter(delivery_status__iexact=status_filter)

        results = []
        for cart in carts:
            order_date = None
            if cart.date and cart.time:
                try:
                    order_date = datetime.combine(cart.date, cart.time).isoformat()
                except Exception:
                    order_date = f'{cart.date}' if cart.date else None
            elif cart.date:
                order_date = f'{cart.date}T00:00:00'
            order_status = (cart.delivery_status or 'cart').lower()
            payment_status = 'paid' if (order_status == 'ordered' and cart.payment_mode) else 'pending'
            payment_method = (cart.payment_mode or '').lower() or None
            customer_name = ''
            customer_id = None
            if cart.ccode:
                profile = UserProfile.objects.filter(customer_code=cart.ccode).first()
                if profile:
                    customer_id = profile.id
                    customer_name = profile.name or ''
            # Use total quantity across all lines (not just line count)
            item_count = cart.items.aggregate(c=Sum('qty'))['c'] or 0
            results.append({
                'order_id': cart.order_no,
                'cart_id': cart.id,
                'order_date': order_date,
                'order_status': order_status,
                'payment_status': payment_status,
                'payment_method': payment_method,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'item_count': item_count,
                'final_total': float(cart.net_amount or 0),
            })
        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)


class AdminOrderDetailAPIView(APIView):
    """GET /api/admin/orders/{order_id}/ – Order details. order_id = Cart.id (int) or order_no (string). Requires authentication for customer recognition."""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        cart = None
        try:
            pk = int(order_id)
            cart = Cart.objects.prefetch_related('items').filter(pk=pk).first()
        except (ValueError, TypeError):
            cart = Cart.objects.prefetch_related('items').filter(order_no=order_id).first()
        if not cart:
            return Response(
                {'error': f'Order with id or order_no "{order_id}" not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        order_date = None
        if cart.date and cart.time:
            try:
                order_date = datetime.combine(cart.date, cart.time).isoformat()
            except Exception:
                order_date = f'{cart.date}' if cart.date else None
        elif cart.date:
            order_date = f'{cart.date}T00:00:00'

        order_status = (cart.delivery_status or 'cart').lower()
        payment_status = 'paid' if (order_status == 'ordered' and cart.payment_mode) else 'pending'
        payment_method = (cart.payment_mode or '').lower() or None

        customer = {
            'customer_id': None,
            'name': '',
            'phone': '',
            'email': '',
        }
        shipping_addr = {
            'full_name': '',
            'phone': '',
            'address_line1': '',
            'address_line2': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': '',
        }
        if cart.ccode:
            profile = UserProfile.objects.filter(customer_code=cart.ccode).first()
            if profile:
                customer['customer_id'] = profile.id
                customer['name'] = profile.name or ''
                customer['phone'] = profile.phone or ''
                customer['email'] = getattr(profile.user, 'email', '') or ''
                try:
                    addr = profile.address
                    shipping_addr['full_name'] = f"{(addr.prefix or '').strip()} {profile.name or ''}".strip() or addr.address[:50]
                    shipping_addr['phone'] = profile.phone or ''
                    shipping_addr['address_line1'] = addr.address or ''
                    shipping_addr['address_line2'] = ''
                    shipping_addr['city'] = addr.post or ''
                    shipping_addr['state'] = addr.state or ''
                    shipping_addr['postal_code'] = addr.pin or ''
                    shipping_addr['country'] = addr.country or ''
                except CustomerAddress.DoesNotExist:
                    pass

        items_payload = []
        for line in cart.items.all():
            product_name = line.item_code
            product_id = None
            item_obj = Item.objects.filter(
                Q(sku_code=line.item_code) | Q(item_code=line.item_code)
            ).first()
            if item_obj:
                product_name = item_obj.sku_name or line.item_code
                product_id = item_obj.id
            items_payload.append({
                'order_item_id': line.id,
                'product_id': product_id,
                'product_name': product_name,
                'variant': {},
                'quantity': int(line.qty),
                'price': float(line.rate),
                'subtotal': float(line.amt),
            })

        subtotal = cart.items.aggregate(s=Sum('amt'))['s'] or Decimal('0')
        summary = {
            'subtotal': float(subtotal),
            'tax': 0.0,
            'shipping_fee': float(cart.courier_amount or 0),
            'discount': float(cart.discount or 0),
            'coupon_code': None,
            'final_total': float(cart.net_amount or 0),
        }

        return Response({
            'order_id': cart.order_no,
            'order_date': order_date,
            'order_status': order_status,
            'payment_status': payment_status,
            'payment_method': payment_method,
            'customer': customer,
            'addresses': {
                'shipping': shipping_addr,
                'billing': shipping_addr,
            },
            'items': items_payload,
            'summary': summary,
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """Register a new user (POST) and fetch current user's registration details (GET)."""
    authentication_classes = [TokenAuthentication]
    permission_classes = []  # POST is open; GET requires token (checked inside)

    def get(self, request):
        """GET /api/auth/register/ – return current logged-in user's registration details."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found for this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {
            'customer_code': (getattr(profile, 'customer_code', None) or '').strip(),
            'name': profile.name or '',
            'email': request.user.email or '',
            'phone': profile.phone or request.user.username or '',
            'username': request.user.username or '',
        }
        serializer = RegisterDetailSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result['user']
        password = result['password']
        token, _ = Token.objects.get_or_create(user=user)
        name = getattr(user.profile, 'name', None) or ''
        from .notification_utils import send_registration_email, send_registration_sms
        email_sent, email_error = send_registration_email(
            user.email, user.username, password, name=name or None
        )
        send_registration_sms(user.username, user.username, password)
        msg = 'User registered successfully. Username and password sent to your email and mobile.'
        if not email_sent:
            msg = 'User registered successfully. Credentials are below; email could not be sent.'
        customer_code = getattr(user.profile, 'customer_code', None) or ''
        payload = {
            'message': msg,
            'customer_code': customer_code,
            'username': user.username,
            'email': user.email,
            'password': password,
            'token': token.key,
            'email_sent': email_sent,
        }
        if not email_sent and email_error:
            payload['email_error'] = email_error
        return Response(payload, status=status.HTTP_201_CREATED)


class IdentifyCustomerAPIView(APIView):
    """POST /api/auth/identify-customer/ – Identify if a mobileNumber belongs to an existing customer."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = IdentifyCustomerSerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobileNumber'].strip()
        if not mobile:
            return Response({'status': 'NEW_CUSTOMER'}, status=status.HTTP_200_OK)

        # In this project, we use phone/mobileNumber as username for login.
        user = User.objects.filter(username=mobile).first()
        if not user:
            return Response({'status': 'NEW_CUSTOMER'}, status=status.HTTP_200_OK)

        # Existing customer – return a richer payload (useful for frontend), but keep the
        # requested NEW_CUSTOMER status for non-existing ones only.
        try:
            profile = user.profile
            customer_code = (getattr(profile, 'customer_code', None) or '').strip()
            name = profile.name or ''
            phone = profile.phone or user.username or ''
        except UserProfile.DoesNotExist:
            customer_code = ''
            name = ''
            phone = user.username or mobile

        return Response(
            {
                'status': 'EXISTING_CUSTOMER',
                'customer_code': customer_code,
                'name': name,
                'email': user.email or '',
                'phone': phone,
                'username': user.username or mobile,
            },
            status=status.HTTP_200_OK,
        )


class SendOtpAPIView(APIView):
    """POST /api/auth/send-otp/ – Generate and store an OTP for the given mobileNumber/email."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = SendOtpSerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobileNumber'].strip()
        email = serializer.validated_data['email'].strip()

        # Generate a 6-digit numeric OTP and store it for potential future verification.
        from django.utils.crypto import get_random_string
        code = get_random_string(6, allowed_chars='0123456789')
        otp = OneTimePassword.objects.create(
            mobile_number=mobile,
            email=email or None,
            code=code,
            purpose=OneTimePassword.PURPOSE_REGISTER,
        )

        # Build reference ID and TTL in seconds based on the stored expires_at.
        from django.utils.timezone import now as tz_now
        expiry_seconds = max(0, int((otp.expires_at - tz_now()).total_seconds()))
        otp_reference_id = f"OTP{otp.id:06d}"

        # Send OTP via email and SMS (if configured)
        from .notification_utils import send_otp_email, send_otp_sms
        send_otp_email(email, code)
        send_otp_sms(mobile, code)

        return Response(
            {
                'status': 'OTP_SENT',
                'otpReferenceId': otp_reference_id,
                'channels': ['EMAIL', 'SMS'],
                'expiryInSeconds': expiry_seconds,
            },
            status=status.HTTP_200_OK,
        )


class VerifyOtpAPIView(APIView):
    """POST /api/auth/verify-otp/ – Verify an OTP and generate a customerCode."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=_parse_post_json(request))
        serializer.is_valid(raise_exception=True)
        ref = serializer.validated_data['otpReferenceId'].strip()
        otp_code = serializer.validated_data['otp'].strip()

        if not ref.startswith('OTP') or not ref[3:].isdigit():
            return Response(
                {'error': 'Invalid otpReferenceId format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp_id = int(ref[3:])

        otp = OneTimePassword.objects.filter(id=otp_id).first()
        if not otp:
            return Response(
                {'error': 'OTP not found.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not otp.is_valid:
            return Response(
                {'error': 'OTP has expired or already been used.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.code != otp_code:
            return Response(
                {'error': 'Invalid OTP code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Determine if this is a new customer (no User with this mobileNumber).
        user = User.objects.filter(username=otp.mobile_number).first()
        is_new_customer = user is None

        # Generate or reuse a customer_code for this OTP.
        if not (otp.customer_code or '').strip():
            from django.utils.crypto import get_random_string
            date_part = now().strftime('%y%m%d')
            while True:
                candidate = f"CUST{date_part}{get_random_string(4, allowed_chars='0123456789')}"
                if not UserProfile.objects.filter(customer_code=candidate).exists():
                    otp.customer_code = candidate
                    break

        from django.utils.timezone import now as tz_now
        otp.verified_at = tz_now()
        otp.save()

        # Issue a token for both new and existing customers.
        if user is None:
            # New customer: create minimal User and UserProfile so we can issue a Token.
            from django.utils.crypto import get_random_string
            password = get_random_string(12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789')
            user = User.objects.create_user(
                username=otp.mobile_number,
                email=(otp.email or '').strip() or f"{otp.mobile_number}@otp.local",
                password=password,
            )
            UserProfile.objects.create(
                user=user,
                name='',
                phone=otp.mobile_number,
                customer_code=otp.customer_code,
            )
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                'status': 'OTP_VERIFIED',
                'customerCode': otp.customer_code,
                'isNewCustomer': is_new_customer,
                'token': token.key,
            },
            status=status.HTTP_200_OK,
        )


class AdminLoginAPIView(APIView):
    """POST /api/admin/login/ – Admin login with username and password. Returns auth token. User must be staff or superuser."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Access denied. Admin privileges required.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Admin login successful.',
            'token': token.key,
            'username': user.username,
        }, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful.',
            'token': token.key,
            'username': user.username,
        })


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'message': 'If an account exists with this email, a reset link has been sent.'},
                status=status.HTTP_200_OK,
            )
        PasswordResetToken.objects.filter(user=user).delete()
        reset = PasswordResetToken.objects.create(user=user)
        return Response({
            'message': 'Password reset token generated.',
            'token': reset.token,
        }, status=status.HTTP_200_OK)


class VerifyPasswordAPIView(APIView):
    def post(self, request):
        serializer = VerifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['token']
        try:
            reset = PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_200_OK)
        if not reset.is_valid():
            reset.delete()
            return Response({'valid': False}, status=status.HTTP_200_OK)
        return Response({'valid': True}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            reset = PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not reset.is_valid():
            reset.delete()
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = reset.user
        user.set_password(new_password)
        user.save()
        reset.delete()
        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class RegisterDeleteAPIView(APIView):
    """Delete the authenticated user's account (register delete)."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        password = serializer.validated_data.get('password')
        if password and not user.check_password(password):
            return Response(
                {'error': 'Invalid password. Provide correct password to delete account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(
            {'message': 'Your account has been deleted successfully.'},
            status=status.HTTP_200_OK,
        )
