# wms_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]