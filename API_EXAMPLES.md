# API Usage Examples

This document provides HTTP request examples for the Health Facility Locator API.

## Base URL
```
http://localhost:8000/api/
```

---

## 1. List All Facilities

```http
GET /api/facilities/
```

**Response:**
```json
{
  "count": 152,
  "next": "http://localhost:8000/api/facilities/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "osm_id": 5674018523,
      "name": "Chuba Clinic",
      "amenity": "clinic",
      "district": "CHITIPA",
      "region": "NORTHERN",
      "latitude": -9.5234,
      "longitude": 33.2876
    }
  ]
}
```

---

## 2. Filter by District

```http
GET /api/facilities/?district=LILONGWE
```

**Response:** Same format as list all facilities, filtered by district.

---

## 3. Filter by Facility Name

```http
GET /api/facilities/?search=health
```

**Response:** Same format as list all facilities, filtered by name.

---

## 4. Filter by Amenity Type

```http
GET /api/facilities/?amenity=hospital
```

```http
GET /api/facilities/?amenity=clinic
```

```http
GET /api/facilities/?amenity=pharmacy
```

**Response:** Same format as list all facilities, filtered by amenity type.

---

## 5. Find Facilities Near Current Location

```http
GET /api/facilities/nearby/?lat=-13.9626&lng=33.7741&radius=25
```

**Parameters:**
- `lat`: Latitude (e.g., -13.9626 for Lilongwe)
- `lng`: Longitude (e.g., 33.7741 for Lilongwe)
- `radius`: Search radius in kilometers (default: 50)

**Response:**
```json
{
  "count": 15,
  "radius_km": 25.0,
  "user_location": {
    "latitude": -13.9626,
    "longitude": 33.7741
  },
  "facilities": [
    {
      "id": 42,
      "name": "Kamuzu Central Hospital",
      "amenity": "hospital",
      "district": "LILONGWE",
      "region": "CENTRAL",
      "latitude": -13.9836,
      "longitude": 33.7886,
      "distance_km": 2.87,
      "distance_m": 2874.32,
      "emergency": "yes",
      "beds": 750
    }
  ]
}
```

---

## 6. Filter by Distance from Location

```http
GET /api/facilities/?lat=-13.9626&lng=33.7741&max_distance=50
```

**Parameters:**
- `lat`: User latitude
- `lng`: User longitude
- `max_distance`: Maximum distance in kilometers

**Response:** Same format as list all facilities with distance information included.

---

## 7. Get Facility Details

```http
GET /api/facilities/247/
```

**Response:**
```json
{
  "id": 247,
  "osm_id": 12745842056,
  "osm_type": "node",
  "name": "Alshefaa Health Centre",
  "amenity": "hospital",
  "district": "ZOMBA",
  "region": "SOUTH",
  "latitude": -15.4516,
  "longitude": 35.4070,
  "operator": null,
  "beds": null,
  "emergency": null,
  "wheelchair": null,
  "completeness": 15.625,
  "source": null,
  "speciality": null
}
```

---

## 8. Get Directions to Facility

```http
GET /api/facilities/247/directions/?lat=-15.38841&lng=35.337439
```

**Parameters:**
- `lat`: User's current latitude
- `lng`: User's current longitude

**Response:**
```json
{
  "facility": {
    "id": 247,
    "name": "Alshefaa Health Centre",
    "latitude": -15.4516,
    "longitude": 35.4070,
    "district": "ZOMBA",
    "amenity": "hospital"
  },
  "from": {
    "latitude": -15.38841,
    "longitude": 35.337439
  },
  "distance": {
    "meters": 8234.45,
    "kilometers": 8.23
  },
  "bearing": 42.56,
  "navigation_urls": {
    "google_maps": "https://www.google.com/maps/dir/?api=1&origin=-15.38841,35.337439&destination=-15.4516,35.4070",
    "openstreetmap": "https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=-15.38841%2C35.337439%3B-15.4516%2C35.4070"
  }
}
```

---

## 9. Get GeoJSON Data for Mapping

```http
GET /api/facilities/geojson/
```

**With filters:**
```http
GET /api/facilities/geojson/?district=LILONGWE&amenity=hospital
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "count": 45,
  "features": [
    {
      "type": "Feature",
      "id": 1,
      "geometry": {
        "type": "Point",
        "coordinates": [33.7886, -13.9836]
      },
      "properties": {
        "id": 1,
        "name": "Kamuzu Central Hospital",
        "amenity": "hospital",
        "district": "LILONGWE",
        "region": "CENTRAL",
        "beds": 750,
        "emergency": "yes"
      }
    }
  ]
}
```

---

## 10. Get List of Districts

```http
GET /api/facilities/districts/
```

**Response:**
```json
{
  "count": 26,
  "districts": [
    {
      "name": "CHITIPA",
      "facility_count": 5
    },
    {
      "name": "LILONGWE",
      "facility_count": 42
    }
  ]
}
```

---

## 11. Get List of Amenity Types

```http
GET /api/facilities/amenities/
```

**Response:**
```json
{
  "count": 5,
  "amenities": [
    {
      "amenity": "clinic",
      "facility_count": 68
    },
    {
      "amenity": "hospital",
      "facility_count": 62
    },
    {
      "amenity": "pharmacy",
      "facility_count": 16
    },
    {
      "amenity": "dentist",
      "facility_count": 5
    },
    {
      "amenity": "doctors",
      "facility_count": 1
    }
  ]
}
```

---

## 12. Get Statistics

```http
GET /api/facilities/stats/
```

**Response:**
```json
{
  "total_facilities": 152,
  "total_districts": 26,
  "total_amenity_types": 5,
  "facilities_by_amenity": {
    "clinic": 68,
    "hospital": 62,
    "pharmacy": 16,
    "dentist": 5,
    "doctors": 1
  },
  "facilities_by_region": {
    "NORTHERN": 21,
    "CENTRAL": 60,
    "SOUTHERN": 68,
    "SOUTH": 3
  }
}
```

---

## 13. Combined Filters

**Find hospitals with emergency services in Lilongwe:**
```http
GET /api/facilities/?district=LILONGWE&amenity=hospital&emergency=yes
```

**Find wheelchair-accessible facilities near location:**
```http
GET /api/facilities/?lat=-13.9626&lng=33.7741&max_distance=15&wheelchair=yes
```

**Find clinics in specific region:**
```http
GET /api/facilities/?region=CENTRAL&amenity=clinic
```

---

## 14. Pagination

```http
GET /api/facilities/?page=2
```

**Custom page size:**
```http
GET /api/facilities/?page=1&page_size=50
```

**Parameters:**
- `page`: Page number (starts at 1)
- `page_size`: Results per page (default: 20, max: 100)

**Response includes pagination info:**
```json
{
  "count": 152,
  "next": "http://localhost:8000/api/facilities/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Error Responses

**Invalid coordinates (400 Bad Request):**
```http
GET /api/facilities/nearby/?lat=invalid&lng=33.7741
```
```json
{
  "error": "Invalid parameters: could not convert string to float: 'invalid'"
}
```

**Missing required parameters (400 Bad Request):**
```http
GET /api/facilities/nearby/
```
```json
{
  "error": "Latitude (lat) and longitude (lng) are required"
}
```

**Facility not found (404 Not Found):**
```http
GET /api/facilities/99999/
```
```json
{
  "detail": "Not found."
}
```

---

## Query Parameter Reference

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search facility name | `?search=hospital` |
| `district` | string | Filter by district | `?district=LILONGWE` |
| `region` | string | Filter by region | `?region=CENTRAL` |
| `amenity` | string | Filter by type | `?amenity=hospital` |
| `lat` | float | User latitude | `?lat=-13.9626` |
| `lng` | float | User longitude | `?lng=33.7741` |
| `radius` | integer | Search radius (km) | `?radius=25` |
| `max_distance` | integer | Max distance (km) | `?max_distance=50` |
| `emergency` | string | Emergency services | `?emergency=yes` |
| `wheelchair` | string | Wheelchair access | `?wheelchair=yes` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Results per page | `?page_size=50` |
