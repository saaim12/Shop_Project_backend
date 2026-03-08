# User API Reference

Base URL: `/api/v1/users/`

## General Rules
- Send JSON with `Content-Type: application/json`. Use `multipart/form-data` only when uploading an `image` file (field name: `image`).
- All requests require `first_name`, `last_name`, `email`, `password`, `phone`, and `age`.
- Validation summary:
  - Email must be unique and will be normalized to lowercase.
  - Password must be at least 8 characters and contain both letters and numbers.
  - Age must be an integer ≥ 18.
  - Phone must contain 7-15 digits and may start with `+`.
- `user_type` defaults to `customer` if omitted. Allowed values: `customer`, `staff`.
- `image` is optional; supply a file if needed. The response always returns the hosted URL.

## Secrets
Keep the following values private. They are required for privileged creations:
- `SECRET_KEY_FOR_STAFF_USER`
- `SECRET_KEY_FOR_ADMIN_USER`

## 1. Create User (Customer / Staff / Superuser)
`POST /api/v1/users/`

### Request Body Fields
| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `first_name` | string | Yes | Max 150 chars |
| `last_name` | string | Yes | Max 150 chars |
| `email` | string | Yes | Must be unique |
| `password` | string | Yes | ≥8 chars, letters & numbers |
| `phone` | string | Yes | 7-15 digits, may start with `+` |
| `age` | integer | Yes | ≥18 |
| `user_type` | string | Optional | `customer` (default) or `staff` |
| `image` | file | Optional | Use multipart upload |
| `key` | string | Conditional | Required for staff + superuser |
| `is_superuser` | boolean | Conditional | Only true for superuser creation |

### Create Customer Example
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

### Create Staff Example
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

### Create Superuser Example
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

### Successful Response
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

### Error Examples
Duplicate email:
```json
{
  "email": ["A user with this email already exists."]
}
```

Invalid staff/superuser key:
```json
{
  "error": "Invalid key for superuser creation"
}
```

Validation failure (age):
```json
{
  "age": ["Age must be 18 or older."]
}
```

## 2. List All Users (Admin Only)
`POST /api/v1/users/all/`

### Request Body
```json
{
  "key": "<SECRET_KEY_FOR_ADMIN_USER>"
}
```

### Response
```json
[
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
  },
  {
    "id": "67c9d7b5f6a2c14d8c7f0a02",
    "first_name": "Ben",
    "last_name": "Service",
    "email": "ben.staff@example.com",
    "phone": "+15550101",
    "user_type": "staff",
    "age": 32,
    "image": "https://cdn.example.com/users/ben.jpg",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false,
    "created_at": "2026-03-09T10:00:00Z",
    "updated_at": "2026-03-09T11:05:00Z"
  }
]
```

Unauthorized key response:
```json
{
  "error": "Only superuser can view all users"
}
```

## Testing Checklist
1. Create customer without key → expect 201.
2. Repeat same email → expect 400 duplicate email error.
3. Create staff with wrong key → expect 403.
4. Create superuser with valid key + all required fields → expect 201.
5. Call `/api/v1/users/all/` with admin key → expect list of users.
6. Call `/api/v1/users/all/` with bad key → expect 403 error.
