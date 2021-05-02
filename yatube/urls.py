from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as flat_views
from rest_framework.authtoken import views as rest_views
from django.urls import include, path
from django.conf.urls import handler404, handler500

handler404 = "posts.views.page_not_found"  # noqa: F811
handler500 = "posts.views.server_error"  # noqa: F811


urlpatterns = [
    path("admin/", admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        'about-author/',
        flat_views.flatpage,
        {'url': '/about-author/'},
        name='about-author'
    ),
    path(
        'about-spec/',
        flat_views.flatpage,
        {'url': '/about-spec/'},
        name='about-spec'
    ),
    path(
        'api-token-auth/',
        rest_views.obtain_auth_token,
        name='obtain_token'
    )
]

urlpatterns += [
    path("", include("posts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
