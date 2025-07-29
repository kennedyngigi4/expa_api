from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path( 'api/account/', include("apps.accounts.urls")),
    path( 'api/account/superadmin/', include("apps.accounts.superadmin.urls")),
    path( 'api/account/partnershop/', include("apps.accounts.partnershop.urls")),


    path( 'api/deliveries/', include("apps.deliveries.urls")),
    path( 'api/deliveries/superadmin/', include("apps.deliveries.superadmin.urls")),
    path( 'api/deliveries/manager/', include("apps.deliveries.manager.urls")),
    path( 'api/deliveries/partnershop/', include("apps.deliveries.partnershop.urls")),
    path( 'api/deliveries/drivers/', include("apps.deliveries.drivers.urls")),


    path( "api/messaging/", include("apps.messaging.urls")),
    path( "api/messaging/partnershop/", include("apps.messaging.partnershop.urls")),


    path( "api/payments/", include("apps.payments.urls")),
]


urlpatterns += static( settings.STATIC_URL, document_root=settings.STATIC_ROOT )
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
