from django.test import TestCase
from django.contrib.gis.geos import Point
from .models import HealthFacility


class HealthFacilityModelTest(TestCase):
    """Test cases for HealthFacility model"""
    
    def setUp(self):
        """Create test facilities"""
        self.facility1 = HealthFacility.objects.create(
            osm_id=1234567890,
            name="Test Hospital",
            location=Point(33.7741, -13.9626, srid=4326),
            district="LILONGWE",
            region="CENTRAL",
            amenity="hospital",
            beds=100,
            emergency="yes"
        )
        
        self.facility2 = HealthFacility.objects.create(
            osm_id=9876543210,
            name="Test Clinic",
            location=Point(33.8000, -14.0000, srid=4326),
            district="LILONGWE",
            region="CENTRAL",
            amenity="clinic",
            beds=20,
            emergency="no"
        )
    
    def test_facility_creation(self):
        """Test that facilities are created correctly"""
        self.assertEqual(HealthFacility.objects.count(), 2)
        self.assertEqual(self.facility1.name, "Test Hospital")
        self.assertEqual(self.facility1.amenity, "hospital")
    
    def test_facility_coordinates(self):
        """Test coordinate properties"""
        self.assertEqual(self.facility1.latitude, -13.9626)
        self.assertEqual(self.facility1.longitude, 33.7741)
        self.assertEqual(self.facility1.coordinates, [33.7741, -13.9626])
    
    def test_facility_string_representation(self):
        """Test string representation"""
        expected = "Test Hospital (LILONGWE)"
        self.assertEqual(str(self.facility1), expected)
    
    def test_facility_filtering_by_district(self):
        """Test filtering facilities by district"""
        facilities = HealthFacility.objects.filter(district="LILONGWE")
        self.assertEqual(facilities.count(), 2)
    
    def test_facility_filtering_by_amenity(self):
        """Test filtering facilities by amenity type"""
        hospitals = HealthFacility.objects.filter(amenity="hospital")
        clinics = HealthFacility.objects.filter(amenity="clinic")
        self.assertEqual(hospitals.count(), 1)
        self.assertEqual(clinics.count(), 1)
