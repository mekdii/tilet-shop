from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator , MinValueValidator

# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name="reviews")
    product = models.ForeignKey("store.product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0) , MaxValueValidator(5)])
    comment = models.TextField(blank= True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="one_review_per_user_product")]

    def __str__(self):
        return f"{self.user} -  {self.product} ({self.rating}/5)"