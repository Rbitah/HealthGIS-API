from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class HealthFacility(models.Model):
    """Model representing a health facility with geospatial data"""
    
    # Basic Information
    osm_id = models.BigIntegerField(unique=True, db_index=True)
    osm_type = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, db_index=True)
    uuid = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Geospatial Data
    location = models.PointField(srid=4326, spatial_index=True)  # WGS84 coordinate system
    
    # Administrative Information
    district = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    perimeter = models.FloatField(blank=True, null=True)
    
    # Facility Classification
    amenity = models.CharField(max_length=100, db_index=True, blank=True, null=True)  # e.g., clinic, hospital
    healthcare = models.CharField(max_length=100, blank=True, null=True)
    speciality = models.CharField(max_length=255, blank=True, null=True)
    health_amenity = models.CharField(max_length=100, blank=True, null=True, db_column='health_ame')
    
    # Operator Information
    operator = models.CharField(max_length=255, blank=True, null=True)
    operator_type = models.CharField(max_length=100, blank=True, null=True, db_column='operator_t')
    operational_status = models.CharField(max_length=100, blank=True, null=True, db_column='operationa')
    
    # Facility Details
    beds = models.IntegerField(blank=True, null=True)
    staff_doctors = models.IntegerField(blank=True, null=True, db_column='staff_doct')
    staff_nurses = models.IntegerField(blank=True, null=True, db_column='staff_nurs')
    
    # Services and Amenities
    dispensing = models.CharField(max_length=50, blank=True, null=True)
    wheelchair = models.CharField(max_length=50, blank=True, null=True)
    emergency = models.CharField(max_length=50, blank=True, null=True)
    insurance = models.CharField(max_length=255, blank=True, null=True)
    
    # Infrastructure
    water_source = models.CharField(max_length=100, blank=True, null=True, db_column='water_sour')
    electricity = models.CharField(max_length=100, blank=True, null=True, db_column='electricit')
    
    # Contact and Address
    url = models.URLField(blank=True, null=True)
    opening_hours = models.CharField(max_length=255, blank=True, null=True, db_column='opening_ho')
    addr_housenumber = models.CharField(max_length=50, blank=True, null=True, db_column='addr_house')
    addr_street = models.CharField(max_length=255, blank=True, null=True, db_column='addr_stree')
    addr_postcode = models.CharField(max_length=20, blank=True, null=True, db_column='addr_postc')
    addr_city = models.CharField(max_length=100, blank=True, null=True, db_column='addr_city')
    
    # Metadata
    source = models.CharField(max_length=255, blank=True, null=True)
    completeness = models.FloatField(blank=True, null=True, db_column='completene')
    changeset_id = models.BigIntegerField(blank=True, null=True, db_column='changeset_')
    changeset_version = models.IntegerField(blank=True, null=True, db_column='changese_1')
    changeset_timestamp = models.CharField(max_length=50, blank=True, null=True, db_column='changese_2')
    
    # Health system classification
    is_in_health_system = models.CharField(max_length=100, blank=True, null=True, db_column='is_in_heal')
    is_in_health_system_1 = models.CharField(max_length=100, blank=True, null=True, db_column='is_in_he_1')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'health_facilities'
        ordering = ['name']
        verbose_name = 'Health Facility'
        verbose_name_plural = 'Health Facilities'
        indexes = [
            models.Index(fields=['district', 'amenity']),
            models.Index(fields=['region', 'district']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.district or 'Unknown District'})"
    
    @property
    def latitude(self):
        """Get the latitude of the facility"""
        return self.location.y if self.location else None
    
    @property
    def longitude(self):
        """Get the longitude of the facility"""
        return self.location.x if self.location else None
    
    @property
    def coordinates(self):
        """Get coordinates as [longitude, latitude] for GeoJSON"""
        if self.location:
            return [self.location.x, self.location.y]
        return None
    
    def distance_from(self, point):
        """
        Calculate distance from a given point in meters
        point should be a Point object or tuple (longitude, latitude)
        """
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        
        if isinstance(point, tuple):
            point = Point(point[0], point[1], srid=4326)
        
        # Use geodetic distance for accuracy
        return self.location.distance(point) * 111319.9  # Convert degrees to meters approximately
