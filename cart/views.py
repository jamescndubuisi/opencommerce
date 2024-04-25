from django.shortcuts import render, redirect
from .models import Cart, Packet
from products.models import Product
import uuid
from django.contrib.auth.decorators import login_required


# Create your views here.


def cart_home(request):
    title = "Cart"
    cart, created = Cart.objects.new_or_get(request)
    packets = Packet.objects.filter(cart=cart)
    print(created)
    unique_id = str(uuid.uuid4())
    instance = Cart.objects.get(id=cart.id)
    instance.temp_id=unique_id
    instance.save()
    return render(request, "cart/index.html", {"title": title, "cart": cart, "packets": packets, "unique_id": unique_id})


def add_to_cart(request):
    product_id = request.POST.get("product_id")
    print(product_id)
    if product_id is not None:
        try:
            product = Product.objects.get(id=product_id)
            print(product)
            cart, created = Cart.objects.new_or_get(request)
            packet = Packet.objects.filter(cart=cart, product=product_id)
            if packet.exists():
                print("packet exist")
                packet = packet.first()
                packet.count += 1
                packet.sub_total += product.price
                cart.total += product.price
                cart.item_count += 1
                packet.save()
                cart.save()
            else:
                packet = Packet.objects.create(cart=cart, count=1, product=product, sub_total=product.price)
                cart.total += product.price
                print(cart.item_count)
                cart.item_count += 1
                print(cart.item_count)
                cart.save()

        except:
            print("Terrible")
            return redirect("cart")

    return redirect("cart")


def remove_from_cart(request):
    packet_id = request.POST.get("packet")
    print(packet_id)

    if packet_id is not None:
        packet = Packet.objects.get(id=packet_id)
        cart = packet.cart
        product = packet.product
        print(packet)
        if packet.count == 1:
            packet.delete()
            cart.total -= product.price
            cart.item_count -= 1
            cart.save()

        else:
            packet.count -= 1
            packet.sub_total -= product.price
            cart.total -= product.price
            cart.item_count -= 1
            packet.save()
            cart.save()
    else:
        pass
    return redirect("cart")


def update_cart(request):
    product_id = request.POST.get("product_id")
    action = request.POST.get("action")
    print("product_id is {}".format(product_id))
    if product_id is not None:
        try:
            product = Product.objects.get(id=product_id)
            print(product)
            cart, created = Cart.objects.new_or_get(request)
            print(action)
            if action == "add":
                cart.products.add(product)
            elif action == "remove":
                cart.products.remove(product)
            else:
                pass
        except:
            print("Terrible")
            return redirect("cart")

    return redirect("cart")


def my_order(request):
    title = "My Orders"
    orders = Cart.objects.filter(user=request.user, paid=True)
    print(orders)
    return render(request, "cart/order_list.html", {"orders": orders, "title": title})


def order_detail(request, id):
    title = "Order Details"
    order = Cart.objects.get(user=request.user, id=id, paid=True)
    packets = Packet.objects.filter(cart=order)
    return render(request, "cart/order_detail.html", {"order": order, "packets": packets, "title": title})
