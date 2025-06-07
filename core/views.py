import json
import base64
import io
import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import ClothingItem
import os
import mimetypes

def home(request):
    featured_items = ClothingItem.objects.filter(is_available=True).order_by('-created_at')[:4]
    new_arrivals = ClothingItem.objects.filter(is_available=True).order_by('-created_at')[:8]

    mens_items = ClothingItem.objects.filter(target_audience='MEN', is_available=True)[:4]
    womens_items = ClothingItem.objects.filter(target_audience='WOMEN', is_available=True)[:4]
    kids_items = ClothingItem.objects.filter(target_audience='KIDS', is_available=True)[:4]

    best_sellers = ClothingItem.objects.filter(is_available=True).order_by('name')[:4]

    context = {
        'featured_items': featured_items,
        'new_arrivals': new_arrivals,
        'mens_items': mens_items,
        'womens_items': womens_items,
        'kids_items': kids_items,
        'best_sellers': best_sellers,
    }
    return render(request, 'home.html', context)

def all_clothes(request, audience_slug=None):
    clothes = ClothingItem.objects.filter(is_available=True)
    page_title = "All Clothing"

    if audience_slug:
        if audience_slug.upper() in [choice[0] for choice in ClothingItem.AUDIENCE_CHOICES]:
            clothes = clothes.filter(target_audience=audience_slug.upper())
            page_title = dict(ClothingItem.AUDIENCE_CHOICES).get(audience_slug.upper(), f"{audience_slug.capitalize()}'s Clothing")
        else:
            page_title = f"Clothing for {audience_slug.capitalize()}"

    context = {
        'clothes': clothes.order_by('-created_at'),
        'page_title': page_title,
        'audience_slug': audience_slug
    }
    return render(request, 'all_clothes.html', context)

def mens_clothes(request):
    clothes = ClothingItem.objects.filter(target_audience='MEN', is_available=True)
    return render(request, 'mens_clothes.html', {'clothes': clothes, 'page_title': "Men's Collection"})

def womens_clothes(request):
    clothes = ClothingItem.objects.filter(target_audience='WOMEN', is_available=True)
    return render(request, 'womens_clothes.html', {'clothes': clothes, 'page_title': "Women's Collection"})

def kids_clothes(request):
    clothes = ClothingItem.objects.filter(target_audience='KIDS', is_available=True)
    return render(request, 'kids_clothes.html', {'clothes': clothes, 'page_title': "Kids' Collection"})

def clothing_detail(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    return render(request, 'clothing_detail.html', {'item': item})

def try_on(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    return render(request, 'try_on.html', {'item': item})

def profile_view(request):
    return render(request, 'profile.html')



@csrf_exempt
def virtual_tryon_view(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    if request.method == 'POST':
        try:
            person_img = None
            person_image_content_type = None

            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_image_data_url = data.get('user_image_data_url')
                if not user_image_data_url:
                    return JsonResponse({'success': False, 'message': 'User image data URL not provided.'}, status=400)
                
                # Decode base64 data URL
                try:
                    # Format: "data:image/jpeg;base64,LzlqLzRBQ...
                    img_format, img_str = user_image_data_url.split(';base64,')
                    ext = img_format.split('/')[-1] # e.g., jpeg, png
                    person_image_content_type = f"image/{ext}"
                    decoded_file = base64.b64decode(img_str)
                    person_img = ContentFile(decoded_file, name=f"uploaded_person_image.{ext}")
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Invalid image data URL format: {str(e)}'}, status=400)
            else: # Fallback to form data if not JSON
                person_img = request.FILES.get('person_image')
                if person_img:
                    person_image_content_type = person_img.content_type

            if not person_img:
                # This condition should now primarily be for non-JSON requests if they reach here without an image
                # For JSON requests, the check is handled above.
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                    return JsonResponse({'success': False, 'message': 'Please upload your image.'}, status=400)
                return render(request, 'upload.html', {'error_message': 'Please upload your image.', 'item': item})

            if not item.image_2d or not item.image_2d.name:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                    return JsonResponse({'success': False, 'message': 'The selected clothing item does not have an image for try-on.'}, status=400)
                return render(request, 'upload.html', {'error_message': 'The selected clothing item does not have an image for try-on.', 'item': item})

            api_url = 'http://127.0.0.1:8001/tryon/'  # FastAPI URL

            person_img.seek(0) # Ensure reading from start
            person_image_data = (person_img.name, person_img.read(), person_image_content_type or 'application/octet-stream')

            cloth_content_type, _ = mimetypes.guess_type(item.image_2d.name)
            if not cloth_content_type:
                cloth_content_type = 'application/octet-stream' # Fallback

            with item.image_2d.open('rb') as cloth_file_rb:
                cloth_image_data = (os.path.basename(item.image_2d.name), cloth_file_rb.read(), cloth_content_type)

            files = {
                'person_img': person_image_data, # Changed key
                'cloth_img': cloth_image_data   # Changed key
            }

            response = requests.post(api_url, files=files, timeout=180) # Increased timeout
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            # If we reach here, the request was successful (status 2xx)
            output_dir = os.path.join(settings.MEDIA_ROOT, 'virtual_tryon_outputs')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'output.jpg')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            output_url = os.path.join(settings.MEDIA_URL, 'virtual_tryon_outputs', 'output.jpg')
            # Always return JSON for AJAX/JSON requests, otherwise render HTML
            is_json_request = request.content_type == 'application/json' or \
                              request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
                              'application/json' in request.META.get('HTTP_ACCEPT', '')

            if is_json_request:
                return JsonResponse({'success': True, 'processed_image_url': output_url, 'message': 'Image processed successfully!'})
            return render(request, 'result.html', {'output_img': output_url})

        except requests.exceptions.ConnectionError:
            error_message = "The AI Try-On service is currently unavailable. Please ensure it is running and accessible at http://127.0.0.1:8001/tryon/."
            if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({'success': False, 'message': error_message}, status=503) # Service Unavailable
            return render(request, 'upload.html', {'error_message': error_message, 'item': item})
        except requests.exceptions.Timeout:
            error_message = "The request to the AI Try-On service timed out. The service might be too busy or unresponsive."
            if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({'success': False, 'message': error_message}, status=504) # Gateway Timeout
            return render(request, 'upload.html', {'error_message': error_message, 'item': item})
        except requests.exceptions.HTTPError as e:
            error_message = f"The AI Try-On service returned an error: {e.response.status_code}. Details: {e.response.text}"
            if e.response.status_code == 500:
                error_message += " This might indicate an issue within the AI service itself."
            elif e.response.status_code == 422: # Unprocessable Entity, common for FastAPI validation errors
                 error_message += " This might be due to invalid input data sent to the AI service."
            elif e.response.status_code == 405: # Method Not Allowed
                 error_message += " The AI service reports that the POST method is not allowed on its /tryon/ URL. This is unexpected for a file upload service and likely indicates a configuration issue with the AI service itself."
            if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({'success': False, 'message': error_message, 'status_code': e.response.status_code if hasattr(e, 'response') else 500}, status=e.response.status_code if hasattr(e, 'response') else 500)
            return render(request, 'upload.html', {'error_message': error_message, 'item': item})
        except requests.exceptions.RequestException as e: # Catch other request-related errors
            error_message = f"A network or request-related error occurred: {str(e)}"
            if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({'success': False, 'message': error_message}, status=500)
            return render(request, 'upload.html', {'error_message': error_message, 'item': item})
        except Exception as e: # Generic fallback, should be after more specific ones
            error_message = f"An unexpected error occurred while processing your request: {str(e)}"
            # Ensure any exception for a JSON request path returns JSON
            if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return JsonResponse({'success': False, 'message': error_message}, status=500)
            return render(request, 'upload.html', {'error_message': error_message, 'item': item})

    # For GET requests or if POST is not application/json and doesn't fit other criteria
    return render(request, 'upload.html', {'item': item})
