from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .forms import QuoteRequestForm, QuoteRequestFormCart, QuoteAddon, QuoteAddonInfo
from .models import Product
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views.decorators.cache import cache_page
from urllib.parse import urlparse, urlunparse, urlunsplit
from django.views.decorators.csrf import csrf_exempt
import re

def get_subdomain(request):
    """
    Extracts the subdomain from the request URL.

    Args:
        request (HttpRequest): The Django HttpRequest object.

    Returns:
        str: The subdomain if it exists, otherwise None.
    """
    full_url = request.build_absolute_uri()
    parsed_url = urlparse(full_url)
    netloc = parsed_url.netloc
    parts = netloc.split('.')
    subdomain = parts[0] if parts and len(parts) > 1 else None
    return subdomain

#Handling 404 Page
def custom_404(request, exception):
    subdomain = get_subdomain(request)

    manufacturer = subdomain
    context = {
        'manufacturer': manufacturer,
    }
    return render(request, 'industrialpartner/404.html', context, status=404)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def get_paginated_data(api_endpoint, page, additional_params=None):
    if additional_params:
        api_endpoint += additional_params
    return fetch_data(f"{api_endpoint}&page={page}")

def is_ip_address(netloc):
    # Regular expression to check if the netloc is an IP address
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    return ip_pattern.match(netloc) is not None

@cache_page(60 * 15)  # Cache the view for 15 minutes
def home(request):
    full_url = request.build_absolute_uri()
    parsed_url = urlparse(full_url)
    netloc = parsed_url.netloc
    parts = netloc.split('.')
    subdomain = parts[0] if parts and len(parts) > 1 and not is_ip_address(netloc) else None

    page_number = request.GET.get('page', 1)
    part_number = request.GET.get('part_number', '')
    brand_name = request.GET.get('brand_name', '')

    if subdomain:
        manufacturer = subdomain.upper()
        additional_params = f"&part_number={part_number}" if part_number else ""
        data = get_paginated_data(f"http://174.46.4.71/items?manufacturer_lookup={manufacturer}", page_number, additional_params)

        if not data.get('items'):
            data = fetch_data(f"http://174.46.4.71/manufacturer?brand_name={brand_name}&page={page_number}")
            return render_index_page(request, data, brand_name, page_number)
        else:
            return render_manufacturer_page(request, data, manufacturer, page_number, part_number)
    else:
        data = fetch_data(f"http://174.46.4.71/manufacturer?brand_name={brand_name}&page={page_number}")
        return render_index_page(request, data, brand_name, page_number)

def render_index_page(request, data, brand_name, page_number):
    items = data.get('items', [])
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    paginator = Paginator(items, page_size)
    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    products = Product.objects.all()

    context = {
        'manufacturers': current_page,
        'total_pages': total_pages,
        'current_page': int(page_number),
        'brand_name': brand_name,
        'products': products,
    }

    return render(request, 'industrialpartner/index.html', context)

def render_manufacturer_page(request, data, manufacturer, page_number, part_number):
    items = data.get('items', [])
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    paginator = Paginator(items, page_size)
    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    manufacturer_info = items[0]['Manufacturer']['Synopsis'] if items else ""
    first_six_items = items[:6]
    remaining_items = items[6:]

    context = {
        'manufacturer': manufacturer,
        'manufacturer_id': items[0]['Manufacturer']['ManufacturerID'] if items else '',
        'manufacturer_info': manufacturer_info,
        'first_six_items': first_six_items,
        'remaining_items': remaining_items,
        'manufacturer_name': items[0]['Manufacturer']['Manufacturer'] if items else '',
        'total_pages': total_pages,
        'current_page': int(page_number),
        'part_number': part_number,
    }

    return render(request, 'industrialpartner/manufacture-product-2.html', context)

#================For the url manufacturer pages not in use===============
def fetch_paginated_data_manufacturer_page(manufacturer, page, part_number=None):
    api_endpoint = f"http://174.46.4.71/items?manufacturer={manufacturer}&page={page}"
    #if part_number of the particular manufacture is queried
    if part_number:
        api_endpoint += f"&part_number={part_number}"

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

    return render(request, 'industrialpartner/manufacture-product-2.html', context)
#========================================================================


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
    full_url = request.build_absolute_uri()
    parsed_url = urlparse(full_url)
    # Extract the current netloc (host and port)
    current_netloc = parsed_url.netloc
   
    # Get the current page number from the request, default to 1 if not provided
    page_number = request.GET.get('page', 1)
    part_number = request.GET.get('part_number', '')

    # Fetch data from the API
    data = fetch_paginated_data_items(manufacturer_id, page_number, part_number)

    items = data.get('items', [])
    total_items = data.get('total', 0)
    page_size = data.get('size', 50)
    total_pages = data.get('pages', 1)

    #print(items)
    
    paginator = Paginator(items, page_size)

    try:
        current_page = paginator.page(page_number)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    manufacturer_name = items[0]['Manufacturer']['Manufacturer'] if items else ""
    manufacturer=items[0]['Manufacturer']['Lookup'] if items else ""
    manufacturer_info = items[0]['Manufacturer']['Synopsis'] if items else ""
    # Split items into first_six_items and remaining_items
    first_six_items = items[:6]
    remaining_items = items[6:]

    # Determine the new host
    if manufacturer and not current_netloc.startswith(f"{manufacturer}."):
        new_host = f"{manufacturer}.{current_netloc}"
    else:
        new_host = current_netloc

    # Reconstruct the new URL with the modified host
    new_url = urlunparse((
        parsed_url.scheme,
        new_host,
        '/',  # Redirect to the root path of the new subdomain
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    
    context = {
        'manufacturer_info':manufacturer_info,
        'manufacturer_id': manufacturer_id,
        'first_six_items': first_six_items,
        'remaining_items': remaining_items,
        'manufacturer_name': manufacturer_name,
        'manufacturer': manufacturer,
        'total_pages': total_pages,
        'current_page': int(page_number),
        'part_number': part_number,
    }
    # Redirect to the new URL
    return HttpResponseRedirect(new_url)
    #return render(request, 'industrialpartner/manufacture-product-2.html', context)


@cache_page(60 * 30)  # Cache the view for 30 minutes
def product(request, item_id, slug):
    api_endpoint = f"http://174.46.4.71/items/{item_id}"
    
    try:
        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        # Convert the response to JSON format
        item_data = response.json()

        product_url = request.build_absolute_uri()

        Feature_List = [feature['Feature'] for feature in item_data['Features']]
        Intro = item_data['Introductions'][0]['Introduction'] if item_data and item_data['Introductions'] else ""
        manufacturer_info = item_data['Manufacturer']['Synopsis'] if item_data else "N/A"
        manufacturer_id = item_data['Manufacturer']['ManufacturerID']
        manufacturer = item_data['Manufacturer']['Manufacturer']
        simpletype = item_data['SimpleTypes'][0]['SimpleType']

        #For Related Product
        data = fetch_paginated_data_items(manufacturer_id, page=1)
        items = data.get('items', [])

        first_three_items = items[:3]

        # Check if the provided slug matches the slug from the API
        if slug != item_data.get('Slug'):
            return HttpResponse("Invalid slug", status=404)

        # Pass the item data to the template
        context = {
            'item_data': item_data,
            'Feature_List': Feature_List,
            'Intro': Intro,
            'manufacturer_info': manufacturer_info,
            'manufacturer_id': manufacturer_id,
            'manufacturer': manufacturer,
            'first_three_items': first_three_items,
            'simpletype':simpletype,
            'product_url':product_url,
        }

        # Render the template with the item data
        return render(request, 'industrialpartner/product-page-2.html', context)

    except requests.RequestException as e:
        # Handle any errors that occur during the request
        error_message = f"Failed to fetch data from API: {str(e)}"
        return HttpResponse(error_message, status=response.status_code)


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

    return render(request, 'industrialpartner/main-2.html', context)

@csrf_exempt
def success(request, quote_id):

    quote_id = request.session.get('quote_id')

    if request.method == 'POST':
        form = QuoteAddon(request.POST)
        form_info = QuoteAddonInfo(request.POST)

        if form.is_valid() and form_info.is_valid:
            data = {
                "QuoteID": form.cleaned_data['quote_id'],
                "Address1": form.cleaned_data['address1'],
                "Address2": form.cleaned_data['address2'],
                "City": form.cleaned_data['city'],
                "StateProv": form.cleaned_data['stateprov'],
                "ZIPPostalCode": form.cleaned_data['zip'],
                "CountryID": form.cleaned_data['country'],
                "CustomerTypeID": form.cleaned_data['industry'],
                "Comments": form.cleaned_data['comments'],
                "QuotePurposeID": form.cleaned_data['purpose']
            }

            api_endpoint = f"http://174.46.4.71/quotes/addon/{quote_id}"
            try:
                response = requests.post(api_endpoint, json=data)
                response.raise_for_status()
                response_data = response.json()  # Parse the JSON response

                messages.success(request, 'Thank You for your Submission!')
                return redirect('success', quote_id=quote_id)
            
            except requests.RequestException as e:
                error_message = f"Failed to send quote request: {str(e)}"
                return HttpResponse(error_message, status=response.status_code)  
    else:
        form = QuoteAddon()


    if request.method == 'POST':
        form_info = QuoteAddonInfo(request.POST)
        if form_info.is_valid():
            data_info = {
                "QuoteID": form_info.cleaned_data['quote_id'],
                "QuotingTime": form_info.cleaned_data['response'],
                "EquipmentConditionID": form_info.cleaned_data['condition']
            }
            api_endpoint_info = f"http://174.46.4.71/quotes/request-info/{quote_id}"
            try:
                response_info = requests.post(api_endpoint_info, json=data_info)
                response_info.raise_for_status()
            except requests.RequestException as e:
                error_message = f"Failed to send quote request: {str(e)}"
                return HttpResponse(error_message, status=response.status_code)        
    else:
        form_info = QuoteAddonInfo()


    context = {
        'quote_id': quote_id,
        'form': form,
        'form_info':form_info
    }
    return render(request, 'industrialpartner/success-page.html', context)


@csrf_exempt
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
                response_data = response.json()  # Parse the JSON response

                # Extract the QuoteID from the response data
                quote_id = response_data.get('QuoteID')

                # Store the quote_id in the session
                request.session['quote_id'] = quote_id

                ip = get_client_ip(request)

                data_info = {
                        "QuoteID": quote_id,
                        "IPAddress": ip,
                        "Source": 'www.industrialpartner.com',
                        "IsFirstRFQ": 0
                    }
                api_endpoint_info = f"http://174.46.4.71/quotes/request-info/{quote_id}"
                try:
                    response_info = requests.post(api_endpoint_info, json=data_info)
                    response_info.raise_for_status()
                except requests.RequestException as e:
                    return HttpResponse( status=response.status_code)
            
                # Use Django messages to pass the success quote request
                #message = 'Your Quote Request has been Submitted.<br>We would get back with you shortly'
                #messages.add_message(request, messages.SUCCESS, mark_safe(message), extra_tags='quote_request')

                # Redirect back to the referring page
                #referer = request.META.get('HTTP_REFERER', '/')
                return redirect('success', quote_id=quote_id)
            
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

    return render(request, 'industrialpartner/main-2.html', {'items': items})


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

@csrf_exempt
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

    return render(request, 'industrialpartner/main-2.html', context)



#SITEMAP LOGIC

def fetch_item_data_page(manufacturer, page):
    api_endpoint = f"http://174.46.4.71/items?manufacturer_lookup={manufacturer}&page={page}"
    #if part_number of the particular manufacture is queried
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    return {}

#@cache_page(60 * 15)  # Cache the view for 15 minutes
def sitemap_products(request, manufacturer):
    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        page = int(request.GET.get('page', 1))  # Ensure page is an integer
        data = fetch_item_data_page(manufacturer, page)
        items = data.get('items', [])
        return JsonResponse({'items': items})

    # Initial page load (for non-AJAX requests)
    data = fetch_item_data_page(manufacturer, 1)  # Fetch data for page 1
    items = data.get('items', [])
    manufacturer_name = items[0]['Manufacturer']['Manufacturer'] if items else ""

    context = {
        'manufacturer': manufacturer,
        'items': items,
        'manufacturer_name': manufacturer_name,
    }

    return render(request, 'industrialpartner/sitemap-2.html', context)