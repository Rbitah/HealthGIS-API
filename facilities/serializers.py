from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from .models import HealthFacility


class HealthFacilityListSerializer(serializers.ModelSerializer):
    """Serializer for listing health facilities with basic information"""
    
    distance = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFacility
        fields = [
            'id', 'osm_id', 'osm_type', 'name', 'amenity', 'district', 'region',
            'latitude', 'longitude', 'distance', 'healthcare', 'operator',
            'beds', 'emergency', 'wheelchair', 'completeness', 'source',
            'speciality', 'operator_type', 'operational_status', 'opening_hours',
            'staff_doctors', 'staff_nurses', 'health_amenity', 'dispensing',
            'insurance', 'water_source', 'electricity', 'is_in_health_system',
            'is_in_health_system_1', 'url', 'addr_housenumber', 'addr_street',
            'addr_postcode', 'addr_city', 'changeset_id', 'changeset_version',
            'changeset_timestamp', 'uuid', 'area', 'perimeter'
        ]
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude
    
    def get_distance(self, obj):
        """Calculate distance from user's location if provided"""
        request = self.context.get('request')
        if request and hasattr(obj, 'distance'):
            # Distance is already annotated in the queryset
            return round(obj.distance.m, 2)  # Return distance in meters
        return None


class HealthFacilityDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for a single health facility"""
    
    distance = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFacility
        fields = '__all__'
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude
    
    def get_coordinates(self, obj):
        return obj.coordinates
    
    def get_distance(self, obj):
        """Calculate distance from user's location if provided"""
        request = self.context.get('request')
        if request and hasattr(obj, 'distance'):
            return round(obj.distance.m, 2)
        return None


class HealthFacilityGeoJSONSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for mapping applications"""
    
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFacility
        geo_field = 'location'
        fields = [
            'id', 'osm_id', 'osm_type', 'name', 'amenity', 'district', 'region',
            'healthcare', 'operator', 'beds', 'emergency', 'wheelchair',
            'staff_doctors', 'staff_nurses', 'opening_hours', 'url',
            'water_source', 'electricity', 'dispensing', 'insurance',
            'completeness', 'source', 'speciality', 'operator_type',
            'operational_status', 'health_amenity', 'is_in_health_system',
            'is_in_health_system_1', 'addr_housenumber', 'addr_street',
            'addr_postcode', 'addr_city', 'uuid', 'area', 'perimeter',
            'distance'
        ]
    
    def get_distance(self, obj):
        """Calculate distance from user's location if provided"""
        if hasattr(obj, 'distance'):
            return round(obj.distance.m, 2)
        return None


class NearbyFacilitySerializer(serializers.ModelSerializer):
    """Serializer for nearby facilities with distance"""
    
    distance_km = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthFacility
        fields = [
            'id', 'osm_id', 'osm_type', 'name', 'amenity', 'district', 'region',
            'latitude', 'longitude', 'distance_km', 'distance_m',
            'healthcare', 'emergency', 'beds', 'opening_hours', 'operator',
            'wheelchair', 'staff_doctors', 'staff_nurses', 'completeness',
            'speciality', 'operational_status', 'water_source', 'electricity',
            'url', 'addr_street', 'addr_city'
        ]
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude
    
    def get_distance_km(self, obj):
        """Return distance in kilometers"""
        if hasattr(obj, 'distance'):
            return round(obj.distance.km, 2)
        return None
    
    def get_distance_m(self, obj):
        """Return distance in meters"""
        if hasattr(obj, 'distance'):
            return round(obj.distance.m, 2)
        return None


class DirectionsSerializer(serializers.Serializer):
    """Serializer for directions request"""
    
    from_lat = serializers.FloatField(required=True)
    from_lng = serializers.FloatField(required=True)
    to_facility_id = serializers.IntegerField(required=True)
    
    def validate(self, data):
        """Validate that the facility exists"""
        try:
            facility = HealthFacility.objects.get(id=data['to_facility_id'])
            data['facility'] = facility
        except HealthFacility.DoesNotExist:
            raise serializers.ValidationError("Facility not found")
        return data
