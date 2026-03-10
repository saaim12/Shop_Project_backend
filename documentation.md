# Auto Spare Parts API Documentation

Base URL

```text
http://127.0.0.1:8000/api
```

Authentication header format

```text
Authorization: Bearer <ACCESS_TOKEN>
```

## FULL API FLOW EXAMPLE

### Step 1 Register Admin

Endpoint

```text
POST /api/auth/register/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "name": "Admin One",
  "email": "admin@example.com",
  "password": "Pass1234",
  "phone": "+923001234567",
  "role": "admin",
  "key": "ADMIN_SECRET_KEY"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "USER_ID",
    "name": "Admin One",
    "email": "admin@example.com",
    "phone": "+923001234567",
    "image": "",
    "role": "admin",
    "created_at": "2026-03-10T10:00:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Invalid admin key"
}
```

Permission rules

```text
Public endpoint
```

### Step 2 Login Admin

Endpoint

```text
POST /api/auth/login/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "email": "admin@example.com",
  "password": "Pass1234"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "ACCESS_TOKEN",
    "refresh": "REFRESH_TOKEN",
    "user": {
      "id": "USER_ID",
      "name": "Admin One",
      "email": "admin@example.com",
      "phone": "+923001234567",
      "image": "",
      "role": "admin",
      "created_at": "2026-03-10T10:00:00"
    }
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

Permission rules

```text
Public endpoint
```

### Step 3 Create Staff User

Endpoint

```text
POST /api/auth/register/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "name": "Staff One",
  "email": "staff@example.com",
  "password": "Pass1234",
  "phone": "+923001234568",
  "role": "staff",
  "key": "STAFF_SECRET_KEY"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "STAFF_ID",
    "name": "Staff One",
    "email": "staff@example.com",
    "phone": "+923001234568",
    "image": "",
    "role": "staff",
    "created_at": "2026-03-10T10:01:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Invalid staff key"
}
```

Permission rules

```text
Public endpoint (current implementation)
```

### Step 4 Login Staff

Endpoint

```text
POST /api/auth/login/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "email": "staff@example.com",
  "password": "Pass1234"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "STAFF_ACCESS_TOKEN",
    "refresh": "STAFF_REFRESH_TOKEN",
    "user": {
      "id": "STAFF_ID",
      "name": "Staff One",
      "email": "staff@example.com",
      "phone": "+923001234568",
      "image": "",
      "role": "staff",
      "created_at": "2026-03-10T10:01:00"
    }
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

Permission rules

```text
Public endpoint
```

### Step 5 Create Car

Endpoint

```text
POST /api/cars/create/
```

Required headers

```json
{
  "Authorization": "Bearer STAFF_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "number_plate": "ABC123",
  "color": "Red",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2018
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Car created successfully",
  "data": {
    "id": "CAR_ID",
    "number_plate": "ABC123",
    "color": "Red",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "created_by": "STAFF_ID",
    "created_at": "2026-03-10T10:02:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can create cars"
}
```

Permission rules

```text
staff, admin
```

### Step 6 Create Spare Part

Endpoint

```text
POST /api/spare-parts/
```

Required headers

```json
{
  "Authorization": "Bearer STAFF_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "name": "Brake Disc",
  "description": "Original used part",
  "price": 150,
  "condition": "used",
  "car_id": "CAR_ID"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Spare part created successfully",
  "data": {
    "id": "PART_ID",
    "name": "Brake Disc",
    "description": "Original used part",
    "price": 150,
    "condition": "used",
    "images": [],
    "car_id": "CAR_ID",
    "created_by": "STAFF_ID",
    "created_at": "2026-03-10T10:03:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Used spare parts must reference a car"
}
```

Permission rules

```text
staff, admin
```

### Step 7 Add Inventory

Endpoint

```text
PATCH /api/inventory/INVENTORY_ID/
```

Required headers

```json
{
  "Authorization": "Bearer STAFF_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "quantity": 12
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Inventory updated successfully",
  "data": {
    "id": "INVENTORY_ID",
    "spare_part_id": "PART_ID",
    "spare_part_name": "Brake Disc",
    "quantity": 12,
    "updated_by": "STAFF_ID",
    "updated_at": "2026-03-10T10:04:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can update inventory"
}
```

Permission rules

```text
staff, admin
```

### Step 8 Register Customer

Endpoint

```text
POST /api/auth/register/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "name": "Customer One",
  "email": "customer@example.com",
  "password": "Pass1234",
  "phone": "+923001234569",
  "role": "customer"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "CUSTOMER_ID",
    "name": "Customer One",
    "email": "customer@example.com",
    "phone": "+923001234569",
    "image": "",
    "role": "customer",
    "created_at": "2026-03-10T10:05:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "User with this email already exists"
}
```

Permission rules

```text
Public endpoint
```

### Step 9 Login Customer

Endpoint

```text
POST /api/auth/login/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "email": "customer@example.com",
  "password": "Pass1234"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "CUSTOMER_ACCESS_TOKEN",
    "refresh": "CUSTOMER_REFRESH_TOKEN",
    "user": {
      "id": "CUSTOMER_ID",
      "name": "Customer One",
      "email": "customer@example.com",
      "phone": "+923001234569",
      "image": "",
      "role": "customer",
      "created_at": "2026-03-10T10:05:00"
    }
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

Permission rules

```text
Public endpoint
```

### Step 10 Create Order

Endpoint

```text
POST /api/orders/
```

Required headers

```json
{
  "Authorization": "Bearer CUSTOMER_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "spare_part_ids": [
    "PART_ID"
  ]
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "id": "ORDER_ID",
    "customer_id": "CUSTOMER_ID",
    "spare_parts": [
      {
        "id": "PART_ID",
        "name": "Brake Disc",
        "price": 150
      }
    ],
    "total_price": 150,
    "status": "pending",
    "created_at": "2026-03-10T10:06:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Only customers can place orders"
}
```

Permission rules

```text
customer
```

### Step 11 Staff Updates Order Status

Endpoint

```text
PATCH /api/orders/ORDER_ID/
```

Required headers

```json
{
  "Authorization": "Bearer STAFF_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Request JSON

```json
{
  "status": "confirmed"
}
```

Success response JSON

```json
{
  "success": true,
  "message": "Order updated successfully",
  "data": {
    "id": "ORDER_ID",
    "customer_id": "CUSTOMER_ID",
    "spare_parts": [
      {
        "id": "PART_ID",
        "name": "Brake Disc",
        "price": 150
      }
    ],
    "total_price": 150,
    "status": "confirmed",
    "created_at": "2026-03-10T10:06:00"
  }
}
```

Error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can update order status"
}
```

Permission rules

```text
staff, admin
```

## ALL ENDPOINTS

### Auth endpoints

#### 1) Register User

Endpoint URL

```text
POST /api/auth/register/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "name": "User One",
  "email": "user@example.com",
  "password": "Pass1234",
  "phone": "+923001111111",
  "role": "customer"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "USER_ID",
    "name": "User One",
    "email": "user@example.com",
    "phone": "+923001111111",
    "image": "",
    "role": "customer",
    "created_at": "2026-03-10T10:00:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Email address is not valid"
}
```

Permission rules

```text
Public endpoint
```

#### 2) Login

Endpoint URL

```text
POST /api/auth/login/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "email": "user@example.com",
  "password": "Pass1234"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "ACCESS_TOKEN",
    "refresh": "REFRESH_TOKEN",
    "user": {
      "id": "USER_ID",
      "name": "User One",
      "email": "user@example.com",
      "phone": "+923001111111",
      "image": "",
      "role": "customer",
      "created_at": "2026-03-10T10:00:00"
    }
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

Permission rules

```text
Public endpoint
```

#### 3) Refresh Token

Endpoint URL

```text
POST /api/auth/refresh/
```

Required headers

```json
{
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access": "NEW_ACCESS_TOKEN"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Invalid token"
}
```

Permission rules

```text
Public endpoint
```

#### 4) Logout

Endpoint URL

```text
POST /api/auth/logout/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {
    "message": "Logout successful. Please delete your access and refresh tokens."
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

Permission rules

```text
Authenticated users
```

### Cars endpoints

#### 1) Create Car

Endpoint URL

```text
POST /api/cars/create/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json or multipart/form-data"
}
```

Example request JSON

```json
{
  "number_plate": "ABC123",
  "color": "Red",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2018
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Car created successfully",
  "data": {
    "id": "CAR_ID",
    "number_plate": "ABC123",
    "color": "Red",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "images": [],
    "created_by": "USER_ID",
    "created_at": "2026-03-10T10:02:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can create cars"
}
```

Duplicate validation errors

```json
{
  "success": false,
  "error": "Number plate already exists"
}
```

```json
{
  "success": false,
  "error": "A car with the same brand, model, and year already exists"
}
```

Permission rules

```text
staff, admin
```

#### 2) List Cars

Endpoint URL

```text
GET /api/cars/get-all/
```

Required headers

```json
{}
```

Pagination query params

```text
page, page_size
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Cars fetched successfully",
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "CAR_ID",
        "number_plate": "ABC123",
        "color": "Red",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2018,
        "created_by": "USER_ID",
        "created_at": "2026-03-10T10:02:00"
      }
    ]
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Invalid page."
}
```

Permission rules

```text
Public endpoint
```

#### 3) Get Car By ID

Endpoint URL

```text
GET /api/cars/CAR_ID/
```

Required headers

```json
{}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Car fetched successfully",
  "data": {
    "id": "CAR_ID",
    "number_plate": "ABC123",
    "color": "Red",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "images": [
      "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/cars/example.jpg"
    ],
    "created_by": "USER_ID",
    "created_at": "2026-03-10T10:02:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Car not found"
}
```

Permission rules

```text
Public endpoint
```

#### 4) Update Car

Endpoint URL

```text
PATCH /api/cars/CAR_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "color": "Black"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Car updated successfully",
  "data": {
    "id": "CAR_ID",
    "number_plate": "ABC123",
    "color": "Black",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "images": [],
    "created_by": "USER_ID",
    "created_at": "2026-03-10T10:02:00"
  }
}
```

Permission rules

```text
staff, admin
```

#### 5) Delete Car

Endpoint URL

```text
DELETE /api/cars/CAR_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Car deleted successfully",
  "data": {
    "deleted": true
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can delete cars"
}
```

Permission rules

```text
staff, admin
```

#### 6) Add Car Images

Endpoint URL

```text
POST /api/cars/CAR_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "multipart/form-data"
}
```

Example form-data

```text
images: file1.jpg
images: file2.jpg
```

Permission rules

```text
staff, admin
```

#### 7) Delete One Car Image

Endpoint URL

```text
DELETE /api/cars/CAR_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "image_url": "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/cars/example.jpg"
}
```

Permission rules

```text
staff, admin
```

#### 8) Delete All Car Images

Endpoint URL

```text
DELETE /api/cars/CAR_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "delete_all": true
}
```

Permission rules

```text
staff, admin
```

### Users endpoints

#### 1) List Users For Admin Dashboard

Endpoint URL

```text
GET /api/users/getall?role=all
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Available query params

```text
role=all | customer | staff | admin
group_by_role=true
```

Example success response JSON

```json
{
  "success": true,
  "message": "Users fetched successfully",
  "data": {
    "admin": [],
    "staff": [],
    "customer": []
  }
}
```

Permission rules

```text
admin only
```

### Spare parts endpoints

#### 1) Spare Part Create Data

Endpoint URL

```text
GET /api/spare-parts/create-data/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Spare part create data fetched successfully",
  "data": {
    "conditions": ["new", "used", "external"],
    "cars": [
      {
        "id": "CAR_ID",
        "number_plate": "ABC123",
        "brand": "Toyota",
        "model": "Corolla"
      }
    ],
    "defaults": {
      "quantity": 1
    }
  }
}
```

Permission rules

```text
staff, admin
```

#### 2) Create Spare Part

Endpoint URL

```text
POST /api/spare-parts/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json or multipart/form-data"
}
```

Example request JSON

```json
{
  "name": "Headlight",
  "description": "Original used part",
  "price": 120.5,
  "quantity": 3,
  "condition": "used",
  "car_id": "CAR_ID"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Spare part created successfully",
  "data": {
    "id": "PART_ID",
    "name": "Headlight",
    "description": "Original used part",
    "price": 120.5,
    "quantity": 3,
    "condition": "used",
    "images": [],
    "car_id": "CAR_ID",
    "created_by": "USER_ID",
    "created_at": "2026-03-10T10:03:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "New or external parts cannot reference a car"
}
```

Permission rules

```text
staff, admin
```

#### 3) List Spare Parts

Endpoint URL

```text
GET /api/spare-parts/
```

Required headers

```json
{}
```

Pagination query params

```text
page, page_size, condition
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Spare parts fetched successfully",
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "PART_ID",
        "name": "Headlight",
        "description": "Original used part",
        "price": 120.5,
        "quantity": 3,
        "condition": "used",
        "images": [],
        "car_id": "CAR_ID",
        "created_by": "USER_ID",
        "created_at": "2026-03-10T10:03:00"
      }
    ]
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Invalid page."
}
```

Permission rules

```text
Public endpoint
```

#### 4) Get Spare Part By ID

Endpoint URL

```text
GET /api/spare-parts/PART_ID/
```

Required headers

```json
{}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Spare part fetched successfully",
  "data": {
    "id": "PART_ID",
    "name": "Headlight",
    "description": "Original used part",
    "price": 120.5,
    "quantity": 3,
    "condition": "used",
    "images": [],
    "car_id": "CAR_ID",
    "created_by": "USER_ID",
    "created_at": "2026-03-10T10:03:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Spare part not found"
}
```

Permission rules

```text
Public endpoint
```

#### 5) Update Spare Part

Endpoint URL

```text
PATCH /api/spare-parts/PART_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "quantity": 5,
  "price": 130
}
```

Permission rules

```text
staff, admin
```

#### 6) Delete Spare Part

Endpoint URL

```text
DELETE /api/spare-parts/PART_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Spare part deleted successfully",
  "data": {
    "deleted": true
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can delete spare parts"
}
```

Permission rules

```text
staff, admin
```

#### 7) Add Spare Part Images

Endpoint URL

```text
POST /api/spare-parts/PART_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "multipart/form-data"
}
```

Example form-data

```text
images: file1.jpg
images: file2.jpg
```

Permission rules

```text
staff, admin
```

#### 8) Delete One Spare Part Image

Endpoint URL

```text
DELETE /api/spare-parts/PART_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "image_url": "https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/spare-parts/example.jpg"
}
```

Permission rules

```text
staff, admin
```

#### 9) Delete All Spare Part Images

Endpoint URL

```text
DELETE /api/spare-parts/PART_ID/images/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "delete_all": true
}
```

Permission rules

```text
staff, admin
```

### Inventory endpoints

#### 1) List Inventory

Endpoint URL

```text
GET /api/inventory/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Inventory fetched successfully",
  "data": [
    {
      "id": "INVENTORY_ID",
      "spare_part_id": "PART_ID",
      "spare_part_name": "Headlight",
      "quantity": 12,
      "updated_by": "STAFF_ID",
      "updated_at": "2026-03-10T10:04:00"
    }
  ]
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

Permission rules

```text
Authenticated users
```

#### 2) Update Inventory

Endpoint URL

```text
PATCH /api/inventory/INVENTORY_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "quantity": 20
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Inventory updated successfully",
  "data": {
    "id": "INVENTORY_ID",
    "spare_part_id": "PART_ID",
    "spare_part_name": "Headlight",
    "quantity": 20,
    "updated_by": "STAFF_ID",
    "updated_at": "2026-03-10T10:07:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can update inventory"
}
```

Permission rules

```text
staff, admin
```

### Orders endpoints

#### 1) Create Order

Endpoint URL

```text
POST /api/orders/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "spare_part_ids": [
    "PART_ID_1",
    "PART_ID_2"
  ]
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "id": "ORDER_ID",
    "customer_id": "CUSTOMER_ID",
    "spare_parts": [
      {
        "id": "PART_ID_1",
        "name": "Headlight",
        "price": 120.5
      },
      {
        "id": "PART_ID_2",
        "name": "Brake Pad",
        "price": 80
      }
    ],
    "total_price": 200.5,
    "status": "pending",
    "created_at": "2026-03-10T10:08:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Spare part does not exist: PART_ID_1"
}
```

Permission rules

```text
customer
```

#### 2) List Orders

Endpoint URL

```text
GET /api/orders/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Orders fetched successfully",
  "data": [
    {
      "id": "ORDER_ID",
      "customer_id": "CUSTOMER_ID",
      "spare_parts": [
        {
          "id": "PART_ID",
          "name": "Headlight",
          "price": 120.5
        }
      ],
      "total_price": 120.5,
      "status": "pending",
      "created_at": "2026-03-10T10:08:00"
    }
  ]
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

Permission rules

```text
Authenticated users
```

#### 3) Get Order By ID

Endpoint URL

```text
GET /api/orders/ORDER_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN"
}
```

Example request JSON

```json
{}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Order fetched successfully",
  "data": {
    "id": "ORDER_ID",
    "customer_id": "CUSTOMER_ID",
    "spare_parts": [
      {
        "id": "PART_ID",
        "name": "Headlight",
        "price": 120.5
      }
    ],
    "total_price": 120.5,
    "status": "pending",
    "created_at": "2026-03-10T10:08:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Order not found"
}
```

Permission rules

```text
customer own order only, staff/admin any order
```

#### 4) Update Order Status

Endpoint URL

```text
PATCH /api/orders/ORDER_ID/
```

Required headers

```json
{
  "Authorization": "Bearer ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

Example request JSON

```json
{
  "status": "completed"
}
```

Example success response JSON

```json
{
  "success": true,
  "message": "Order updated successfully",
  "data": {
    "id": "ORDER_ID",
    "customer_id": "CUSTOMER_ID",
    "spare_parts": [
      {
        "id": "PART_ID",
        "name": "Headlight",
        "price": 120.5
      }
    ],
    "total_price": 120.5,
    "status": "completed",
    "created_at": "2026-03-10T10:08:00"
  }
}
```

Example error response JSON

```json
{
  "success": false,
  "error": "Only staff or admin can update order status"
}
```

Permission rules

```text
staff, admin
```
