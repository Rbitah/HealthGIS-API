from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShapefileLayerViewSet
from .authentication import login_view, logout_view, current_user_view, refresh_token_view

router = DefaultRouter()
router.register(r'shapefiles', ShapefileLayerViewSet, basename='shapefile')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', current_user_view, name='current-user'),
    path('auth/refresh/', refresh_token_view, name='refresh-token'),
    
    # Shapefile CRUD endpoints
    path('', include(router.urls)),
]
