from rest_framework import serializers
from .models import ShapefileLayer


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
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']
    
    def validate_shapefile(self, value):
        """Validate that the uploaded file is a valid shapefile"""
        if not value.name.endswith('.shp'):
            raise serializers.ValidationError("File must be a .shp shapefile")
        return value


class ShapefileUploadSerializer(serializers.Serializer):
    """Serializer for uploading complete shapefile package"""
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    geometry_type = serializers.CharField(required=False, allow_blank=True)
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
