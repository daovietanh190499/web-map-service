# wms_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, PredictAreaViewSet, BaseMapViewSet, ArcGISConfigViewSet, TopicViewSet
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet, "image")
router.register(r'predict-area', PredictAreaViewSet, "predict-area")
router.register(r'basemaps', BaseMapViewSet, "basemap")
router.register(r'arcgis-config', ArcGISConfigViewSet, "arcgis-config")
router.register(r'topics', TopicViewSet, "topic")

urlpatterns = [
    path('', include(router.urls)),
]