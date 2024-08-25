# wms_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, MaskViewSet

router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'masks', MaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]