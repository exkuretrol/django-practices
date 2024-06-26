"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db.utils import OperationalError
from django.urls import include, path
from django.views.generic import TemplateView

from prod.models import Prod

from .api import api

try:
    last_prod = Prod.objects.last()
except OperationalError:
    last_prod = None

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="home.html"),
        kwargs={
            "last_prod": last_prod,
            "header_title": "儀表板",
            "header_description": "歡迎使用本系統。",
        },
        name="home",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("prod.urls")),
    path("", include("order.urls")),
    path("", include("manufacturer.urls")),
    # reloader
    # path("__reload__/", include("django_browser_reload.urls")),
    # debug
    path("__debug__/", include("debug_toolbar.urls")),
    # ninja api
    path("api/", api.urls),
]

# performance profiling
# urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
