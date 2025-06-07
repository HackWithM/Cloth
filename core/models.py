from django.db import models
from django.contrib.auth.models import User
import base64

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class ClothingItem(models.Model):
    CATEGORY_CHOICES = [
        ('TOP', 'Top Wear (Shirts, T-Shirts, etc.)'),
        ('BOTTOM', 'Bottom Wear (Pants, Jeans, Skirts)'),
        ('DRESS', 'Dresses'),
        ('OUTERWEAR', 'Outerwear (Jackets, Coats)'),
        ('FOOTWEAR', 'Footwear'),
        ('ACCESSORY', 'Accessory'),
    ]

    AUDIENCE_CHOICES = [
        ('MEN', "Men's"),
        ('WOMEN', "Women's"),
        ('KIDS', "Kids'"),
        ('UNISEX', 'Unisex'),
    ]

    name = models.CharField(max_length=100)  # Renamed from title for clarity
    description = models.TextField(blank=True, null=True)
    target_audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='UNISEX', db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TOP', db_index=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    sizes_available = models.CharField(max_length=100, help_text="e.g., S, M, L, XL or 30, 32, 34", blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    
    image_2d = models.ImageField(upload_to='clothing_images/2d/', help_text="2D image for display in lists/galleries")
    model_3d_file = models.FileField(upload_to='clothing_models/3d/', blank=True, null=True, help_text="3D model file (e.g., .glb, .obj)")
    texture_file = models.FileField(upload_to='clothing_models/textures/', blank=True, null=True, help_text="Texture file for the 3D model, if separate")

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def image_2d_base64(self):
        if not self.image_2d:
            return None
        with self.image_2d.open("rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
