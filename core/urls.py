from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = ""
admin.site.site_title = ""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include("apps.accounts.urls")),
    path("api/account/admin/", include("apps.accounts.superadmin.urls")),
    path("api/account/courier/", include("apps.accounts.courier.urls")),
    path('api/logistics/admin/', include("apps.logistics.superadmin.urls")),
    path('api/logistics/manager/', include("apps.logistics.manager.urls")),
    path("api/logistics/client/", include("apps.logistics.urls")),
    path("api/messaging/client/", include("apps.messaging.urls")),
    path("api/logistics/courier/", include("apps.logistics.courier.urls")),
    path("api/payments/", include("apps.payments.urls")),
]


urlpatterns += static( settings.STATIC_URL, document_root=settings.STATIC_ROOT )
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )

