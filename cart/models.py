from django.db import models
from django.conf import settings
from products.models import Product
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from paystack.api import signals
import uuid

from django.db.models.signals import post_save
# from django.dispatch import receiver

User = settings.AUTH_USER_MODEL

# Create your models here.


class CartManager(models.Manager):

    def new_or_get(self, request):
        cart_id = request.session.get("cart_id")
        # print(cart_id)
        query = self.get_queryset().filter(user=request.user, paid=False)

        if query.count() == 1:
            new_object = False
            cart = query.first()
            if request.user.is_authenticated and cart.user is None:
                cart.user = request.user
                cart.save()
        else:
            new_object = True
            cart = Cart.objects.new_cart(user=request.user)

        return cart, new_object

    def new_cart(self, user=None):
        site_user = None
        if user is not None:
            if user.is_authenticated:
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
    temp_id = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    objects = CartManager()

    def check_and_delete(self, sender, instance, created, **kwargs):
        if instance.item_count == 0:
            instance.delete()

    def __str__(self):
        return str(self.id)


class Packet(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def check_and_delete(self, sender, instance, created, **kwargs):
        if instance.count == 0:
            instance.delete()

    def __str__(self):
        return self.product.title + " " + "Packet"


def cart_price_update_reciever(sender,instance,action, *args, **kwargs):
    print(action)
    products = instance.products.all()
    total = 0
    for item in products:
        total += item.price
    print(total)
    instance.total=total
    instance.save()


m2m_changed.connect(cart_price_update_reciever, sender=Cart.products.through)


@receiver(signals.payment_verified)
def on_successful_payment(sender, ref, **kwargs):
    print(ref)
    cart = Cart.objects.get(temp_id=ref)
    cart.paid = True
    cart.save()


@receiver(post_save, sender=Packet)
def handle_packet_save(sender, instance, created, **kwargs):
    instance.check_and_delete(sender, instance, created)


# @receiver(post_save, sender=Cart)
# @receiver(post_save, sender=Cart)
# def handle_cart_save(sender, instance, created, **kwargs):
#     instance.check_and_delete(sender, instance, created)
