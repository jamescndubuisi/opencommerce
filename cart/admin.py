from django.contrib import admin
from .models import Cart, Packet
# Register your models here.
# class CartAdmin(admin.ModelAdmin):
     # list_editable = ['id']
admin.site.register(Cart)
admin.site.register(Packet)