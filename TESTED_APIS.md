# Garage Backend API Documentation

## 1) Base Server URL

The backend service can be verified using:

- Base URL: `http://127.0.0.1:8000`

### Health Check Example Response

```json
{
  "status": "ok",
  "service": "Garage Backend fully active",
  "database": "Mongo DB is connected",
  "debug": true
}
```

This confirms:

- Backend server is running
- MongoDB connection is active
- Debug mode is enabled

---

## 2) Role-Based Access Control

The system uses three roles:

- Customer
- Staff
- Admin

Each role has different permissions.

### 2.1 Customer Permissions

Customers can:

- Create orders
- View available cars
- View spare parts

Customers cannot:

- Create cars
- Delete cars
- Create spare parts
- Delete spare parts
- Update inventory

### 2.2 Staff Permissions

Staff users require Bearer token authentication for protected operations.

Staff can:

- Create cars
- Delete cars
- Create spare parts
- Delete spare parts
- Update inventory quantities

### 2.3 Admin Permissions

Admin users have full system access.

Admins can:

- Perform all staff actions
- Update order status
- Update inventory
- Create staff users
- Delete any user

---

## 3) Authentication Overview

Authentication uses JWT.

On login, two tokens are returned:

- Access token
- Refresh token

Use access token in protected routes:

`Authorization: Bearer <ACCESS_TOKEN>`

---

## 4) User Registration

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/register/`
- Content-Type: `multipart/form-data` (or JSON without image)

### Required Fields

| Field | Description |
|---|---|
| `name` | User full name |
| `email` | User email |
| `password` | User password |
| `phone` | Phone number |
| `role` | `customer` / `staff` / `admin` |

### Optional Fields

| Field | Description |
|---|---|
| `image` | Profile image file |
| `key` | Required only for `staff` and `admin` |

### Example (Form Data)

- `name`: `saim`
- `email`: `saim@gmail.com`
- `password`: `pass1234`
- `phone`: `+923249923289`
- `image`: `(file)`
- `role`: `customer`

### Example Response

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "69b1c71afddc87d6e27760c6",
    "name": "saim",
    "email": "saim@gmail.com",
    "phone": "+923249923289",
    "image": "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/users/ea6e6f86-879d-4a6c-9ce3-d0f49465de33_customer_one.jpeg",
    "role": "customer",
    "created_at": "2026-03-11T19:48:42.156328"
  }
}
```

---

## 5) Special Registration Keys

When creating staff/admin users, provide `key`.

| Role | Secret Key |
|---|---|
| Staff | `Sahal_saim_staff_key` |
| Admin | `Sahal_saim_admin_key` |

Customers do not require a key.

---

## 6) User Login

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/login/`
- Content-Type: `application/json`

### Request Body

```json
{
  "email": "aameranees@gmail.com",
  "password": "pass1234"
}
```

### Response

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "ACCESS_TOKEN",
    "refresh": "REFRESH_TOKEN",
    "user": {
      "id": "69b1c923fddc87d6e27760c9",
      "name": "amer anees",
      "email": "aameranees@gmail.com",
      "phone": "+4528881837",
      "image": "image_url",
      "role": "admin",
      "created_at": "2026-03-11T19:57:22.917000"
    }
  }
}
```

---

## 7) User Logout

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/logout/`
- Auth: Bearer token required

### Response

```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {
    "message": "Logout successful. Please delete your access and refresh tokens."
  }
}
```

---

## 8) Refresh Access Token

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/refresh/`
- Content-Type: `application/json`

### Request

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

### Response

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access": "NEW_ACCESS_TOKEN"
  }
}
```

---

## 9) Get Logged-In User Profile

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/users/profile/`
- Auth: Bearer token required

### Response

```json
{
  "success": true,
  "message": "Profile fetched successfully",
  "data": {
    "id": "69b1c974fddc87d6e27760ca",
    "name": "david",
    "email": "david.234@gmail.com",
    "phone": "+4528881546",
    "image": "image_url",
    "role": "staff",
    "created_at": "2026-03-11T19:58:44.252000"
  }
}
```

---

## 10) Update User Profile

- Method: `PUT`
- URL: `http://127.0.0.1:8000/api/users/profile/`
- Auth: Bearer token required
- Content-Type: `multipart/form-data` or `application/json`

Supported fields include:

- `name`
- `email`
- `phone`
- `image`
- `old_password` + `new_password` (for password change)

### Password Update Example

- `old_password`: `current_password`
- `new_password`: `new_password`

---

## 11) Delete User

- Method: `DELETE`
- URL: `http://127.0.0.1:8000/api/users/deleting/{user_id}/`
- Auth: Bearer token required

Rule summary:

- Admin can delete any user
- Non-admin users can delete only their own account

---

## 12) Admin-Only User Endpoints

### Get All Users

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/users/getall`
- Auth: Admin Bearer token

### Get Specific User by ID

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/users/{user_id}/`
- Auth: Admin Bearer token

---

## 13) Important Security Rules

- Admin can view any user
- Admin can delete any user
- Staff cannot manage user accounts
- Customers cannot access admin-only endpoints
- All protected routes require a valid Bearer token

---

# Spare Parts APIs

## 1) Get All Spare Parts

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/spare-parts/`
- Auth: Not required (public)

## 2) Create Spare Part

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/spare-parts/`
- Auth: Bearer token (`staff` or `admin` only)
- Content-Type: `multipart/form-data` (for images) or JSON

### Fields

- `name`
- `description`
- `price`
- `quantity`
- `category`
- `condition`
- `car_id` (required when `condition` is `used`)
- `images` (optional, multiple)

## 3) Update Spare Part

- Method: `PATCH`
- URL: `http://127.0.0.1:8000/api/spare-parts/{spare_part_id}/`
- Auth: Bearer token (`staff` or `admin` only)

Updatable fields:

- `name`
- `description`
- `category`
- `price`
- `quantity`
- `condition`
- `car_id`
- `images` (if sent in multipart patch, new images are appended)

## 4) Delete Single Spare Part Image

- Method: `DELETE`
- URL: `http://127.0.0.1:8000/api/spare-parts/{spare_part_id}/images/`
- Auth: Bearer token (`staff` or `admin` only)

### Body

```json
{
  "image_url": "IMAGE_URL"
}
```

## 5) Delete All Spare Part Images

- Method: `DELETE`
- URL: `http://127.0.0.1:8000/api/spare-parts/{spare_part_id}/images/`
- Auth: Bearer token (`staff` or `admin` only)

### Body

```json
{
  "delete_all": true
}
```

## 6) Delete Spare Part

- Method: `DELETE`
- URL: `http://127.0.0.1:8000/api/spare-parts/{spare_part_id}/`
- Auth: Bearer token (`staff` or `admin` only)

On delete, related spare-part images are also deleted from storage.

### Response

```json
{
  "success": true,
  "message": "Spare part deleted successfully",
  "data": {
    "deleted": true
  }
}
```
