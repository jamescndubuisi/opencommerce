from django.db import models
from portal.models import User
from django.urls import reverse
# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to="products/%Y/%m/%d")
    price= models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    modified= models.DateTimeField(auto_now = True)
    created= models.DateTimeField(auto_now_add=True)
    owner= models.ForeignKey(User,on_delete=models.CASCADE )
    slug = models.SlugField(blank=True,unique=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail", kwargs={"slug":self.slug})
