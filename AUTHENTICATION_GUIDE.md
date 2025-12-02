# Admin Authentication & Authorization Guide

## Overview
The admin dashboard API uses JWT (JSON Web Token) authentication. Only users with admin/staff privileges can access the API endpoints.

## Setup

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
Or use the setup script:
```bash
python setup_admin_api.py
```
This creates: username=`admin`, password=`admin123`

### 4. Start Server
```bash
python manage.py runserver
```

## Authentication Flow

### Step 1: Login
**Endpoint:** `POST /api/auth/login/`

**Request:**
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
    "is_staff": true,
    "is_superuser": true
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Step 2: Use Access Token
Include the access token in all subsequent requests:

**Header:**
```
Authorization: Bearer <access_token>
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/shapefiles/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Step 3: Refresh Token (when access token expires)
**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 4: Logout
**Endpoint:** `POST /api/auth/logout/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Authorization Rules

### Admin Requirements
- User must have `is_staff=True` or `is_superuser=True`
- Only admin users can access shapefile management endpoints

### Token Lifetimes
- **Access Token:** 1 hour
- **Refresh Token:** 7 days

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | Login and get tokens | No |
| POST | `/api/auth/logout/` | Logout and blacklist token | Yes |
| GET | `/api/auth/me/` | Get current user info | Yes |
| POST | `/api/auth/refresh/` | Refresh access token | No |

### Shapefile Management Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/shapefiles/` | List all shapefiles | Yes (Admin) |
| POST | `/api/shapefiles/` | Upload new shapefile | Yes (Admin) |
| GET | `/api/shapefiles/{id}/` | Get shapefile details | Yes (Admin) |
| PUT/PATCH | `/api/shapefiles/{id}/edit/` | **Edit shapefile by ID** | Yes (Admin) |
| DELETE | `/api/shapefiles/{id}/` | Delete shapefile | Yes (Admin) |
| GET | `/api/shapefiles/{id}/metadata/` | Get shapefile metadata | Yes (Admin) |
| POST | `/api/shapefiles/{id}/toggle-active/` | Toggle active status | Yes (Admin) |
| GET | `/api/shapefiles/active/` | Get active layers only | Yes (Admin) |

## Edit Shapefile by ID

The dedicated endpoint for editing shapefiles:

**Endpoint:** `PUT/PATCH /api/shapefiles/{id}/edit/`

**What you can edit:**
- `name` - Layer name
- `description` - Layer description
- `geometry_type` - Geometry type (Point, Polygon, etc.)
- `shapefile` - Replace .shp file
- `shx_file` - Replace .shx file
- `dbf_file` - Replace .dbf file
- `prj_file` - Replace .prj file
- `is_active` - Active status

**Example - Edit metadata:**
```bash
curl -X PATCH http://localhost:8000/api/shapefiles/1/edit/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Layer Name",
    "description": "Updated description",
    "geometry_type": "Polygon",
    "is_active": true
  }'
```

**Example - Replace shapefile:**
```bash
curl -X PATCH http://localhost:8000/api/shapefiles/1/edit/ \
  -H "Authorization: Bearer <access_token>" \
  -F "shapefile=@new_file.shp" \
  -F "dbf_file=@new_file.dbf"
```

**Response:**
```json
{
  "message": "Shapefile updated successfully",
  "data": {
    "id": 1,
    "name": "Updated Layer Name",
    "description": "Updated description",
    "geometry_type": "Polygon",
    "is_active": true,
    ...
  }
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied. Admin privileges required."
}
```

### 400 Bad Request
```json
{
  "error": "Please provide both username and password"
}
```

## Testing with Postman

1. **Login:**
   - Method: POST
   - URL: `http://localhost:8000/api/auth/login/`
   - Body (JSON): `{"username": "admin", "password": "admin123"}`
   - Copy the `access` token from response

2. **Access Protected Endpoints:**
   - Add Authorization header
   - Type: Bearer Token
   - Token: Paste the access token

3. **Edit Shapefile:**
   - Method: PATCH
   - URL: `http://localhost:8000/api/shapefiles/1/edit/`
   - Authorization: Bearer Token
   - Body: JSON or form-data depending on what you're updating

## Security Notes

- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Tokens are blacklisted on logout
- Only admin users can access the API
- CSRF protection is enabled
- CORS is configured for localhost:3000
