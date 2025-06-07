from django.contrib import admin
from .models import UserProfile, ClothingItem

# Basic registration for UserProfile (can be enhanced similarly if needed)
admin.site.register(UserProfile)

# Custom Admin for ClothingItem
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_audience', 'category', 'brand', 'price', 'is_available', 'created_at', 'updated_at')
    list_filter = ('target_audience', 'category', 'brand', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'brand', 'category', 'target_audience')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'target_audience', 'category', 'brand')
        }),
        ('Media Files', {
            'fields': ('image_2d', 'model_3d_file', 'texture_file')
        }),
        ('Details & Availability', {
            'fields': ('color', 'sizes_available', 'material', 'price', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Make this section collapsible
        }),
    )

# Unregister the basic registration if it was already done (to avoid errors)
# and register with the custom admin class.
# If ClothingItem was already registered, this will replace it.
# If not, it will simply register it.
# A more robust way is to check if it's registered first, but for simplicity:
try:
    admin.site.unregister(ClothingItem)
except admin.sites.NotRegistered:
    pass
admin.site.register(ClothingItem, ClothingItemAdmin)
