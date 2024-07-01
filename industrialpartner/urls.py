from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('manufacturer_prod/<int:manufacturer_id>/', manufacturer_prod, name='manufacturer_prod'),
    path('product/<int:item_id>/', product, name='product'),
    path('all_product', all_product, name='all_product'),
    path('add_to_cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('quote_request', quote_request, name='quote_request'),
    path('quote_request_cart', quote_request_cart, name='quote_request_cart'),
    path('search/', search_items, name='search_items'),
    path('cart', cart, name='cart'),
    path('contact', contact, name='contact'),
    path('about', about, name='about'),
    path('ser_rqst', ser_rqst, name='ser_rqst'),
    path('success', success, name='success'),
    path('cart/count/', cart_count, name='cart_count'),
    #path('<str:manufacturer>/', manufacturer_prod_page, name='manufacturer_prod_page'),
    path('filtered', filter_view, name='filter_view'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)