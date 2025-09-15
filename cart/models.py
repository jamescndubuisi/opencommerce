from django.db import models
from django.conf import settings
from products.models import Product
# from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from paystack.api import signals
import uuid
from decimal import Decimal
from django.db.models.signals import post_save
import logging
# from django.dispatch import receiver
from django.db.models.signals import post_delete
User = settings.AUTH_USER_MODEL
from django.db import transaction
# Create your models here.


# class CartManager(models.Manager):
#
#     def new_or_get(self, request):
#         cart_id = request.session.get("cart_id")
#         # print(cart_id)
#         query = self.get_queryset().filter(user=request.user, paid=False)
#
#         if query.count() == 1:
#             new_object = False
#             cart = query.first()
#             if request.user.is_authenticated and cart.user is None:
#                 cart.user = request.user
#                 cart.save()
#         else:
#             new_object = True
#             cart = Cart.objects.new_cart(user=request.user)
#
#         return cart, new_object
#
#     def new_cart(self, user=None):
#         site_user = None
#         if user is not None:
#             if user.is_authenticated:
#                 site_user = user
#         return self.model.objects.create(user=site_user)


# class CartManager(models.Manager):
#
#     def new_or_get(self, request):
#         """
#         Session-aware cart retrieval:
#          - If a cart_id is present in session, return that (if not paid).
#          - Otherwise try to find an active cart for authenticated user.
#          - Otherwise create a new cart and set session['cart_id'].
#         """
#         cart_obj = None
#         new_object = False
#         cart_id = request.session.get("cart_id")
#
#         if cart_id:
#             try:
#                 cart_obj = self.get_queryset().get(id=cart_id, paid=False)
#             except (self.model.DoesNotExist, ValueError):
#                 cart_obj = None
#
#         if cart_obj is None and request.user.is_authenticated:
#             cart_obj = self.get_queryset().filter(user=request.user, paid=False).first()
#             if cart_obj:
#                 request.session['cart_id'] = str(cart_obj.id)
#
#         if cart_obj is None:
#             new_object = True
#             cart_obj = self.new_cart(user=request.user if request.user.is_authenticated else None)
#             request.session['cart_id'] = str(cart_obj.id)
#
#         # attach user if needed
#         if request.user.is_authenticated and cart_obj.user is None:
#             cart_obj.user = request.user
#             cart_obj.save()
#
#         return cart_obj, new_object
#


class CartManager(models.Manager):
    """
    Session-aware Cart manager.
    Provides:
     - new_or_get(request): returns (cart, created_bool)
     - new_cart(user=None): creates a new cart optionally attached to an authenticated user
    """

    def new_or_get(self, request):
        # >>> CHANGED: session-aware retrieval and robust fallback logic
        cart_obj = None
        new_object = False
        cart_id = request.session.get("cart_id")

        if cart_id:
            try:
                cart_obj = self.get_queryset().get(id=cart_id, paid=False)
            except (self.model.DoesNotExist, ValueError):
                cart_obj = None

        # If not found in session and user is authenticated, try user's active cart
        if cart_obj is None and getattr(request, "user", None) and request.user.is_authenticated:
            cart_obj = self.get_queryset().filter(user=request.user, paid=False).first()
            if cart_obj:
                request.session["cart_id"] = str(cart_obj.id)

        # If still none — create a new one and store in session
        if cart_obj is None:
            new_object = True
            cart_obj = self.new_cart(user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None)
            request.session["cart_id"] = str(cart_obj.id)

        # Attach user if a logged-in user and cart has no owner
        if getattr(request, "user", None) and request.user.is_authenticated and cart_obj.user is None:
            cart_obj.user = request.user
            cart_obj.save()

        return cart_obj, new_object

    def new_cart(self, user=None):
        # >>> CHANGED: ensure new_cart exists and handles anonymous users safely
        site_user = None
        if user is not None and getattr(user, "is_authenticated", False):
            site_user = user
        return self.model.objects.create(user=site_user)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    products = models.ManyToManyField(Product, blank=True, through="Packet")
    total = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item_count = models.IntegerField(default=0)
    paid = models.BooleanField(default=False)
    # temp_id = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    temp_id = models.CharField(max_length=36,blank=True, null=True,  unique=True, default=uuid.uuid4,)

    objects = CartManager()

    def check_and_delete(self, sender, instance, created, **kwargs):
        if instance.item_count == 0:
            instance.delete()

    def __str__(self):
        return str(self.id)

    def update_totals(self):
        """
        Recompute cart.total and cart.item_count from Packet objects.
        Call this after packet create/update/delete.
        """
        packets = self.packet_set.all()
        total = Decimal('0.00')
        item_count = 0
        for p in packets:
            # ensure sub_total has Decimal
            total += p.sub_total or Decimal('0.00')
            item_count += p.count or 0
        # Avoid recursive save triggers — only save if changed
        if self.total != total or self.item_count != item_count:
            self.total = total
            self.item_count = item_count
            # Use update to avoid triggering signals unnecessarily:
            self.save()


# class Packet(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product,on_delete=models.CASCADE)
#     count = models.IntegerField(default=1)
#     sub_total = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def check_and_delete(self, sender, instance, created, **kwargs):
#         if instance.count == 0:
#             instance.delete()
#
#     def __str__(self):
#         return self.product.title + " " + "Packet"

class Packet(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # >>> CHANGED: default

    def save(self, *args, **kwargs):
        # >>> CHANGED: automatically maintain sub_total based on product.price & count
        if self.product:
            self.sub_total = Decimal(self.product.price) * int(self.count)
        super().save(*args, **kwargs)
        # update the cart totals after packet saved
        if self.cart:
            self.cart.update_totals()

    @staticmethod
    def check_and_delete(sender, instance, created, **kwargs):
        if instance.count == 0:
            instance.delete()


# def cart_price_update_reciever(sender,instance,action, *args, **kwargs):
#     print(action)
#     products = instance.products.all()
#     total = 0
#     for item in products:
#         total += item.price
#     print(total)
#     instance.total=total
#     instance.save()
#
#
# m2m_changed.connect(cart_price_update_reciever, sender=Cart.products.through)


# @receiver(signals.payment_verified)
# def on_successful_payment(sender, ref, **kwargs):
#     print(ref)
#     cart = Cart.objects.get(temp_id=ref)
#     cart.paid = True
#     cart.save()

@receiver(signals.payment_verified)
def on_successful_payment(sender, ref, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("Payment verified for ref %s", ref)
    print(ref)
    try:
        cart = Cart.objects.get(temp_id=ref)
        cart.paid = True
        cart.save()
    except Cart.DoesNotExist:
        logger.error("on_successful_payment: no cart found with temp_id=%s", ref)


@receiver(post_save, sender=Packet)
def handle_packet_save(sender, instance, created, **kwargs):
    instance.check_and_delete(sender, instance, created)


@receiver(post_delete, sender=Packet)
def handle_packet_delete(sender, instance, **kwargs):
    """
    When a packet is deleted, recompute cart totals.
    """
    cart = instance.cart
    if cart:
        cart.update_totals()


# @receiver(post_save, sender=Cart)
# @receiver(post_save, sender=Cart)
# def handle_cart_save(sender, instance, created, **kwargs):
#     instance.check_and_delete(sender, instance, created)
