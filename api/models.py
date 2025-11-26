from django.db import models
from django.contrib.auth.models import User
import os


class ShapefileLayer(models.Model):
    """Model to store GIS shapefile metadata and data"""
    
    GEOMETRY_TYPES = [
        ('Point', 'Point'),
        ('LineString', 'LineString'),
        ('Polygon', 'Polygon'),
        ('MultiPoint', 'MultiPoint'),
        ('MultiLineString', 'MultiLineString'),
        ('MultiPolygon', 'MultiPolygon'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    geometry_type = models.CharField(max_length=50, choices=GEOMETRY_TYPES, blank=True)
    
    # File storage
    shapefile = models.FileField(upload_to='shapefiles/', help_text='Upload .shp file')
    shx_file = models.FileField(upload_to='shapefiles/', blank=True, null=True)
    dbf_file = models.FileField(upload_to='shapefiles/', blank=True, null=True)
    prj_file = models.FileField(upload_to='shapefiles/', blank=True, null=True)
    
    # GeoJSON representation (stored for quick access)
    geojson_data = models.JSONField(blank=True, null=True)
    
    # Metadata
    feature_count = models.IntegerField(default=0)
    srid = models.IntegerField(default=4326, help_text='Spatial Reference System ID')
    bounds = models.JSONField(blank=True, null=True, help_text='Bounding box [minx, miny, maxx, maxy]')
    
    # Tracking
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_shapefiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shapefile Layer'
        verbose_name_plural = 'Shapefile Layers'
    
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        """Override delete to remove associated files"""
        # Delete files from storage
        if self.shapefile:
            if os.path.isfile(self.shapefile.path):
                os.remove(self.shapefile.path)
        if self.shx_file:
            if os.path.isfile(self.shx_file.path):
                os.remove(self.shx_file.path)
        if self.dbf_file:
            if os.path.isfile(self.dbf_file.path):
                os.remove(self.dbf_file.path)
        if self.prj_file:
            if os.path.isfile(self.prj_file.path):
                os.remove(self.prj_file.path)
        
        super().delete(*args, **kwargs)
