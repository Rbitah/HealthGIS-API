from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import ShapefileLayer
from .serializers import ShapefileLayerSerializer, ShapefileUploadSerializer


class ShapefileLayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing GIS shapefile layers.
    
    Provides CRUD operations for shapefiles:
    - list: Get all shapefiles
    - retrieve: Get a specific shapefile
    - create: Upload a new shapefile
    - update: Update shapefile metadata
    - partial_update: Partially update shapefile
    - destroy: Delete a shapefile
    - upload_complete: Upload all shapefile components at once
    """
    queryset = ShapefileLayer.objects.all()
    serializer_class = ShapefileLayerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to the current user"""
        serializer.save(uploaded_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update shapefile and track the user"""
        serializer.save()
    
    @action(detail=False, methods=['post'], url_path='upload-complete')
    def upload_complete(self, request):
        """
        Upload a complete shapefile package with all components.
        
        Expected form-data:
        - name: Layer name
        - description: Layer description (optional)
        - shp_file: .shp file (required)
        - shx_file: .shx file (optional)
        - dbf_file: .dbf file (optional)
        - prj_file: .prj file (optional)
        """
        serializer = ShapefileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create ShapefileLayer instance
            shapefile_data = {
                'name': serializer.validated_data['name'],
                'description': serializer.validated_data.get('description', ''),
                'geometry_type': serializer.validated_data.get('geometry_type', ''),
                'shapefile': serializer.validated_data['shp_file'],
                'shx_file': serializer.validated_data.get('shx_file'),
                'dbf_file': serializer.validated_data.get('dbf_file'),
                'prj_file': serializer.validated_data.get('prj_file'),
            }
            
            layer_serializer = ShapefileLayerSerializer(data=shapefile_data)
            if layer_serializer.is_valid():
                layer_serializer.save(uploaded_by=request.user)
                return Response(layer_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(layer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='metadata')
    def get_metadata(self, request, pk=None):
        """Get the metadata of the shapefile"""
        layer = self.get_object()
        metadata = {
            'name': layer.name,
            'geometry_type': layer.geometry_type,
            'feature_count': layer.feature_count,
            'srid': layer.srid,
            'bounds': layer.bounds,
        }
        return Response(metadata)
    
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """Toggle the is_active status of a shapefile layer"""
        layer = self.get_object()
        layer.is_active = not layer.is_active
        layer.save()
        serializer = self.get_serializer(layer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='active')
    def active_layers(self, request):
        """Get only active shapefile layers"""
        active_layers = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_layers, many=True)
        return Response(serializer.data)
