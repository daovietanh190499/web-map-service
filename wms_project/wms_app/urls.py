# wms_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, PredictAreaViewSet
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet, "image")
router.register(r'predict-area', PredictAreaViewSet, "predict-area")

urlpatterns = [
    path('', include(router.urls)),
]