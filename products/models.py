from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    parent = models.ForeignKey(
        'self',
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Auto-generate slug if empty """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse("products:product_list") + f"?category={self.slug}"



class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='products')
    image = models.ImageField(upload_to='products/',blank=True, null=True)
    is_active =  models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"


    def __str__ (self):
        return self.name

    def save(self, *args, **kwargs):
        """ Auto-generate slug if empty """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})


    @property
    def is_discounted(self):
        return self.old_price and self.old_price > self.price

    @property
    def discount_percent(self):
        if self.is_discounted:
            return int(100 - (self.price / self.old_price * 100))
        return 0

