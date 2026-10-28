from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Ocassion(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='categories')
    ocasions = models.ManyToManyField(Ocassion, related_name='ocasions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="colors")
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)
    stock = models.PositiveIntegerField(default = 0)

    class Meta:
        unique_together = ("product", "color", "size")

    def __str__(self):
        return f"{self.product.name} - {self.color.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="images")
    image = models.ImageField(upload_to = "products/")

    def __str__(self):
        return f"Image for{self.product.name}"

 

