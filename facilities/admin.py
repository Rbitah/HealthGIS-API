from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import HealthFacility


@admin.register(HealthFacility)
class HealthFacilityAdmin(GISModelAdmin):
    """Admin interface for Health Facilities with map integration"""
    
    list_display = ['name', 'amenity', 'district', 'region', 'beds', 'emergency']
    list_filter = ['amenity', 'district', 'region', 'emergency', 'wheelchair']
    search_fields = ['name', 'district', 'region', 'operator']
    readonly_fields = ['created_at', 'updated_at', 'latitude', 'longitude']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'osm_id', 'osm_type', 'uuid')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude', 'district', 'region')
        }),
        ('Classification', {
            'fields': ('amenity', 'healthcare', 'speciality', 'health_amenity')
        }),
        ('Operator', {
            'fields': ('operator', 'operator_type', 'operational_status')
        }),
        ('Capacity', {
            'fields': ('beds', 'staff_doctors', 'staff_nurses')
        }),
        ('Services', {
            'fields': ('dispensing', 'wheelchair', 'emergency', 'insurance')
        }),
        ('Infrastructure', {
            'fields': ('water_source', 'electricity')
        }),
        ('Contact', {
            'fields': ('url', 'opening_hours', 'addr_housenumber', 'addr_street', 
                      'addr_postcode', 'addr_city')
        }),
        ('Metadata', {
            'fields': ('source', 'completeness', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Enable map widget
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 6,
            'default_lon': 34.0,
            'default_lat': -13.5,
        }
    }
