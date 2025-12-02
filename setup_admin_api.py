#!/usr/bin/env python


import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthGIS.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User


def setup():
    print("=" * 50)
    print("Admin Dashboard API Setup")
    print("=" * 50)
    
    # Create migrations
    print("\n1. Creating migrations...")
    call_command('makemigrations')
    
    # Run migrations
    print("\n2. Running migrations...")
    call_command('migrate')
    
    # Create superuser if it doesn't exist
    print("\n3. Setting up admin user...")
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user (username: admin, password: admin123)")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Admin user created successfully!")
    else:
        print("✓ Admin user already exists")
    
    # Create media directory
    print("\n4. Creating media directory...")
    media_dir = os.path.join(os.path.dirname(__file__), 'media', 'shapefiles')
    os.makedirs(media_dir, exist_ok=True)
    print(f"✓ Media directory created at: {media_dir}")
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run the development server: python manage.py runserver")
    print("2. Access the admin panel: http://localhost:8000/admin/")
    print("3. Login with username: admin, password: admin123")
    print("4. API endpoint: http://localhost:8000/api/shapefiles/")
    print("\nSee API_DOCUMENTATION.md for full API documentation.")


if __name__ == '__main__':
    setup()
