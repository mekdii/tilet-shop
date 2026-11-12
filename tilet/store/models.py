from django.db import models
from decimal import Decimal , ROUND_HALF_UP
from django.core.validators import MinValueValidator

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
    weight_grams = models.PositiveIntegerField(default=1000)
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



class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, blank=True)
    decimals = models.PositiveSmallIntegerField(default=2)
    etb_per_unit =models.DecimalField(
        max_digits=14, decimal_places=4, validators=[MinValueValidator(Decimal("0.0001"))]

    )
    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "currencies"

    def convert(self, etb_amount):
        raw  = Decimal(etb_amount)/ self.etb_per_unit * (1 + self.markup_percent /100 )
        return raw.quantize(Decimal(1).scaleb(-self.decimals), rounding=ROUND_HALF_UP) 

    def to_minor_units(self, amount):
        return int(Decimal(amount) * (10 ** self.decimals))

    def __str__(self):
        return self.code

