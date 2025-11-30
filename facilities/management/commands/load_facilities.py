import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from facilities.models import HealthFacility
from pathlib import Path


class Command(BaseCommand):
    help = 'Load health facility data from Malawi GeoJSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='sampleData/malawi.geojson',
            help='Path to the GeoJSON file (relative to project root)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_data = options['clear']
        
        # Get the base directory
        from django.conf import settings
        base_dir = settings.BASE_DIR
        geojson_path = base_dir / file_path
        
        if not geojson_path.exists():
            self.stdout.write(
                self.style.ERROR(f'File not found: {geojson_path}')
            )
            return
        
        # Clear existing data if requested
        if clear_data:
            self.stdout.write('Clearing existing data...')
            deleted_count = HealthFacility.objects.all().delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_count} existing facilities')
            )
        
        # Load GeoJSON data
        self.stdout.write(f'Loading data from {geojson_path}...')
        
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            total_features = len(features)
            
            self.stdout.write(f'Found {total_features} features in GeoJSON file')
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for index, feature in enumerate(features, 1):
                try:
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    
                    # Extract coordinates
                    coordinates = geometry.get('coordinates', [])
                    if not coordinates or len(coordinates) < 2:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping feature {index}: No valid coordinates')
                        )
                        skipped_count += 1
                        continue
                    
                    lng, lat = coordinates[0], coordinates[1]
                    location = Point(lng, lat, srid=4326)
                    
                    # Get OSM ID
                    osm_id = properties.get('osm_id')
                    if not osm_id:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping feature {index}: No OSM ID')
                        )
                        skipped_count += 1
                        continue
                    
                    # Prepare facility data
                    facility_name = properties.get('name')
                    if not facility_name or facility_name.strip() == '':
                        facility_name = f'Unnamed {properties.get("amenity", "Facility")} {osm_id}'
                    
                    facility_data = {
                        'osm_type': properties.get('osm_type'),
                        'name': facility_name,
                        'uuid': properties.get('uuid'),
                        'location': location,
                        'district': properties.get('district'),
                        'region': properties.get('region'),
                        'area': properties.get('area'),
                        'perimeter': properties.get('perimeter'),
                        'amenity': properties.get('amenity'),
                        'healthcare': properties.get('healthcare'),
                        'speciality': properties.get('speciality'),
                        'health_amenity': properties.get('health_ame'),
                        'operator': properties.get('operator'),
                        'operator_type': properties.get('operator_t'),
                        'operational_status': properties.get('operationa'),
                        'beds': self._parse_int(properties.get('beds')),
                        'staff_doctors': self._parse_int(properties.get('staff_doct')),
                        'staff_nurses': self._parse_int(properties.get('staff_nurs')),
                        'dispensing': properties.get('dispensing'),
                        'wheelchair': properties.get('wheelchair'),
                        'emergency': properties.get('emergency'),
                        'insurance': properties.get('insurance'),
                        'water_source': properties.get('water_sour'),
                        'electricity': properties.get('electricit'),
                        'url': properties.get('url'),
                        'opening_hours': properties.get('opening_ho'),
                        'addr_housenumber': properties.get('addr_house'),
                        'addr_street': properties.get('addr_stree'),
                        'addr_postcode': properties.get('addr_postc'),
                        'addr_city': properties.get('addr_city'),
                        'source': properties.get('source'),
                        'completeness': self._parse_float(properties.get('completene')),
                        'changeset_id': self._parse_int(properties.get('changeset_')),
                        'changeset_version': self._parse_int(properties.get('changese_1')),
                        'changeset_timestamp': properties.get('changese_2'),
                        'is_in_health_system': properties.get('is_in_heal'),
                        'is_in_health_system_1': properties.get('is_in_he_1'),
                    }
                    
                    # Create or update facility
                    facility, created = HealthFacility.objects.update_or_create(
                        osm_id=osm_id,
                        defaults=facility_data
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    # Progress indicator
                    if index % 100 == 0:
                        self.stdout.write(
                            f'Processed {index}/{total_features} features... '
                            f'(Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count})'
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing feature {index}: {str(e)}')
                    )
                    skipped_count += 1
                    continue
            
            # Final summary
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
            self.stdout.write(self.style.SUCCESS(f'Created: {created_count} facilities'))
            self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} facilities'))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} features'))
            self.stdout.write(self.style.SUCCESS('='*50))
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load data: {str(e)}')
            )
            import traceback
            traceback.print_exc()
    
    def _parse_int(self, value):
        """Safely parse integer values"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value):
        """Safely parse float values"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
