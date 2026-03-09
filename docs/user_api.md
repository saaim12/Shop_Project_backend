# User API Reference

Base URL:
- `/users/`

All routes are included in `config/urls.py` via:
- `path("users/", include("apps.users.urls"))`

## Response Contract

Success shape:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

Error shape:

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "email": [
      "Email is required"
    ]
  }
}
```

Notes:
- `data` may be omitted for operations like logout/delete.
- `field_errors` appears for validation-style errors.
- DRF auth/permission errors are also normalized to this shape via custom exception handler.

## Route Support

Both styles are supported for all endpoints:
- with trailing slash: `/users/login/`
- without trailing slash: `/users/login`

## Endpoints
- `POST /users/create`
- `POST /users/login`
- `POST /users/logout`
- `GET /users/info`
- `PUT /users/update`
- `PUT /users/update-photo`
- `POST /users/change-password`
- `GET /users/getall`
- `GET /users/category/<category>`
- `DELETE /users/delete/<user_id>`

Compatibility aliases:
- `GET /users/all`
- `GET /users/by-category/<category>`

## Authentication

This project uses Django session auth.

Login flow:
1. Call `POST /users/login`.
2. Save cookie jar (`sessionid`, and CSRF if needed).
3. Use cookie jar for protected endpoints.
4. Call `POST /users/logout`.

Postman tips:
- Use a cookie jar (Postman handles this automatically).
- For unsafe methods with session auth, send `X-CSRFToken` when CSRF is enforced.

## Global Validation Rules
- `user_type`: `customer` or `staff`.
- `age`: at least `18`.
- `phone`: `^\+?[0-9]{7,15}$`.
- Password: minimum 8 chars, must include letters and numbers.
- Staff creation requires `key=SECRET_KEY_FOR_STAFF_USER`.
- Superuser creation requires `is_superuser=true` and `key=SECRET_KEY_FOR_ADMIN_USER`.

## 1) Create User
`POST /users/create`

Accepted content types:
- `application/json`
- `multipart/form-data` (for `image`)

Body fields:
- `first_name` (required)
- `last_name` (required)
- `email` (required, unique)
- `password` (required)
- `phone` (required)
- `age` (required)
- `user_type` (optional, default `customer`)
- `image` (optional file)
- `key` (required for `staff` and superuser creation)
- `is_superuser` (optional bool)

Example request:

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

Success (201):

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "...",
    "email": "cara.customer@example.com",
    "user_type": "customer"
  }
}
```

## 2) Login
`POST /users/login`

Request:

```json
{
  "email": "cara.customer@example.com",
  "password": "CustomerPass123"
}
```

Success (200):

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "photo": null,
    "user": {
      "id": "...",
      "email": "cara.customer@example.com"
    }
  }
}
```

Credential error (401):

```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

## 3) Logout
`POST /users/logout`

Requires authenticated session.

Success (200):

```json
{
  "success": true,
  "message": "Logout successful"
}
```

## 4) Logged-In User Info
`GET /users/info`

Requires authenticated session.

Success (200):

```json
{
  "success": true,
  "message": "User info fetched successfully",
  "data": {
    "photo": "https://...",
    "user": {
      "id": "...",
      "email": "..."
    }
  }
}
```

## 5) Update Profile
`PUT /users/update`

Requires authenticated session.

Accepted fields:
- `first_name`
- `last_name`
- `phone`
- `age`

Success (200):

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "photo": "https://...",
    "user": {
      "id": "..."
    }
  }
}
```

## 6) Update Photo
`PUT /users/update-photo`

Requires authenticated session.

Request type:
- `multipart/form-data`
- required file field: `image`

Example error (400):

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "image": [
      "Image file is required"
    ]
  }
}
```

## 7) Change Password
`POST /users/change-password`

Requires authenticated session.

Request:

```json
{
  "old_password": "CustomerPass123",
  "new_password": "CustomerPass456"
}
```

Success (200):

```json
{
  "success": true,
  "message": "Password changed successfully. Please login again."
}
```

After success, user is logged out.

## 8) Get All Users (Superuser Only)
`GET /users/getall`

Requires authenticated superuser.

Query params:
- `email` (contains)
- `user_type` (`customer` or `staff`)
- `is_active` (`true|false|1|0|yes|no`)
- `page`
- `page_size`

Success (200):

```json
{
  "success": true,
  "message": "Users fetched successfully",
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "...",
        "email": "..."
      }
    ]
  }
}
```

## 9) Get Users By Category (Superuser Only)
`GET /users/category/<category>`

Alias:
- `GET /users/by-category/<category>`

Valid values:
- `customers`
- `customer`
- `staff`

Success (200):
- same response envelope as `getall` (`success/message/data` with paginated payload).

## 10) Delete User
`DELETE /users/delete/<user_id>`

Requires authenticated user.

Permissions:
- Superuser can delete any account.
- Normal user can delete only own account.

Behavior:
- default: soft delete (`is_active=false`)
- hard delete: `?hard=true` (superuser only)

Success (200):

```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

Hard delete success (200):

```json
{
  "success": true,
  "message": "User hard-deleted successfully"
}
```

## Postman Quick Flow
1. `POST /users/create`
2. `POST /users/login`
3. `GET /users/info`
4. `PUT /users/update`
5. `PUT /users/update-photo`
6. `POST /users/change-password` (logs out)
7. `POST /users/login` (new password)
8. As superuser: `GET /users/getall`
9. As superuser: `GET /users/category/customers`
10. `DELETE /users/delete/<user_id>`


