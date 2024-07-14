from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from django.http import HttpResponse, JsonResponse
from .forms import QuoteRequestForm, QuoteRequestFormCart
from .models import Product
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views.decorators.cache import cache_page

#Handling 404 Page
def custom_404(request, exception):
    return render(request, 'industrialpartner/404.html', status=404)

def fetch_paginated_data(brand_name, page):
    response = requests.get(f"http://174.46.4.71/manufacturer?brand_name={brand_name}&page={page}")
    if response.status_code == 200:
        return response.json()
    return {}

def home(request):
    brand_name = request.GET.get('brand_name', 'A')  # Default to 'A' if not specified
    page_number = request.GET.get('page', 1)
        
    data = fetch_paginated_data(brand_name, page_number)
    
    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    
    paginator = Paginator(items, page_size)

    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    # Modify the manufacturer objects to include attributes for each brand name
    for manufacturer in current_page.object_list:
        manufacturer_attributes = {}
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            attribute_name = f'Manufacturer_{letter}'
            if attribute_name in manufacturer:
                manufacturer_attributes[attribute_name] = manufacturer[attribute_name]
        manufacturer.update(manufacturer_attributes)

    #Getting Featured Product from app home db
    # Fetch all Product objects from the database
    products = Product.objects.all()

    context = {
        'manufacturers': current_page,
        'total_pages': total_pages,
        'current_page': int(page_number),
        'brand_name': brand_name,
        'products': products,
    }

    return render(request, 'industrialpartner/index.html', context)


#For the url manufacturer pages
def fetch_paginated_data_manufacturer_page(manufacturer, page):
    api_endpoint = f"http://174.46.4.71/items?manufacturer={manufacturer}&page={page}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    return {}

def manufacturer_prod_page(request, manufacturer):
    page_number = request.GET.get('page', 1)
    data = fetch_paginated_data_manufacturer_page(manufacturer, page_number)
    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    paginator = Paginator(items, page_size)
    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    manufacturer_name = manufacturer
    first_six_items = items[:6]
    remaining_items = items[6:]

    context = {
        'manufacturer': manufacturer,
        'first_six_items': first_six_items,
        'remaining_items': remaining_items,
        'manufacturer_name': manufacturer_name,
        'total_pages': total_pages,
        'current_page': int(page_number),
    }

    return render(request, 'industrialpartner/manufacture-product.html', context)


def fetch_paginated_data_items(manufacturer_id, page, part_number=None):
    api_endpoint = f"http://174.46.4.71/items?manufacturer_id={manufacturer_id}&page={page}"
    #if part_number of the particular manufacture is queried
    if part_number:
        api_endpoint += f"&part_number={part_number}"
        
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    return {}

def manufacturer_prod(request, manufacturer_id):
    # Get the current page number from the request, default to 1 if not provided
    page_number = request.GET.get('page', 1)
    part_number = request.GET.get('part_number', '')

    # Fetch data from the API
    data = fetch_paginated_data_items(manufacturer_id, page_number, part_number)

    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    paginator = Paginator(items, page_size)

    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    manufacturer_name = items[0]['Manufacturer']['Manufacturer'] if items else "Unknown Manufacturer"
    manufacturer_info = items[0]['Manufacturer']['Synopsis'] if items else ""
    # Split items into first_six_items and remaining_items
    first_six_items = items[:6]
    remaining_items = items[6:]

    context = {
        'manufacturer_info':manufacturer_info,
        'manufacturer_id': manufacturer_id,
        'first_six_items': first_six_items,
        'remaining_items': remaining_items,
        'manufacturer_name': manufacturer_name,
        'total_pages': total_pages,
        'current_page': int(page_number),
        'part_number': part_number,
    }

    return render(request, 'industrialpartner/manufacture-product.html', context)



def product(request, item_id, slug):
    api_endpoint = f"http://174.46.4.71/items/{item_id}"
    
    try:
        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        # Convert the response to JSON format
        item_data = response.json()

        # Check if the provided slug matches the slug from the API
        if slug != item_data.get('Slug'):
            return HttpResponse("Invalid slug", status=404)

        # Pass the item data to the template
        context = {
            'item_data': item_data
        }

        # Render the template with the item data
        return render(request, 'industrialpartner/product-page.html', context)

    except requests.RequestException as e:
        # Handle any errors that occur during the request
        error_message = f"Failed to fetch data from API: {str(e)}"
        return HttpResponse(error_message, status=response.status_code)


def all_product(request):
    return render(request, 'industrialpartner/main.html')

def fetch_paginated_data_all_items(page):
    api_endpoint = f"http://174.46.4.71/items?page={page}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    return {}


def all_product(request):
    # Get the current page number from the request, default to 1 if not provided
    page_number = request.GET.get('page', 1)

    # Fetch data from the API
    data = fetch_paginated_data_all_items(page_number)

    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    paginator = Paginator(items, page_size)

    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    context = {
        'items': current_page,
        'total_pages': total_pages,
        'current_page': int(page_number),
    }

    return render(request, 'industrialpartner/main.html', context)

def quote_request(request):

    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            data = {
                "Notes": form.cleaned_data['notes'],
                "Comments": form.cleaned_data['comments'],
                "FirstName": form.cleaned_data['first_name'],
                "LastName": form.cleaned_data['last_name'],
                "Company": form.cleaned_data['company'],
                "Phone": form.cleaned_data['phone'],
                "Email": form.cleaned_data['email'],
                "LineItems": [
                    {
                        "ItemID": form.cleaned_data['item_id'],
                        "Qty": form.cleaned_data['quantity']
                    }
                ]
            }

            api_endpoint = "http://174.46.4.71/quotes"
            try:
                response = requests.post(api_endpoint, json=data)
                response.raise_for_status()
                # Use Django messages to pass the success quote request
                message = 'Your Quote Request has been Submitted.<br>We would get back with you shortly'
                messages.add_message(request, messages.SUCCESS, mark_safe(message), extra_tags='quote_request')

                #messages.success(request, f'Your Quote Request has been Submitted.\nWe would get back with you shortly')

                # Redirect back to the referring page
                #referer = request.META.get('HTTP_REFERER', '/')
                return redirect('success')
            
            except requests.RequestException as e:
                error_message = f"Failed to send quote request: {str(e)}"
                return HttpResponse(error_message, status=response.status_code)
    else:
        form = QuoteRequestForm()

    return render(request, 'industrialpartner/product-page.html', {'form': form})


def search_items(request):
    part_number = request.GET.get('part_number', '')

    if part_number:
        api_endpoint = f"http://174.46.4.71/items?part_number={part_number}"
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            items = response.json().get('items', [])
        except requests.RequestException as e:
            return HttpResponse(f"Failed to fetch data from API: {str(e)}", status=response.status_code)
    else:
        items = []

    return render(request, 'industrialpartner/main.html', {'items': items})


def fetch_product_details_from_api(item_id):
    # Function to fetch product details from the API based on item_id
    api_endpoint = f"http://174.46.4.71/items/{item_id}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    return None


def add_to_cart(request, item_id):
    # Fetch product details from the API using the fetch_product_details_from_api function
    product_details = fetch_product_details_from_api(item_id)

    if product_details:
        # Retrieve the cart from the session
        cart = request.session.get('cart', {})

        # Add the item to the cart or increment its quantity if it's already there
        if item_id in cart:
            cart[item_id]['quantity'] += 1
        else:
            cart[item_id] = {
                'PartNumber': product_details.get('PartNumber', 'N/A'),
                'Description': product_details.get('Description', 'N/A'),
                'quantity': 1
            }

        # Save the updated cart back to the session
        request.session['cart'] = cart

    # Calculate total cart count
    cart_count = calculate_cart_count(cart)

    # Use Django messages to pass the updated cart count
    message = f'Cart updated.<br> Change quantity of item in Shopping Cart'
    messages.add_message(request, messages.SUCCESS, mark_safe(message), extra_tags='add_cart')


    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def cart(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'cart_count': cart_count,
    }
    return render(request, 'industrialpartner/cart.html', {'cart': cart})

def calculate_cart_count(cart):
    total_count = 0
    for item_id, item_data in cart.items():
        total_count += item_data['quantity']
    return total_count

def cart_count(request):
    cart = request.session.get('cart', {})
    cart_count = calculate_cart_count(cart)
    return JsonResponse({'cart_count': cart_count})

def remove_from_cart(request, item_id):
    # Convert item_id to string to match the key in the session dictionary
    item_id = str(item_id)
    
    # Retrieve the cart from the session
    cart = request.session.get('cart', {})

    # Remove the item if it exists in the cart
    if item_id in cart:
        del cart[item_id]
        request.session['cart'] = cart

    # Redirect back to the cart page
    return redirect('cart')


def contact(request):
    return render(request, 'industrialpartner/contact.html')

def about(request):
    return render(request, 'industrialpartner/about.html')

def ser_rqst(request):
    return render(request, 'industrialpartner/service-request.html')


def success(request):
    return render(request, 'industrialpartner/success-page.html')

def quote_request_cart(request):
    if request.method == 'POST':
        form = QuoteRequestFormCart(request.POST)
        if form.is_valid():
            line_items = []
            for key in request.POST:
                if key.startswith('item_id_'):
                    index = key.split('_')[2]
                    item_id = request.POST.get(f'item_id_{index}')
                    quantity = request.POST.get(f'quantity_{index}')
                    line_items.append({
                        "ItemID": item_id,
                        "Qty": quantity
                    })

            data = {
                "Notes": form.cleaned_data['notes'],
                "Comments": form.cleaned_data['comments'],
                "FirstName": form.cleaned_data['first_name'],
                "LastName": form.cleaned_data['last_name'],
                "Company": form.cleaned_data['company'],
                "Phone": form.cleaned_data['phone'],
                "Email": form.cleaned_data['email'],
                "LineItems": line_items
            }

            # Print the data for debugging purposes
            #print("Data to be sent to the API:")
            #print(data)

            # Temporarily comment out the API request for debugging
            api_endpoint = "http://174.46.4.71/quotes"
            try:
                response = requests.post(api_endpoint, json=data)
                response.raise_for_status()

                # Clear cart session after successful quote request
                request.session['cart'] = {}

                 # Use Django messages to pass the updated cart count
                messages.success(request, f'Your Quote Request has been Submitted.\nWe would get back with you shortly')


                return redirect('success')
            except requests.RequestException as e:
                error_message = f"Failed to send quote request: {str(e)}"
                return HttpResponse(error_message, status=response.status_code)
            #return HttpResponse("Data printed to console. Check the server logs.", status=200)
    else:
        form = QuoteRequestForm()

    return redirect('cart', {'form': form})


def fetch_items_by_manufacture_simpletype(manufacturer, simpletype, page):
    api_endpoint = f"http://174.46.4.71/items"
    params = {
        'manufacturer': manufacturer,
        'simpletype': simpletype,
        'page': page
    }
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

def filter_view(request):
    manufacturer = request.GET.get('manufacturer', '')  # Get manufacturer parameter from query string
    simpletype = request.GET.get('simpletype', '')  # Get simpletype parameter from query string
    page_number = request.GET.get('page', 1)  # Get page number from query string

    # Fetch items based on manufacturer and simpletype
    data = fetch_items_by_manufacture_simpletype(manufacturer, simpletype, page_number)

    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    context = {
        'items': items,
        'total_pages': total_pages,
        'current_page': int(page_number),
        'selected_manufacturer': manufacturer,  # Pass selected manufacturer to template
        'selected_simpletype': simpletype  # Pass selected simpletype to template
    }

    return render(request, 'industrialpartner/main.html', context)



#SITEMAP LOGIC
def fetch_all_data_load(brand_name, page):
    response = requests.get(f"http://174.46.4.71/manufacturer?brand_name={brand_name}&page={page}")
    if response.status_code == 200:
        data = response.json()
        return data
    return {'items': [], 'pages': 0}

def sitemap_data_load(request):
    brand_name = request.GET.get('brand_name', '')
    page = int(request.GET.get('page', 1))
    
    data = fetch_all_data_load(brand_name, page)
    items = data.get('items', [])
    for manufacturer in items:
        manufacturer_attributes = {}
        manufacturer_name = manufacturer.get('ManufacturerStandardized', '')
        if manufacturer_name:
            first_letter = manufacturer_name[0].upper()
            attribute_name = f'Manufacturer_{first_letter}'
            manufacturer_attributes[attribute_name] = manufacturer_name
        manufacturer.update(manufacturer_attributes)

    return JsonResponse({'manufacturers': items, 'pages': data.get('pages', 0), 'current_page': page})

def sitemap_loading(request):
    brand_name = request.GET.get('brand_name', '')
    
    context = {
        'brand_name': brand_name,
    }
    
    return render(request, 'industrialpartner/sitemap_loading.html', context)


def fetch_all_data_main(brand_name):
    all_items = []
    page = 1
    
    while True:
        response = requests.get(f"http://174.46.4.71/manufacturer?brand_name={brand_name}&page={page}")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
            all_items.extend(items)
            total_pages = data.get('pages', 1)
            if page >= total_pages:
                break
            page += 1
        else:
            break
    
    return {
        'items': all_items
    }

@cache_page(60 * 30)  # Cache the view for 15 minutes
def sitemap(request):
    brand_name = request.GET.get('brand_name', '')  # Default to 'A' if not specified
        
    data = fetch_all_data_main(brand_name)
    
    items = data.get('items', [])
    # Modify the manufacturer objects to include attributes for each brand name
    for manufacturer in items:
        #print(manufacturer)  # Print the manufacturer object to debug
        manufacturer_attributes = {}
        manufacturer_name = manufacturer.get('ManufacturerStandardized', '')
        if manufacturer_name:
            first_letter = manufacturer_name[0].upper()
            attribute_name = f'Manufacturer_{first_letter}'
            manufacturer_attributes[attribute_name] = manufacturer_name
        manufacturer.update(manufacturer_attributes)


    context = {
        'manufacturers': items,  # Pass all items to the template
        'brand_name': brand_name,
    }
    return render(request, 'industrialpartner/sitemap.html', context)


def fetch_all_item_data(manufacturer_id):
    all_items = []
    page = 1

    while True:
        response = requests.get(f"http://174.46.4.71/items?manufacturer_id={manufacturer_id}&page={page}")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
            all_items.extend(items)
            total_pages = data.get('pages', 1)
            if page >= total_pages:
                break
            page += 1
        else:
            break
    
    return {
        'items': all_items
    }

@cache_page(60 * 15)  # Cache the view for 15 minutes
def sitemap_products(request, manufacturer_id):
    # Fetch data from the API
    data = fetch_all_item_data(manufacturer_id)

    items = data.get('items', [])
    manufacturer_name = items[0]['Manufacturer']['Manufacturer'] if items else ""

    context = {
        'manufacturer_id': manufacturer_id,
        'items': items,
        'manufacturer_name': manufacturer_name,
    }

    return render(request, 'industrialpartner/sitemap-2.html', context)