from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthFacilityViewSet

router = DefaultRouter()
router.register(r'facilities', HealthFacilityViewSet, basename='facility')

urlpatterns = [
    path('', include(router.urls)),
]
