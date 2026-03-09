# User API Reference

Base URL:
- `/users/`

All routes are included from `config/urls.py` via `path("users/", include("apps.users.urls"))`.

## Endpoints
- `POST /users/create/`
- `GET /users/getall/`
- `GET /users/category/<category>/`
- `GET /users/info/`
- `PUT /users/update/`
- `PUT /users/update-photo/`
- `POST /users/change-password/`
- `POST /users/login/`
- `POST /users/logout/`
- `DELETE /users/delete/<user_id>/`

Compatibility aliases:
- `GET /users/all/` -> same as `GET /users/getall/`
- `GET /users/by-category/<category>/` -> same as `GET /users/category/<category>/`

## Authentication
This project uses Django session authentication.

Login flow:
1. `POST /users/login/` with email/password.
2. Browser stores `sessionid` cookie.
3. Protected endpoints use that cookie automatically.
4. `POST /users/logout/` to invalidate the session.

Notes:
- In browser-based frontend calls, use `credentials: "include"`.
- For unsafe methods (`POST`, `PUT`, `DELETE`) with session auth, include CSRF token.
- Unauthorized/forbidden errors produced by DRF permissions still use `{"detail": "..."}`.

## Standard Error Shape (View-Level)
User view validation/business errors are returned as:

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "email": [
      "A user with this email already exists."
    ]
  }
}
```

Possible keys:
- `success`: always `false` on these errors.
- `message`: high-level message.
- `field_errors`: optional field-level details.

## Global Rules
- `user_type`: `customer` or `staff`.
- `age`: must be `>= 18`.
- `phone`: must match `^\+?[0-9]{7,15}$`.
- Password must be at least 8 characters and contain both letters and numbers.
- Staff creation requires `key=SECRET_KEY_FOR_STAFF_USER`.
- Superuser creation requires `is_superuser=true` and `key=SECRET_KEY_FOR_ADMIN_USER`.

## 1) Create User
`POST /users/create/`

Content types:
- `application/json`
- `multipart/form-data` (if uploading `image`)

Body fields:
- `first_name` (required)
- `last_name` (required)
- `email` (required, unique)
- `password` (required)
- `phone` (required)
- `age` (required)
- `user_type` (optional, default `customer`)
- `image` (optional file)
- `key` (required for staff/superuser creation)
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

Success (201): returns full user object.

Example error (400):

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "email": [
      "A user with this email already exists."
    ]
  }
}
```

## 2) Login
`POST /users/login/`

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
  "message": "Login successful",
  "photo": null,
  "user": {
    "id": "...",
    "email": "cara.customer@example.com"
  }
}
```

Validation error (400):

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

Credential error (401):

```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

## 3) Logout
`POST /users/logout/`

Requires authenticated session.

Success (200):

```json
{
  "message": "Logout successful"
}
```

## 4) Logged-In User Info
`GET /users/info/`

Requires authenticated session.

Success (200):

```json
{
  "photo": "https://...",
  "user": {
    "id": "...",
    "email": "..."
  }
}
```

## 5) Update Profile
`PUT /users/update/`

Requires authenticated session.

Accepted fields:
- `first_name`
- `last_name`
- `phone`
- `age`

Success (200):

```json
{
  "message": "Profile updated successfully",
  "photo": "https://...",
  "user": {
    "id": "..."
  }
}
```

Validation error (400): standardized error shape.

## 6) Update Photo
`PUT /users/update-photo/`

Requires authenticated session.

Request type:
- `multipart/form-data`
- required file field: `image`

Missing image (400):

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
`POST /users/change-password/`

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
  "message": "Password changed successfully. Please login again."
}
```

After success, user is logged out.

## 8) Get All Users (Superuser Only)
`GET /users/getall/`

Requires authenticated superuser.

Query params:
- `email` (contains)
- `user_type` (`customer` or `staff`)
- `is_active` (`true|false|1|0|yes|no`)
- `page`
- `page_size`

Success (200): paginated response:

```json
{
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
```

Validation error example (400):

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "user_type": [
      "Use 'customer' or 'staff'"
    ]
  }
}
```

## 9) Get Users By Category (Superuser Only)
`GET /users/category/<category>/`

Alias:
- `GET /users/by-category/<category>/`

Valid categories:
- `customers`
- `customer`
- `staff`

Invalid category (400):

```json
{
  "success": false,
  "message": "Validation failed",
  "field_errors": {
    "category": [
      "Use 'customers' or 'staff'"
    ]
  }
}
```

## 10) Delete User
`DELETE /users/delete/<user_id>/`

Requires authenticated user.

Permissions:
- Superuser can delete any account.
- Normal user can delete only own account.

Behavior:
- Default: soft delete (`is_active=false`).
- Hard delete: `?hard=true` and requester must be superuser.

Success (soft delete, 200):

```json
{
  "message": "User deactivated successfully"
}
```

Success (hard delete, 200):

```json
{
  "message": "User hard-deleted successfully"
}
```

## Quick Test Flow
1. `POST /users/create/` create a customer.
2. `POST /users/login/`.
3. `GET /users/info/`.
4. `PUT /users/update/`.
5. `PUT /users/update-photo/`.
6. `POST /users/change-password/` (forces logout).
7. `POST /users/login/` with new password.
8. As superuser: `GET /users/getall/`.
9. As superuser: `GET /users/category/customers/`.
10. `DELETE /users/delete/<user_id>/`.


