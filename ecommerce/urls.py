from django.contrib import admin
from django.urls import path, include
from portal import urls as portal_url
from cart import urls as cart_urls
from products import urls as product_url
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.dispatch import receiver
from paystack.api import signals


@receiver(signals.successful_payment_signal)
def on_successful_payment(sender, **kwargs):
   print("paid")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(portal_url)),
    path('products/',include(product_url),),
    path('cart/',include(cart_urls),),
    path("paystack/",include(("paystack.frameworks.django.urls", "paystack"), namespace="paystack"),),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns +=  staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)