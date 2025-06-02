from django.urls import path
from apps.logistics.views import *


urlpatterns = [
    path( "routes/", AllRoutesView.as_view(), name="routes", ),
    path( "create_order/", CreateOrderView.as_view(), name="create_order"),
    path( "my_orders/", MyOrdersView.as_view(), name="my_orders", ),
    path( "order_details/<str:pk>/", OrderDetailsView.as_view(), name="order_details", ),
    path( "update_order_details/<str:pk>/", UpdateDetailsView.as_view(), name="update_order_details", ),
]


