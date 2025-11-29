from django.contrib import admin
from .models import ShapefileLayer


@admin.register(ShapefileLayer)
class ShapefileLayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'geometry_type', 'feature_count', 'uploaded_by', 'is_active', 'created_at']
    list_filter = ['geometry_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['feature_count', 'bounds', 'geojson_data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Files', {
            'fields': ('shapefile', 'shx_file', 'dbf_file', 'prj_file')
        }),
        ('Metadata', {
            'fields': ('geometry_type', 'feature_count', 'srid', 'bounds'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
