from django.urls import path
from apps.corporate.views import *


urlpatterns = [
    path( "calculate_price/", CalculatePriceView.as_view(), name="calculate_price", ),
    path( "create_order/", CreateOrderView.as_view(), name="create_order", ), 
    path( "orders/", CorporateOrdersView.as_view(), name="orders", ),
    path( "order_details/<slug:slug>/", CorpPackageRetrieveEditDeleteView.as_view(), name="order_details", ),
]

