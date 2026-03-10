# Auto Spare Parts API - Validation First Documentation

## Validation First Execution Rule
Every create/update endpoint follows this strict order:
1. Validate request data with serializer methods.
2. Return descriptive validation error if invalid.
3. Upload image(s) if request includes files.
4. Create or update MongoEngine document.
5. Return success JSON.

No image upload and no database write occurs before validation passes.

## Standard Response Format
Success:
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {}
}
```

Error:
```json
{
  "success": false,
  "error": "Invalid image format"
}
```

## JWT Token Structure
This API uses stateless JWT (JSON Web Token) authentication. Tokens are signed using HS256 algorithm.

### Access Token Payload
Used for authenticating API requests. Include in `Authorization: Bearer <access_token>` header.

```json
{
  "sub": "<user_id>",
  "role": "customer|staff|admin",
  "type": "access",
  "iat": 1234567890,
  "exp": 1234571490
}
```

**Fields:**
- `sub`: MongoDB ObjectId of the user (string)
- `role`: User's role - `customer`, `staff`, or `admin`
- `type`: Token type - always `"access"` for access tokens
- `iat`: Issued at timestamp (Unix epoch seconds)
- `exp`: Expiration timestamp (Unix epoch seconds)

**Expiration:** Configurable via `JWT_ACCESS_TOKEN_MINUTES` in settings (default: 60 minutes)

### Refresh Token Payload
Used to obtain new access tokens without re-login. Send to `/api/auth/refresh/` endpoint.

```json
{
  "sub": "<user_id>",
  "role": "customer|staff|admin",
  "type": "refresh",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**Fields:**
- `sub`: MongoDB ObjectId of the user (string)
- `role`: User's role - `customer`, `staff`, or `admin`
- `type`: Token type - always `"refresh"` for refresh tokens
- `iat`: Issued at timestamp (Unix epoch seconds)
- `exp`: Expiration timestamp (Unix epoch seconds)

**Expiration:** Configurable via `JWT_REFRESH_TOKEN_DAYS` in settings (default: 7 days)

### Token Usage
1. **Login** → Receive both `access` and `refresh` tokens
2. **API Requests** → Include `Authorization: Bearer <access_token>` header
3. **Token Expired** → Send `refresh` token to `/api/auth/refresh/` to get new `access` token
4. **Logout** → Client deletes both tokens (stateless, no server-side session)

### Error Responses
Expired token:
```json
{
  "success": false,
  "error": "Token expired"
}
```

Invalid token:
```json
{
  "success": false,
  "error": "Invalid token"
}
```

Wrong token type (using refresh token for API request):
```json
{
  "success": false,
  "error": "Invalid access token"
}
```

## Health Endpoint
### GET `/`
```json
{
  "status": "ok",
  "service": "Auto Spare Parts API",
  "database": "connected"
}
```

## Storage
- S3 backend when credentials exist:
  - `DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"`
- Fallback to local media storage when credentials are missing.
- Upload failure response:
```json
{
  "success": false,
  "error": "Image upload failed"
}
```

## Image Validation
- Allowed: `jpg`, `jpeg`, `png`, `webp`
- Max size: `5MB`

Invalid format response:
```json
{
  "success": false,
  "error": "Invalid image format"
}
```

## Mock Data for Postman Testing
Use this exact order for a full working flow.

### Base Variables (Postman Environment)
- `base_url`: `http://127.0.0.1:8000`
- `staff_key`: `Sahal_Saaim_staff_key`
- `admin_key`: `Sahal_Saaim_super_key`
- `customer_email`: `customer1@example.com`
- `staff_email`: `staff1@example.com`
- `admin_email`: `admin1@example.com`
- `default_password`: `Pass1234`

### Reusable Mock Users
### Staff register payload (multipart/form-data)
- `name`: `Staff One`
- `email`: `staff1@example.com`
- `password`: `Pass1234`
- `phone`: `+923001234567`
- `role`: `staff`
- `key`: `<SECRET_KEY_FOR_STAFF_USER>`
- `image`: `<file>`

### Customer register payload (multipart/form-data)
- `name`: `Customer One`
- `email`: `customer1@example.com`
- `password`: `Pass1234`
- `phone`: `+923001234568`
- `role`: `customer`
- `image`: `<file>`

### Admin register payload (multipart/form-data)
- `name`: `Admin One`
- `email`: `admin1@example.com`
- `password`: `Pass1234`
- `phone`: `+923001234569`
- `role`: `admin`
- `key`: `<SECRET_KEY_FOR_ADMIN_USER>`
- `image`: `<file>`

### Login payload (application/json)
```json
{
  "email": "staff1@example.com",
  "password": "Pass1234"
}
```

Expected success:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>",
    "user": {
      "id": "<user_id>",
      "name": "Staff One",
      "email": "staff1@example.com",
      "phone": "+923001234567",
      "image": "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/users/...",
      "role": "staff"
    }
  }
}
```

### Logout payload (No body required)
- Header: `Authorization: Bearer <jwt_access_token>`

Expected success:
```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {
    "message": "Logout successful. Please delete your access and refresh tokens."
  }
}
```

### Car create payload (multipart/form-data)
- `brand`: `BMW`
- `model`: `M3`
- `year`: `2022`
- `vin_number`: `VIN-BMW-M3-2022-001`
- `description`: `Sports sedan`
- `images`: `<file1>`, `<file2>`

Expected success data sample:
```json
{
  "id": "<car_id>",
  "brand": "BMW",
  "model": "M3",
  "year": 2022,
  "vin_number": "VIN-BMW-M3-2022-001",
  "description": "Sports sedan",
  "images": [
    "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/cars/...",
    "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/cars/..."
  ],
  "added_by": "<staff_user_id>"
}
```

### Spare part create payload (multipart/form-data)
- `name`: `Brake Disc`
- `description`: `Used original part`
- `price`: `150`
- `condition`: `used`
- `car_id`: `<car_id from cars endpoint>`
- `images`: `<file1>`, `<file2>`

Expected success data sample:
```json
{
  "id": "<spare_part_id>",
  "name": "Brake Disc",
  "description": "Used original part",
  "price": 150.0,
  "condition": "used",
  "car_id": "<car_id>",
  "images": [
    "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/spares/...",
    "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/spares/..."
  ],
  "added_by": "<staff_user_id>"
}
```

### Order create payload (application/json)
```json
{
  "items": [
    {
      "spare_part_id": "<spare_part_id>",
      "quantity": 2
    }
  ]
}
```

Expected success data sample:
```json
{
  "id": "<order_id>",
  "customer": "<customer_id>",
  "items": [
    {
      "spare_part_id": "<spare_part_id>",
      "quantity": 2,
      "price": 150.0,
      "total_price": 300.0
    }
  ],
  "total_price": 300.0,
  "order_status": "pending"
}
```

### Inventory upsert payload (application/json)
```json
{
  "spare_part_id": "<spare_part_id>",
  "quantity": 12
}
```

### Quick Negative Test Mock Data
- Invalid email register:
```json
{
  "name": "Bad Email",
  "email": "invalid-email",
  "password": "Pass1234",
  "phone": "+923001234570",
  "role": "customer"
}
```
- Duplicate email register: reuse `customer1@example.com`
- Invalid image: upload `sample.txt` as `image` or `images`
- Used spare part with bad car id:
```json
{
  "name": "Disc",
  "description": "Used",
  "price": 120,
  "condition": "used",
  "car_id": "507f1f77bcf86cd799439011"
}
```

## Auth Routes
### POST `/api/auth/register/`
- Public
- Supports `multipart/form-data` and `application/json`

Validation:
- `name`, `email`, `password`, `phone` required
- email format validated
- email uniqueness validated
- password min length 8
- phone non-empty

Duplicate email error:
```json
{
  "success": false,
  "error": "User with this email already exists"
}
```

### POST `/api/auth/login/`
- Public

### POST `/api/auth/logout/`
- Authenticated
- Requires: Bearer token in `Authorization` header
- Response confirms logout success. Client must delete stored access and refresh tokens.

### POST `/api/auth/refresh/`
- Public

## Users Routes
### GET `/api/users/profile/`
### GET `/api/users/me/`
- Authenticated
- Returns `image` full URL/path field in response.

### PUT `/api/users/me/`
- Authenticated
- Supports multipart `image`.

### GET `/api/users/`
- Admin only

### GET `/api/users/{user_id}/`
- Admin only

### PATCH `/api/users/{user_id}/`
- Admin only

### DELETE `/api/users/delete/{user_id}/`
- Admin only
- Staff delete staff response:
```json
{
  "success": false,
  "error": "Staff users cannot delete other staff members"
}
```

## Cars Routes
### GET `/api/cars/`
- Public

### POST `/api/cars/`
- Staff/Admin only
- Supports multiple images via `images` files.

Customer permission error:
```json
{
  "success": false,
  "error": "Only staff or admin can create cars"
}
```

### GET `/api/cars/{car_id}/`
- Authenticated

### PUT `/api/cars/{car_id}/`
- Staff/Admin only

### DELETE `/api/cars/{car_id}/`
- Staff/Admin only

Car validation errors:
- `year` must be numeric
- `vin_number` must be unique

## Spare Parts Routes
### GET `/api/spare-parts/`
- Public

### POST `/api/spare-parts/`
- Staff/Admin only
- Supports multiple images via `images` files.

Validation:
- `price` must be positive
- `condition` must be `new` or `used`
- if `condition=used`, valid `car_id` must exist

Used part invalid car example:
```json
{
  "success": false,
  "error": "Invalid car reference"
}
```

### GET `/api/spare-parts/{part_id}/`
- Authenticated

### PUT `/api/spare-parts/{part_id}/`
- Staff/Admin only

### DELETE `/api/spare-parts/{part_id}/`
- Staff/Admin only

## Orders Routes
### GET `/api/orders/`
- Authenticated
- customer sees own orders
- staff/admin see all

### POST `/api/orders/`
- Customer only

Validation:
- customer exists/authenticated
- spare part references valid
- quantity > 0

Quantity error:
```json
{
  "success": false,
  "error": "Quantity must be greater than zero"
}
```

### GET `/api/orders/{order_id}/`
- Authenticated

### PATCH `/api/orders/{order_id}/`
- Staff/Admin

### DELETE `/api/orders/{order_id}/`
- Admin

## Inventory Routes
### GET `/api/inventory/`
### POST `/api/inventory/`
### GET `/api/inventory/{inventory_id}/`
### DELETE `/api/inventory/{inventory_id}/`
- Staff/Admin only

## Global Exception Handling
Unhandled errors return:
```json
{
  "success": false,
  "error": "Internal server error"
}
```

## Error Logging
All API errors are logged to:
- `logs/app.log`

Each log entry includes:
- timestamp
- endpoint
- method
- user id
- HTTP status
- error message
