from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import ShapefileLayer
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class ShapefileAPITestCase(TestCase):
    """Test cases for Shapefile Admin API"""
    
    def setUp(self):
        """Set up test client and admin user"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a test shapefile layer
        self.test_layer = ShapefileLayer.objects.create(
            name='Test Layer',
            description='Test description',
            geometry_type='Point',
            uploaded_by=self.admin_user
        )
    
    def test_list_shapefiles(self):
        """Test listing all shapefiles"""
        response = self.client.get('/api/shapefiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Layer')
    
    def test_retrieve_shapefile(self):
        """Test retrieving a single shapefile"""
        response = self.client.get(f'/api/shapefiles/{self.test_layer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Layer')
    
    def test_update_shapefile(self):
        """Test updating shapefile metadata"""
        data = {'name': 'Updated Layer', 'description': 'Updated description'}
        response = self.client.patch(
            f'/api/shapefiles/{self.test_layer.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Layer')
    
    def test_delete_shapefile(self):
        """Test deleting a shapefile"""
        response = self.client.delete(f'/api/shapefiles/{self.test_layer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ShapefileLayer.objects.count(), 0)
    
    def test_toggle_active(self):
        """Test toggling active status"""
        initial_status = self.test_layer.is_active
        response = self.client.post(f'/api/shapefiles/{self.test_layer.id}/toggle-active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_layer.refresh_from_db()
        self.assertEqual(self.test_layer.is_active, not initial_status)
    
    def test_active_layers_filter(self):
        """Test filtering active layers"""
        # Create inactive layer
        ShapefileLayer.objects.create(
            name='Inactive Layer',
            is_active=False,
            uploaded_by=self.admin_user
        )
        
        response = self.client.get('/api/shapefiles/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Layer')
    
    def test_unauthorized_access(self):
        """Test that non-admin users cannot access the API"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/shapefiles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_non_admin_access(self):
        """Test that regular users cannot access admin endpoints"""
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123'
        )
        self.client.force_authenticate(user=regular_user)
        response = self.client.get('/api/shapefiles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ShapefileModelTestCase(TestCase):
    """Test cases for ShapefileLayer model"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
    
    def test_create_shapefile_layer(self):
        """Test creating a shapefile layer"""
        layer = ShapefileLayer.objects.create(
            name='Test Layer',
            description='Test description',
            geometry_type='Polygon',
            uploaded_by=self.admin_user
        )
        self.assertEqual(layer.name, 'Test Layer')
        self.assertEqual(layer.geometry_type, 'Polygon')
        self.assertTrue(layer.is_active)
    
    def test_shapefile_str_representation(self):
        """Test string representation of shapefile"""
        layer = ShapefileLayer.objects.create(
            name='My Layer',
            uploaded_by=self.admin_user
        )
        self.assertEqual(str(layer), 'My Layer')
    
    def test_unique_name_constraint(self):
        """Test that shapefile names must be unique"""
        ShapefileLayer.objects.create(
            name='Unique Layer',
            uploaded_by=self.admin_user
        )
        
        with self.assertRaises(Exception):
            ShapefileLayer.objects.create(
                name='Unique Layer',
                uploaded_by=self.admin_user
            )
