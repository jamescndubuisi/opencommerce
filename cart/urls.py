from django.urls import path
from .views import cart_home, add_to_cart, remove_from_cart, update_cart, order_detail, my_order

urlpatterns = [

        path("", cart_home, name="cart"),
        path("remove", remove_from_cart, name="remove_from_cart"),
        path("add", add_to_cart, name="add_to_cart"),
        path("update", update_cart, name="cart_update"),

        path("orders/", my_order, name="order_list"),
        path("orders/<str:id>", order_detail, name="order_details"),

]
