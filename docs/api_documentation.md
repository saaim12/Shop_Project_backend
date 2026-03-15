# Garage Inventory Management API Documentation

## Base URL
- `/`

## Authentication
Use JWT bearer token for protected endpoints.

Header:
- `Authorization: Bearer <access_token>`

---

## Auth APIs

### POST /auth/register
Create user.

Rules:
- Public can create `CUSTOMER`
- Admin can create `STAFF` or `ADMIN` only
- Admin cannot create `CUSTOMER`
- Creating `STAFF` requires `key` = `SECRET_KEY_FOR_STAFF_USER`
- Creating `ADMIN` requires `key` = `SECRET_KEY_FOR_ADMIN_USER`

Request example:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "password": "Pass12345",
  "phone_number": "+123456789",
  "role": "CUSTOMER"
}
```

Admin create STAFF example:
```json
{
  "name": "Staff One",
  "email": "staff1@example.com",
  "age": 30,
  "password": "Pass12345",
  "phone_number": "+123456780",
  "role": "STAFF",
  "key": "<SECRET_KEY_FOR_STAFF_USER>"
}
```

### POST /auth/login
Request:
```json
{
  "email": "john@example.com",
  "password": "Pass12345"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "<jwt_access>",
    "refresh": "<jwt_refresh>",
    "user": {
      "id": "67d...",
      "name": "John Doe",
      "role": "CUSTOMER"
    }
  }
}
```

### POST /auth/logout
Protected endpoint.

### POST /auth/refresh
Request:
```json
{
  "refresh": "<jwt_refresh>"
}
```

Response:
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access": "<new_jwt_access>"
  }
}
```

---

## User APIs

### GET /users
- Admin only
- List all users

### POST /users/{user_id}
- Admin only
- Get user by id

### GET /profile_data/{user_id}
- Admin or self

### GET /users/me
- Authenticated user profile

### PATCH /users/me
- Authenticated user updates only own profile

Allowed fields:
- `name`, `email`, `age`, `phone_number`
- password change using `old_password`, `new_password`

### POST /user-update/{user_id}
- Admin only
- Update any user

### DELETE /user/delete/{user_id}
- Admin only
- Admin can delete `STAFF` and `ADMIN`
- Admin cannot delete `CUSTOMER`

---

## Spare Parts APIs

### GET /spare-parts/
Public list (with pagination).

Filters:
- `name`, `brand`, `model`, `model_year`, `vehicle_type`, `category`, `condition`, `item_number`, `engine_code`, `oem_numbers`

### POST /spare-parts/
- Staff/Admin only

### GET /spare-parts/{id}
- Public

### PATCH /spare-parts/{id}
- Staff/Admin only

### DELETE /spare-parts/{id}
- Staff/Admin only

---

## Cars APIs

### GET /cars/
- Public
- Filters: `name`, `brand`, `model`, `model_year`, `year`, `condition`

### POST /cars/
- Staff/Admin only

### GET /cars/{id}
- Public

### PATCH /cars/{id}
- Staff/Admin only

### DELETE /cars/{id}
- Staff/Admin only

---

## Tyres APIs

### GET /tyres/
- Public
- Filters: `company`, `condition`, `inches`, `type`

### POST /tyres/
- Staff/Admin only

### GET /tyres/{id}
- Public

### PATCH /tyres/{id}
- Staff/Admin only

### DELETE /tyres/{id}
- Staff/Admin only

---

## Rims APIs

### GET /rims/
- Public
- Filters: `company`, `condition`, `inches`, `type`

### POST /rims/
- Staff/Admin only

### GET /rims/{id}
- Public

### PATCH /rims/{id}
- Staff/Admin only

### DELETE /rims/{id}
- Staff/Admin only

---

## Image APIs (Spare Parts / Cars / Tyres / Rims)

### POST /{resource}/{id}/images
- Upload multiple images
- Staff/Admin only

Form-data:
- `images`: multiple files

### PATCH /{resource}/images/{image_id}
- Update one image
- Staff/Admin only

Form-data:
- `image`: single file

### DELETE /{resource}/images/{image_id}
- Delete one image
- Staff/Admin only

### DELETE /{resource}/{id}/images
- Delete all images of resource
- Staff/Admin only

---

## Inventory APIs

### GET /inventory/
- Staff/Admin only

### POST /inventory/
- Staff/Admin only

Request:
```json
{
  "spare_part_id": "67d...",
  "quantity": 10,
  "storage_position": "A-R1-S1"
}
```

### PATCH /inventory/{inventory_id}
- Staff/Admin only

### DELETE /inventory/{inventory_id}
- Staff/Admin only

Inventory response example:
```json
{
  "id": "67f...",
  "spare_part_id": "67d...",
  "quantity": 10,
  "storage_position": "A-R1-S1",
  "added_by": "67a...",
  "created_at": "2026-03-13T12:00:00Z",
  "updated_at": "2026-03-13T12:00:00Z"
}
```

Inventory auto-delete logic:
- If inventory quantity becomes `0`:
  - related spare part is deleted
  - related spare part images are deleted from S3
  - inventory row is deleted

---

## Pagination
List endpoints return:
```json
{
  "count": 120,
  "next": "http://localhost:8000/spare-parts/?page=2",
  "previous": null,
  "results": []
}
```

---

## Validation Rules
- `condition` allowed values: `NEW`, `USED`, `REFURBISHED`
- `model_year` must be > 1950 and <= current year
- user `age` must be between 18 and 90
- email must be unique
- password must be at least 8 chars and include letters + numbers

---

## Seed Data
Command:
```bash
python manage.py seed_mock_data
```

Seeds:
- 3 spare parts
- 3 cars
- 3 tyres
- 3 rims
- inventory entries for spare parts
