from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from .models import HealthFacility
from .serializers import (
    HealthFacilityListSerializer,
    HealthFacilityDetailSerializer,
    HealthFacilityGeoJSONSerializer,
    NearbyFacilitySerializer,
    DirectionsSerializer
)


class HealthFacilityPagination(PageNumberPagination):
    """Custom pagination for health facilities"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HealthFacilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for health facilities with comprehensive filtering options.
    
    Endpoints:
    - GET /api/facilities/ - List all facilities
    - GET /api/facilities/{id}/ - Get facility details
    - GET /api/facilities/nearby/ - Find nearby facilities
    - GET /api/facilities/geojson/ - Get facilities in GeoJSON format
    - GET /api/facilities/districts/ - Get list of districts
    - GET /api/facilities/amenities/ - Get list of amenity types
    - GET /api/facilities/directions/ - Get directions to a facility
    
    Query Parameters:
    - name: Filter by facility name (case-insensitive partial match)
    - district: Filter by district name (case-insensitive)
    - region: Filter by region name
    - amenity: Filter by amenity type (clinic, hospital, etc.)
    - lat & lng: User's current location for distance calculations
    - radius: Search radius in kilometers (default: 50km)
    - max_distance: Maximum distance in kilometers
    - emergency: Filter facilities with emergency services (yes/no)
    - wheelchair: Filter wheelchair accessible facilities (yes/no)
    """
    
    queryset = HealthFacility.objects.all()
    pagination_class = HealthFacilityPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return HealthFacilityDetailSerializer
        elif self.action == 'geojson':
            return HealthFacilityGeoJSONSerializer
        elif self.action == 'nearby':
            return NearbyFacilitySerializer
        return HealthFacilityListSerializer
    
    def get_queryset(self):
        """Apply filters to the queryset"""
        queryset = HealthFacility.objects.all()
        
        # Filter by name (case-insensitive partial match)
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # Filter by district (case-insensitive)
        district = self.request.query_params.get('district', None)
        if district:
            queryset = queryset.filter(district__iexact=district)
        
        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region__iexact=region)
        
        # Filter by amenity type
        amenity = self.request.query_params.get('amenity', None)
        if amenity:
            queryset = queryset.filter(amenity__iexact=amenity)
        
        # Filter by emergency services
        emergency = self.request.query_params.get('emergency', None)
        if emergency:
            queryset = queryset.filter(emergency__iexact=emergency)
        
        # Filter by wheelchair accessibility
        wheelchair = self.request.query_params.get('wheelchair', None)
        if wheelchair:
            queryset = queryset.filter(wheelchair__iexact=wheelchair)
        
        # Calculate distance from user's location
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('lng', None)
        
        if lat and lng:
            try:
                user_location = Point(float(lng), float(lat), srid=4326)
                queryset = queryset.annotate(
                    distance=Distance('location', user_location)
                ).order_by('distance')
                
                # Filter by maximum distance
                max_distance = self.request.query_params.get('max_distance', None)
                if max_distance:
                    queryset = queryset.filter(
                        distance__lte=D(km=float(max_distance))
                    )
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Find nearby facilities based on user's current location.
        
        Required Parameters:
        - lat: User's latitude
        - lng: User's longitude
        
        Optional Parameters:
        - radius: Search radius in kilometers (default: 50km)
        - amenity: Filter by amenity type
        - limit: Maximum number of results (default: 20)
        """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude (lat) and longitude (lng) are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_location = Point(float(lng), float(lat), srid=4326)
            radius = float(request.query_params.get('radius', 50))  # Default 50km
            limit = int(request.query_params.get('limit', 20))
            
            # Get facilities within radius
            queryset = HealthFacility.objects.annotate(
                distance=Distance('location', user_location)
            ).filter(
                distance__lte=D(km=radius)
            ).order_by('distance')
            
            # Apply amenity filter if provided
            amenity = request.query_params.get('amenity')
            if amenity:
                queryset = queryset.filter(amenity__iexact=amenity)
            
            # Limit results
            queryset = queryset[:limit]
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': len(queryset),
                'radius_km': radius,
                'user_location': {
                    'latitude': float(lat),
                    'longitude': float(lng)
                },
                'facilities': serializer.data
            })
        
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid parameters: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """
        Return facilities in GeoJSON format for mapping applications.
        Supports same filters as list endpoint.
        """
        queryset = self.get_queryset()
        
        # Limit results for performance
        limit = int(request.query_params.get('limit', 1000))
        queryset = queryset[:limit]
        
        serializer = HealthFacilityGeoJSONSerializer(
            queryset, 
            many=True,
            context={'request': request}
        )
        
        return Response({
            'type': 'FeatureCollection',
            'count': len(queryset),
            'features': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def districts(self, request):
        """Get list of all districts with facility counts"""
        districts = HealthFacility.objects.values('district').distinct().order_by('district')
        
        district_data = []
        for d in districts:
            if d['district']:
                count = HealthFacility.objects.filter(district=d['district']).count()
                district_data.append({
                    'district': d['district'],
                    'facility_count': count
                })
        
        return Response({
            'count': len(district_data),
            'districts': district_data
        })
    
    @action(detail=False, methods=['get'])
    def amenities(self, request):
        """Get list of all amenity types with counts"""
        amenities = HealthFacility.objects.values('amenity').distinct().order_by('amenity')
        
        amenity_data = []
        for a in amenities:
            if a['amenity']:
                count = HealthFacility.objects.filter(amenity=a['amenity']).count()
                amenity_data.append({
                    'amenity': a['amenity'],
                    'facility_count': count
                })
        
        return Response({
            'count': len(amenity_data),
            'amenities': amenity_data
        })
    
    @action(detail=True, methods=['get'])
    def directions(self, request, pk=None):
        """
        Get directions from user's location to a specific facility.
        
        Required Parameters:
        - lat: User's starting latitude
        - lng: User's starting longitude
        
        Returns:
        - Straight-line distance and bearing
        - Facility coordinates
        - Google Maps and OpenStreetMap URLs
        """
        facility = self.get_object()
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude (lat) and longitude (lng) are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_location = Point(float(lng), float(lat), srid=4326)
            
            # Calculate distance
            from django.contrib.gis.geos import Point as GEOSPoint
            distance_m = user_location.distance(facility.location) * 111319.9  # Approximate conversion to meters
            distance_km = distance_m / 1000
            
            # Calculate bearing (approximate)
            import math
            lat1 = math.radians(float(lat))
            lat2 = math.radians(facility.latitude)
            lng1 = math.radians(float(lng))
            lng2 = math.radians(facility.longitude)
            
            dLon = lng2 - lng1
            y = math.sin(dLon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
            bearing = math.degrees(math.atan2(y, x))
            bearing = (bearing + 360) % 360
            
            # Generate navigation URLs
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={facility.latitude},{facility.longitude}"
            osm_url = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={lat}%2C{lng}%3B{facility.latitude}%2C{facility.longitude}"
            
            return Response({
                'facility': {
                    'id': facility.id,
                    'name': facility.name,
                    'latitude': facility.latitude,
                    'longitude': facility.longitude,
                    'district': facility.district,
                    'amenity': facility.amenity
                },
                'from': {
                    'latitude': float(lat),
                    'longitude': float(lng)
                },
                'distance': {
                    'meters': round(distance_m, 2),
                    'kilometers': round(distance_km, 2)
                },
                'bearing': round(bearing, 2),
                'navigation_urls': {
                    'google_maps': google_maps_url,
                    'openstreetmap': osm_url
                }
            })
        
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid parameters: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about health facilities"""
        total_facilities = HealthFacility.objects.count()
        districts_count = HealthFacility.objects.values('district').distinct().count()
        amenities_count = HealthFacility.objects.values('amenity').distinct().count()
        
        # Facilities by amenity type
        amenity_breakdown = {}
        for amenity in HealthFacility.objects.values('amenity').distinct():
            if amenity['amenity']:
                count = HealthFacility.objects.filter(amenity=amenity['amenity']).count()
                amenity_breakdown[amenity['amenity']] = count
        
        # Facilities with emergency services
        emergency_facilities = HealthFacility.objects.filter(
            emergency__iexact='yes'
        ).count()
        
        return Response({
            'total_facilities': total_facilities,
            'total_districts': districts_count,
            'total_amenity_types': amenities_count,
            'facilities_by_amenity': amenity_breakdown,
            'emergency_facilities': emergency_facilities
        })
