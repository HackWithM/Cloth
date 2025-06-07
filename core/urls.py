from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
     path('profile/', views.profile_view, name='profile'),
    path('clothes/', views.all_clothes, name='all_clothes'), # General listing
    path('clothes/<slug:audience_slug>/', views.all_clothes, name='all_clothes_by_audience'), # Filtered by audience
    #path('clothes/men/', views.mens_clothing, name='mens_clothing'),
    path('mens/', views.mens_clothes, name='mens_clothes'),
    path('womens/', views.womens_clothes, name='womens_clothes'),
    path('kids/', views.kids_clothes, name='kids_clothes'),
    path('clothes/item/<int:item_id>/', views.clothing_detail, name='clothing_detail'), # Changed path slightly for clarity
    path('try-on/<int:item_id>/', views.try_on, name='try_on'), # This might be deprecated by model-viewer's AR features
    path('virtual-try-on-ai/<int:item_id>/', views.virtual_tryon_view, name='virtual_try_on_ai'),
]