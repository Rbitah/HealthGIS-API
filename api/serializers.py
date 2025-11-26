from rest_framework import serializers
from .models import ShapefileLayer
import fiona
from shapely.geometry import shape, mapping
import json


class ShapefileLayerSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = ShapefileLayer
        fields = [
            'id', 'name', 'description', 'geometry_type',
            'shapefile', 'shx_file', 'dbf_file', 'prj_file',
            'geojson_data', 'feature_count', 'srid', 'bounds',
            'uploaded_by', 'uploaded_by_username',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at', 'feature_count', 'bounds', 'geojson_data']
    
    def validate_shapefile(self, value):
        """Validate that the uploaded file is a valid shapefile"""
        if not value.name.endswith('.shp'):
            raise serializers.ValidationError("File must be a .shp shapefile")
        return value
    
    def create(self, validated_data):
        """Process shapefile and extract GeoJSON data"""
        instance = super().create(validated_data)
        self._process_shapefile(instance)
        return instance
    
    def update(self, instance, validated_data):
        """Update shapefile and reprocess if file changed"""
        shapefile_changed = 'shapefile' in validated_data
        instance = super().update(instance, validated_data)
        
        if shapefile_changed:
            self._process_shapefile(instance)
        
        return instance
    
    def _process_shapefile(self, instance):
        """Extract GeoJSON and metadata from shapefile"""
        try:
            with fiona.open(instance.shapefile.path) as src:
                # Extract geometry type
                instance.geometry_type = src.schema['geometry']
                
                # Extract SRID
                if src.crs:
                    instance.srid = src.crs.to_epsg() or 4326
                
                # Extract bounds
                bounds = src.bounds
                instance.bounds = [bounds[0], bounds[1], bounds[2], bounds[3]]
                
                # Convert to GeoJSON
                features = []
                for feature in src:
                    features.append({
                        'type': 'Feature',
                        'geometry': feature['geometry'],
                        'properties': feature['properties']
                    })
                
                instance.feature_count = len(features)
                instance.geojson_data = {
                    'type': 'FeatureCollection',
                    'features': features
                }
                
                instance.save()
        except Exception as e:
            raise serializers.ValidationError(f"Error processing shapefile: {str(e)}")


class ShapefileUploadSerializer(serializers.Serializer):
    """Serializer for uploading complete shapefile package"""
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    shp_file = serializers.FileField()
    shx_file = serializers.FileField(required=False)
    dbf_file = serializers.FileField(required=False)
    prj_file = serializers.FileField(required=False)
    
    def validate_shp_file(self, value):
        if not value.name.endswith('.shp'):
            raise serializers.ValidationError("Main file must be a .shp file")
        return value
    
    def validate_shx_file(self, value):
        if value and not value.name.endswith('.shx'):
            raise serializers.ValidationError("Index file must be a .shx file")
        return value
    
    def validate_dbf_file(self, value):
        if value and not value.name.endswith('.dbf'):
            raise serializers.ValidationError("Attribute file must be a .dbf file")
        return value
    
    def validate_prj_file(self, value):
        if value and not value.name.endswith('.prj'):
            raise serializers.ValidationError("Projection file must be a .prj file")
        return value
