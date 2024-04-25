from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Product
from cart.models import Cart
# Create your views here.

class ProductListView(ListView):
    queryset = Product.objects.all()


    def get_context_data(self, *args, **kwargs):
        Cart.objects.new_or_get(self.request)
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['title'] = "Product List"
        context['search'] = False
        return context


class ProductDetailView(DetailView):
    queryset = Product.objects.all()


    def get_context_data(self, *args, **kwargs):
        Cart.objects.new_or_get(self.request)
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['title'] = "Product Detail"
        cart, created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart
        return context

class ProductSearchView(ListView):
    queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(ProductSearchView, self).get_context_data(**kwargs)
        context['title'] = "Search Results"
        context['search'] = True
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        print(request.GET)
        query = request.GET.get("q")
        if query is not None:
            lookups = Q(title__icontains=query)|Q(description__icontains=query)
            return Product.objects.filter(lookups).distinct()
        return Product.objects.none()

