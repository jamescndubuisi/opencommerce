from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Packet
from products.models import Product
import uuid
import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction

logger = logging.getLogger(__name__)

# Create your views here.


# def cart_home(request):
#     title = "Cart"
#     cart, created = Cart.objects.new_or_get(request)
#     packets = Packet.objects.filter(cart=cart)
#     print(created)
#     unique_id = str(uuid.uuid4())
#     instance = Cart.objects.get(id=cart.id)
#     instance.temp_id=unique_id
#     instance.save()
#     return render(request, "cart/index.html", {"title": title, "cart": cart, "packets": packets, "unique_id": unique_id})


def cart_home(request):
    title = "Cart"
    cart, created = Cart.objects.new_or_get(request)
    packets = Packet.objects.filter(cart=cart)
    return render(request, "cart/index.html", {"title": title, "cart": cart, "packets": packets})


# def add_to_cart(request):
#     product_id = request.POST.get("product_id")
#     print(product_id)
#     if product_id is not None:
#         try:
#             product = Product.objects.get(id=product_id)
#             print(product)
#             cart, created = Cart.objects.new_or_get(request)
#             packet = Packet.objects.filter(cart=cart, product=product_id)
#             if packet.exists():
#                 print("packet exist")
#                 packet = packet.first()
#                 packet.count += 1
#                 packet.sub_total += product.price
#                 cart.total += product.price
#                 cart.item_count += 1
#                 packet.save()
#                 cart.save()
#             else:
#                 packet = Packet.objects.create(cart=cart, count=1, product=product, sub_total=product.price)
#                 cart.total += product.price
#                 print(cart.item_count)
#                 cart.item_count += 1
#                 print(cart.item_count)
#                 cart.save()
#
#         except:
#             print("Terrible")
#             return redirect("cart")
#
#     return redirect("cart")


def add_to_cart(request):
    if request.method != "POST":
        logger.debug("add_to_cart: non-POST request ignored")
        return redirect("cart")

    product_id = request.POST.get("product_id")
    if not product_id:
        logger.debug("add_to_cart: missing product_id")
        return redirect("cart")

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.new_or_get(request)

    # Use transaction and select_for_update to avoid concurrent count issues
    with transaction.atomic():
        packet_qs = Packet.objects.select_for_update().filter(cart=cart, product=product)
        if packet_qs.exists():
            packet = packet_qs.first()
            packet.count += 1
            # packet.save() computes sub_total (see models change) and will update cart totals.
            packet.save()
        else:
            Packet.objects.create(cart=cart, count=1, product=product)  # sub_total set in Packet.save()

    logger.debug("add_to_cart: added product %s to cart %s", product_id, cart.id)
    return redirect("cart")


# def remove_from_cart(request):
#     packet_id = request.POST.get("packet")
#     print(packet_id)
#
#     if packet_id is not None:
#         packet = Packet.objects.get(id=packet_id)
#         cart = packet.cart
#         product = packet.product
#         print(packet)
#         if packet.count == 1:
#             packet.delete()
#             cart.total -= product.price
#             cart.item_count -= 1
#             cart.save()
#
#         else:
#             packet.count -= 1
#             packet.sub_total -= product.price
#             cart.total -= product.price
#             cart.item_count -= 1
#             packet.save()
#             cart.save()
#     else:
#         pass
#     return redirect("cart")


def remove_from_cart(request):
    # >>> CHANGED: only accept POST for destructive ops
    if request.method != "POST":
        logger.debug("remove_from_cart: non-POST request ignored")
        return redirect("cart")

    packet_id = request.POST.get("packet")
    if not packet_id:
        logger.debug("remove_from_cart: missing packet id")
        return redirect("cart")

    packet = get_object_or_404(Packet, id=packet_id)

    with transaction.atomic():
        cart = packet.cart
        if packet.count <= 1:
            # packet.delete() triggers post_delete signal to update cart totals (see models change)
            packet.delete()
            logger.debug("remove_from_cart: packet %s deleted", packet_id)
        else:
            packet.count -= 1
            packet.save()  # Packet.save will re-calc sub_total and then update cart totals

    return redirect("cart")


# def update_cart(request):
#     product_id = request.POST.get("product_id")
#     action = request.POST.get("action")
#     print("product_id is {}".format(product_id))
#     if product_id is not None:
#         try:
#             product = Product.objects.get(id=product_id)
#             print(product)
#             cart, created = Cart.objects.new_or_get(request)
#             print(action)
#             if action == "add":
#                 cart.products.add(product)
#             elif action == "remove":
#                 cart.products.remove(product)
#             else:
#                 pass
#         except:
#             print("Terrible")
#             return redirect("cart")
#
#     return redirect("cart")


def update_cart(request):
    # This endpoint is ambiguous in original code; keep behavior but validate input.
    if request.method != "POST":
        logger.debug("update_cart: non-POST request ignored")
        return redirect("cart")

    product_id = request.POST.get("product_id")
    action = request.POST.get("action")
    if not product_id or not action:
        logger.debug("update_cart: missing product_id or action")
        return redirect("cart")

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.new_or_get(request)

    # Keep original add/remove semantics but recommend using add_to_cart/remove_from_cart instead
    if action == "add":
        # create or increment a Packet
        with transaction.atomic():
            packet_qs = Packet.objects.select_for_update().filter(cart=cart, product=product)
            if packet_qs.exists():
                packet = packet_qs.first()
                packet.count += 1
                packet.save()
            else:
                Packet.objects.create(cart=cart, count=1, product=product)
    elif action == "remove":
        # remove one quantity or delete packet
        with transaction.atomic():
            packet_qs = Packet.objects.select_for_update().filter(cart=cart, product=product)
            if packet_qs.exists():
                packet = packet_qs.first()
                if packet.count <= 1:
                    packet.delete()
                else:
                    packet.count -= 1
                    packet.save()
    else:
        logger.debug("update_cart: unknown action %s", action)

    return redirect("cart")


# def my_order(request):
#     title = "My Orders"
#     orders = Cart.objects.filter(user=request.user, paid=True)
#     print(orders)
#     return render(request, "cart/order_list.html", {"orders": orders, "title": title})
#
#
# def order_detail(request, id):
#     title = "Order Details"
#     order = Cart.objects.get(user=request.user, id=id, paid=True)
#     packets = Packet.objects.filter(cart=order)
#     return render(request, "cart/order_detail.html", {"order": order, "packets": packets, "title": title})

@login_required  # >>> CHANGED: ensure only authenticated users view orders
def my_order(request):
    title = "My Orders"
    orders = Cart.objects.filter(user=request.user, paid=True)
    return render(request, "cart/order_list.html", {"orders": orders, "title": title})


@login_required
def order_detail(request, id):
    title = "Order Details"
    order = get_object_or_404(Cart, user=request.user, id=id, paid=True)
    packets = Packet.objects.filter(cart=order)
    return render(request, "cart/order_detail.html", {"order": order, "packets": packets, "title": title})



