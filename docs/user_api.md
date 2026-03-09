# User API Reference

Supported base URLs:
- `/users/`

## Implemented Endpoints
- `POST {base}/create/`
- `GET {base}/getall/`
- `GET {base}/info/`
- `PUT {base}/update/`
- `PUT {base}/update-photo/`
- `POST {base}/change-password/`
- `POST {base}/login/`
- `POST {base}/logout/`
- `DELETE {base}/delete/<user_id>/`

Legacy aliases kept for compatibility:
- `POST {base}/` maps to create
- `GET {base}/all/` maps to getall

## Auth Flow (Django Auth Session)
1. Call `POST /users/login/` with email/password.
2. On success, Django creates a session (`sessionid` cookie).
3. Send that cookie with subsequent protected requests.
4. Call `POST /users/logout/` to clear the session.

Notes:
- This project uses Django session auth (not JWT).
- In browsers, cookies are managed automatically.
- In API clients (Postman/Insomnia/curl), persist cookies between requests.
- If you get CSRF errors on authenticated `POST/PUT/DELETE` with session cookie, test protected endpoints using Basic Auth (`email` + `password`) in Postman.

## Quick Start: Test Every API (Postman/cURL)
Use `/users/` for all examples below.

1. Create a user with `POST /create/`.
2. Login with `POST /login/` and store cookies (`sessionid`).
3. Call `GET /info/`.
4. Call `PUT /update/`.
5. Call `PUT /update-photo/`.
6. Call `POST /change-password/` (logs you out).
7. Login again with new password.
8. Call `GET /getall/` using superuser account.
9. Call `DELETE /delete/<user_id>/` (soft delete).
10. Call `DELETE /delete/<user_id>/?hard=true` as superuser.

## General Validation Rules
- Send JSON with `Content-Type: application/json`.
- Use `multipart/form-data` only when uploading an `image` file.
- Email must be unique.
- Password must be at least 8 characters with letters and numbers.
- Age must be at least 18.
- Phone must contain 7-15 digits and may start with `+`.
- `user_type` values: `customer` or `staff`.

## S3/Spaces Image Handling
- During `create` and `update`, image files are uploaded to S3/Spaces and saved as `image` URL.
- On image replace (update), old image is deleted from S3/Spaces.
- On hard delete, user image is deleted from S3/Spaces.
- On soft delete, account is deactivated (`is_active=false`) and image is kept.

## Secrets for Privileged Creation
- `SECRET_KEY_FOR_STAFF_USER`
- `SECRET_KEY_FOR_ADMIN_USER`

## 1) Create User
`POST /users/create/`

### Body Fields
| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `first_name` | string | Yes | Max 150 chars |
| `last_name` | string | Yes | Max 150 chars |
| `email` | string | Yes | Must be unique |
| `password` | string | Yes | Minimum 8 chars |
| `phone` | string | Yes | 7-15 digits, may start with `+` |
| `age` | integer | Yes | Minimum 18 |
| `user_type` | string | Optional | `customer` (default) or `staff` |
| `image` | file | Optional | Use multipart upload |
| `key` | string | Conditional | Required for `staff` and `is_superuser=true` |
| `is_superuser` | boolean | Conditional | True only for superuser creation |

### Example
```json
{
  "first_name": "Cara",
  "last_name": "Driver",
  "email": "cara.customer@example.com",
  "password": "CustomerPass123",
  "phone": "+15550202",
  "age": 28,
  "user_type": "customer"
}
```

### Staff Create Example
```json
{
  "first_name": "Ben",
  "last_name": "Service",
  "email": "ben.staff@example.com",
  "password": "StrongPass456",
  "phone": "+15550101",
  "age": 32,
  "user_type": "staff",
  "key": "<SECRET_KEY_FOR_STAFF_USER>"
}
```

### Superuser Create Example
```json
{
  "first_name": "Alice",
  "last_name": "Root",
  "email": "alice.root@example.com",
  "password": "UltraSecure789",
  "phone": "+15550303",
  "age": 35,
  "is_superuser": true,
  "key": "<SECRET_KEY_FOR_ADMIN_USER>"
}
```

### Success Response (201)
```json
{
  "id": "67c9d7b5f6a2c14d8c7f0a01",
  "first_name": "Cara",
  "last_name": "Driver",
  "email": "cara.customer@example.com",
  "phone": "+15550202",
  "user_type": "customer",
  "age": 28,
  "image": null,
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "created_at": "2026-03-09T12:10:00Z",
  "updated_at": "2026-03-09T12:10:00Z"
}
```

## 2) Login
`POST /users/login/`

### Request
```json
{
  "email": "cara.customer@example.com",
  "password": "CustomerPass123"
}
```

### Success Response (200)
```json
{
  "message": "Login successful",
  "photo": "https://cdn.example.com/users/cara.jpg",
  "user": {
    "id": "67c9d7b5f6a2c14d8c7f0a01",
    "first_name": "Cara",
    "last_name": "Driver",
    "email": "cara.customer@example.com",
    "phone": "+15550202",
    "user_type": "customer",
    "age": 28,
    "image": null,
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "created_at": "2026-03-09T12:10:00Z",
    "updated_at": "2026-03-09T12:10:00Z"
  }
}
```

### Error Response (401)
```json
{
  "error": "Invalid credentials"
}
```

### Login cURL Example
```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"cara.customer@example.com","password":"CustomerPass123"}'
```

## 3) Logout
`POST /users/logout/`

### Request
```json
{}
```

### Logout cURL Example
```bash
curl -X POST http://localhost:8000/users/logout/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{}'
```

### Success Response (200)
```json
{
  "message": "Logout successful"
}
```

## 4) Get Logged-In User Info
`GET /users/info/`

Required auth:
- Must be logged in (valid Django session cookie)

### Success Response (200)
```json
{
  "photo": "https://cdn.example.com/users/cara.jpg",
  "user": {
    "id": "67c9d7b5f6a2c14d8c7f0a01",
    "first_name": "Cara",
    "last_name": "Driver",
    "email": "cara.customer@example.com",
    "phone": "+15550202",
    "user_type": "customer",
    "age": 28,
    "image": "https://cdn.example.com/users/cara.jpg",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "created_at": "2026-03-09T12:10:00Z",
    "updated_at": "2026-03-09T12:10:00Z"
  }
}
```

## 5) Update Logged-In User Profile
`PUT /users/update/`

Required auth:
- Must be logged in (valid Django session cookie)

Accepted fields:
- `first_name`, `last_name`, `phone`, `age`
- Optional image file using `multipart/form-data` field name `image`

### Request Example (JSON)
```json
{
  "first_name": "Cara Updated",
  "phone": "+15550999",
  "age": 29
}
```

### Success Response (200)
```json
{
  "message": "Profile updated successfully",
  "photo": "https://cdn.example.com/users/cara-new.jpg",
  "user": {
    "id": "67c9d7b5f6a2c14d8c7f0a01",
    "first_name": "Cara Updated",
    "last_name": "Driver",
    "email": "cara.customer@example.com",
    "phone": "+15550999",
    "user_type": "customer",
    "age": 29,
    "image": "https://cdn.example.com/users/cara-new.jpg",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "created_at": "2026-03-09T12:10:00Z",
    "updated_at": "2026-03-09T12:20:00Z"
  }
}
```

## 6) Change Password
`POST /users/change-password/`

Required auth:
- Must be logged in (valid Django session cookie)

### Request
```json
{
  "old_password": "CustomerPass123",
  "new_password": "CustomerPass456"
}
```

### Success Response (200)
```json
{
  "message": "Password changed successfully. Please login again."
}
```

After success, current session is logged out for security.

## 7) Update Logged-In User Photo
`PUT /users/update-photo/`

Required auth:
- Must be logged in (valid Django session cookie)

Request type:
- `multipart/form-data`
- Required file field: `image`

### Request Example (JSON-like)
```json
{
  "image": "<binary_file_multipart>"
}
```

### cURL Example
```bash
curl -X PUT http://localhost:8000/users/update-photo/ \
  -b cookies.txt \
  -F "image=@C:/path/to/photo.jpg"
```

### Success Response (200)
```json
{
  "message": "Photo updated successfully",
  "photo": "https://cdn.example.com/users/cara-new.jpg",
  "user": {
    "id": "67c9d7b5f6a2c14d8c7f0a01",
    "first_name": "Cara",
    "last_name": "Driver",
    "email": "cara.customer@example.com",
    "phone": "+15550202",
    "user_type": "customer",
    "age": 28,
    "image": "https://cdn.example.com/users/cara-new.jpg",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "created_at": "2026-03-09T12:10:00Z",
    "updated_at": "2026-03-09T12:25:00Z"
  }
}
```

### Error Response (400)
```json
{
  "error": "image file is required"
}
```

## 8) Get All Users (Superuser Only)
`GET /users/getall/`

Required auth:
- Must be logged in (valid Django session cookie)

Only authenticated superusers can access this endpoint.

Supported query parameters:
- `email` (partial match)
- `user_type` (`customer` or `staff`)
- `is_active` (`true` or `false`)
- `page` (default pagination)
- `page_size` (max 100)

### Request Example (JSON-style query object)
```json
{
  "email": "cara",
  "user_type": "customer",
  "is_active": true,
  "page": 1,
  "page_size": 20
}
```

### Request Body
```json
// no request body
```

### Unauthorized Response (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Success Response (200)
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "67c9d7b5f6a2c14d8c7f0a01",
      "first_name": "Cara",
      "last_name": "Driver",
      "email": "cara.customer@example.com",
      "phone": "+15550202",
      "user_type": "customer",
      "age": 28,
      "image": "https://cdn.example.com/users/cara.jpg",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2026-03-09T12:10:00Z",
      "updated_at": "2026-03-09T12:10:00Z"
    }
  ]
}
```

### GetAll cURL Example
```bash
curl -X GET "http://localhost:8000/users/getall/?user_type=customer&page=1&page_size=20" \
  -b cookies.txt
```

## 9) Delete User
`DELETE /users/delete/<user_id>/`

Required auth:
- Must be logged in (valid Django session cookie)
- Superuser can delete any user
- Normal user can only delete own account

Default behavior:
- Soft delete (deactivate): `is_active` set to `false`

Hard delete behavior:
- Superuser only, use `?hard=true`
- User record is removed and image is deleted from S3/Spaces

### Request Example (Soft Delete)
```json
{
  "user_id": "67c9d7b5f6a2c14d8c7f0a01",
  "hard": false
}
```

### Request Example (Hard Delete)
```json
{
  "user_id": "67c9d7b5f6a2c14d8c7f0a01",
  "hard": true
}
```

### Request Body
```json
// no request body
```

### Success Response (200)
```json
{
  "message": "User deactivated successfully"
}
```

### Hard Delete Success Response (200)
```json
{
  "message": "User hard-deleted successfully"
}
```

### Error Response (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Quick Test Checklist
1. Create customer with `POST /users/create/`.
2. Login with `POST /users/login/` and keep session cookie.
3. Call `GET /users/info/` and verify profile + photo.
4. Call `PUT /users/update/` with image and verify old image is replaced in S3.
5. Call `PUT /users/update-photo/` and verify photo changes in response.
6. Call `POST /users/change-password/` and verify forced re-login.
7. Call `GET /users/getall/` as non-superuser and expect 403.
8. Login as superuser and call `GET /users/getall/?is_active=true` and expect paginated 200.
9. Call `DELETE /users/delete/<user_id>/` (soft delete), verify `is_active=false`.
10. Call `DELETE /users/delete/<user_id>/?hard=true` as superuser, verify DB + S3 delete.
11. Logout with `POST /users/logout/` and verify session is cleared.


