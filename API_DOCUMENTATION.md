# Admin Dashboard API - GIS Shapefile Management

## Overview
This API provides complete CRUD operations for managing GIS shapefiles in the healthGIS backend. Only authenticated admin users can access these endpoints.

## Authentication
All endpoints require JWT authentication. Admin users only.

### Login Endpoint
**POST** `/api/auth/login/`

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "is_staff": true,
    "is_superuser": true
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Using JWT Token
Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Base URL
```
http://localhost:8000/api/
```

## Authentication Endpoints

### 1. Login
**POST** `/api/auth/login/`
- Body: `{"username": "admin", "password": "password"}`
- Returns: JWT tokens and user info

### 2. Logout
**POST** `/api/auth/logout/`
- Body: `{"refresh": "refresh_token"}`
- Requires: Authentication

### 3. Get Current User
**GET** `/api/auth/me/`
- Returns: Current user information
- Requires: Authentication

### 4. Refresh Token
**POST** `/api/auth/refresh/`
- Body: `{"refresh": "refresh_token"}`
- Returns: New access token

## Shapefile Management Endpoints

### 1. List All Shapefiles
**GET** `/api/shapefiles/`

Returns a list of all uploaded shapefiles.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Health Facilities",
    "description": "Location of health facilities",
    "geometry_type": "Point",
    "shapefile": "/media/shapefiles/facilities.shp",
    "feature_count": 150,
    "srid": 4326,
    "bounds": [-180, -90, 180, 90],
    "uploaded_by": 1,
    "uploaded_by_username": "admin",
    "created_at": "2025-11-26T10:00:00Z",
    "updated_at": "2025-11-26T10:00:00Z",
    "is_active": true
  }
]
```

### 2. Get Active Layers Only
**GET** `/api/shapefiles/active/`

Returns only active shapefile layers.

### 3. Get Single Shapefile
**GET** `/api/shapefiles/{id}/`

Returns details of a specific shapefile.

### 4. Upload Shapefile (Simple)
**POST** `/api/shapefiles/`

Upload a single .shp file with metadata.

**Form Data:**
- `name` (required): Layer name
- `description` (optional): Layer description
- `shapefile` (required): .shp file
- `shx_file` (optional): .shx file
- `dbf_file` (optional): .dbf file
- `prj_file` (optional): .prj file

**Example using cURL:**
```bash
curl -X POST http://localhost:8000/api/shapefiles/ \
  -H "Authorization: Basic <credentials>" \
  -F "name=My Layer" \
  -F "description=Test layer" \
  -F "shapefile=@path/to/file.shp" \
  -F "dbf_file=@path/to/file.dbf" \
  -F "shx_file=@path/to/file.shx" \
  -F "prj_file=@path/to/file.prj"
```

### 5. Upload Complete Shapefile Package
**POST** `/api/shapefiles/upload-complete/`

Upload all shapefile components at once.

**Form Data:**
- `name` (required): Layer name
- `description` (optional): Layer description
- `shp_file` (required): .shp file
- `shx_file` (optional): .shx file
- `dbf_file` (optional): .dbf file
- `prj_file` (optional): .prj file

### 6. Edit Shapefile by ID
**PUT/PATCH** `/api/shapefiles/{id}/edit/`

Edit an existing shapefile using its ID. This is the dedicated admin endpoint for editing.

**Can update:**
- name
- description
- geometry_type
- shapefile (replace .shp file)
- shx_file, dbf_file, prj_file
- is_active

**Example:**
```bash
curl -X PATCH http://localhost:8000/api/shapefiles/1/edit/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "description": "New description", "is_active": true}'
```

**Response:**
```json
{
  "message": "Shapefile updated successfully",
  "data": {
    "id": 1,
    "name": "Updated Name",
    "description": "New description",
    ...
  }
}
```

### 7. Update Shapefile (Alternative)
**PUT** `/api/shapefiles/{id}/`

Update an existing shapefile completely.

**PATCH** `/api/shapefiles/{id}/`

Partially update a shapefile.

### 8. Delete Shapefile
**DELETE** `/api/shapefiles/{id}/`

Permanently delete a shapefile and all associated files.

**Response:** `204 No Content`

### 9. Get Metadata
**GET** `/api/shapefiles/{id}/metadata/`

Returns the metadata of the shapefile.

**Response:**
```json
{
  "name": "Health Facilities",
  "geometry_type": "Point",
  "feature_count": 150,
  "srid": 4326,
  "bounds": [-180, -90, 180, 90]
}
```

### 10. Toggle Active Status
**POST** `/api/shapefiles/{id}/toggle-active/`

Toggle the `is_active` status of a shapefile layer.

## Error Responses

### 400 Bad Request
```json
{
  "shapefile": ["File must be a .shp shapefile"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access Admin Panel
Navigate to `http://localhost:8000/admin/` and login with your admin credentials.

## Testing with Postman

1. **Authentication**: Use Basic Auth with your admin credentials
2. **Upload File**: 
   - Set method to POST
   - URL: `http://localhost:8000/api/shapefiles/`
   - Body: form-data
   - Add files and text fields as specified above

## Notes

- All shapefile uploads are automatically processed to extract GeoJSON data
- Files are stored in the `media/shapefiles/` directory
- The API automatically extracts metadata like geometry type, feature count, and bounds
- Deleting a shapefile removes all associated files from storage
- Only admin users can access these endpoints
