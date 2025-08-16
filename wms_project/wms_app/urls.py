# wms_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, PredictAreaViewSet, BaseMapViewSet, ArcGISConfigViewSet, TopicViewSet
from . import views
from .auth import LoginView, LogoutView, UserInfoView, RegisterView, login_view, logout_view, user_info_view, register_view

router = DefaultRouter()
router.register(r'images', ImageViewSet, "image")
router.register(r'predict-area', PredictAreaViewSet, "predict-area")
router.register(r'basemaps', BaseMapViewSet, "basemap")
router.register(r'arcgis-config', ArcGISConfigViewSet, "arcgis-config")
router.register(r'topics', TopicViewSet, "topic")

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication URLs
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/user/', UserInfoView.as_view(), name='api_user_info'),
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    
    # Function-based auth views for compatibility
    path('auth/login-func/', login_view, name='login_func'),
    path('auth/logout-func/', logout_view, name='logout_func'),
    path('auth/user-func/', user_info_view, name='user_info_func'),
    path('auth/register-func/', register_view, name='register_func'),
]