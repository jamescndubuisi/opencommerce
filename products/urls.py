from django.urls import path
from .views import ProductListView, ProductDetailView, ProductSearchView


urlpatterns = [

    path('', ProductListView.as_view(), name = "products"),
    path('<int:pk>', ProductDetailView.as_view(), name = "product_pk_detail"),
    path('<slug:slug>', ProductDetailView.as_view(), name = "detail"),
    path('search/', ProductSearchView.as_view(), name = "search"),

]
