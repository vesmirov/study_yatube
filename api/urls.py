from django.urls import path
from rest_framework.authtoken import views as apiviews

from . import views


urlpatterns = [
    path('v1/api-token-auth/', apiviews.obtain_auth_token),
]
