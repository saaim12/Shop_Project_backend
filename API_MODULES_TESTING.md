# API Modules Testing Guide

This guide covers testing for:

- Cars module
- Spare Parts module
- Inventory module
- Orders module

All endpoints are under `/api/...` and use JWT Bearer authentication.

## Base URL

- Local: `http://127.0.0.1:8000`

## Required Headers

Use these headers for protected endpoints:

- `Authorization: Bearer ACCESS_TOKEN`
- `Content-Type: application/json` (for JSON requests)
- `Content-Type: multipart/form-data` (for spare part image upload)

## JWT Usage

1. Register or login from existing auth endpoints:
- `POST /api/auth/register/`
- `POST /api/auth/login/`

2. Copy `access` token from login response.

3. Add header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

4. If access token expires, refresh using:
- `POST /api/auth/refresh/`

## Role-Based Access Rules

- `customer`
- `staff`
- `admin`

Rules:

- Customer:
  - Can create orders
  - Cannot create/delete cars
  - Cannot create/delete spare parts
- Staff:
  - Can create/delete cars
  - Can create/delete spare parts
  - Can update inventory quantities
  - Can update order status
- Admin:
  - Can do all staff actions
  - Can update order status
  - Can update inventory
  - In users module, only admin can create staff users

## Response Format

Success:

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Users Module

### 1) List Users For Admin Dashboard

- **GET** `/api/users/getall`
- Roles: `admin`
- Query params:
  - `role=all` to show all users
  - `role=customer` to show only customers
  - `role=staff` to show only staff
  - `role=admin` to show only admins
  - `group_by_role=true` to return grouped buckets

Example:

```bash
curl -X GET "http://127.0.0.1:8000/api/users/getall?role=all" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Example grouped response:

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

---

## Cars Module

### 1) Get All Cars

- **GET** `/api/cars/get-all/`
- Roles: public (no JWT required)
- Query params:
  - `page` (optional)
  - `page_size` (optional)

Example success response:

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
        "id": "67ce7c7f17f2eb210aa0a8b1",
        "number_plate": "ABC123",
        "color": "Red",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2018,
        "created_by": "67ce77ce17f2eb210aa0a8aa",
        "created_at": "2026-03-10T10:45:20.124000"
      }
    ]
  }
}
```

### 2) Create Car

- **POST** `/api/cars/create/`
- Roles: `staff`, `admin`
- Content type: `application/json` or `multipart/form-data`

Body:

```json
{
  "number_plate": "ABC123",
  "color": "Red",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2018
}
```

Example success response:

```json
{
  "success": true,
  "message": "Car created successfully",
  "data": {
    "id": "67ce7c7f17f2eb210aa0a8b1",
    "number_plate": "ABC123",
    "color": "Red",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2018,
    "created_by": "67ce77ce17f2eb210aa0a8aa",
    "created_at": "2026-03-10T10:45:20.124000"
  }
}
```

Duplicate validation:

- `number_plate` must be unique (case-insensitive)
- `brand + model + year` combination must be unique

If duplicate:

```json
{
  "success": false,
  "error": "Number plate already exists"
}
```

### 3) Get Car By ID

- **GET** `/api/cars/<car_id>/`
- Roles: public (no JWT required)

### 4) Update Car

- **PATCH** `/api/cars/<car_id>/`
- Roles: `staff`, `admin`

### 5) Delete Car

- **DELETE** `/api/cars/<car_id>/`
- Roles: `staff`, `admin`

### 6) Add Car Images

- **POST** `/api/cars/<car_id>/images/`
- Roles: `staff`, `admin`
- Content type: `multipart/form-data`
- Field: `images` (multiple files supported)

### 7) Delete One Car Image

- **DELETE** `/api/cars/<car_id>/images/`
- Roles: `staff`, `admin`
- Body:

```json
{
  "image_url": "https://.../cars/example.jpg"
}
```

### 8) Delete All Car Images

- **DELETE** `/api/cars/<car_id>/images/`
- Roles: `staff`, `admin`
- Body:

```json
{
  "delete_all": true
}
```

---

## Spare Parts Module

### 1) Spare Part Create Form Data

- **GET** `/api/spare-parts/create-data/`
- Roles: `staff`, `admin`

Returns:

- Available `conditions`: `new`, `used`, `external`
- Available cars with `id`, `number_plate`, `brand`, `model`
- Default quantity value: `1`

### 2) Create Spare Part

- **POST** `/api/spare-parts/`
- Roles: `staff`, `admin`
- Content type: `multipart/form-data`

Fields:

- `name` (string)
- `description` (string, optional)
- `price` (number)
- `quantity` (number, optional, default `1`)
- `condition` (`new` | `used` | `external`)
- `car_id` (required only when `condition=used`)
- `images` (multiple files, optional)

Validation rules:

- If `condition=used`, `car_id` must be provided.
- If `condition=new` or `condition=external`, `car_id` must not be provided.

Example (form-data):

- `name`: `Headlight`
- `description`: `Front right headlight`
- `price`: `120.5`
- `quantity`: `3`
- `condition`: `used`
- `car_id`: `67ce7c7f17f2eb210aa0a8b1`
- `images`: file1, file2

Example success response:

```json
{
  "success": true,
  "message": "Spare part created successfully",
  "data": {
    "id": "67ce7d3917f2eb210aa0a8b2",
    "name": "Headlight",
    "description": "Front right headlight",
    "price": 120.5,
    "quantity": 3,
    "condition": "used",
    "images": [
      "https://space.example.com/spare-parts/uuid_img1.jpg",
      "https://space.example.com/spare-parts/uuid_img2.jpg"
    ],
    "car_id": "67ce7c7f17f2eb210aa0a8b1",
    "created_by": "67ce77ce17f2eb210aa0a8aa",
    "created_at": "2026-03-10T10:48:25.004000"
  }
}
```

### 3) List Spare Parts

- **GET** `/api/spare-parts/`
- Roles: public (no JWT required)
- Query params:
  - `page` (optional)
  - `page_size` (optional)
  - `condition` (`new` | `used` | `external`, optional)

### 4) Get Spare Part By ID

- **GET** `/api/spare-parts/<part_id>/`
- Roles: public (no JWT required)

### 5) Update Spare Part

- **PATCH** `/api/spare-parts/<part_id>/`
- Roles: `staff`, `admin`

### 6) Delete Spare Part

- **DELETE** `/api/spare-parts/<part_id>/`
- Roles: `staff`, `admin`

### 7) Add Spare Part Images

- **POST** `/api/spare-parts/<part_id>/images/`
- Roles: `staff`, `admin`

### 8) Delete One Spare Part Image

- **DELETE** `/api/spare-parts/<part_id>/images/`
- Roles: `staff`, `admin`
- Body:

```json
{
  "image_url": "https://.../spare-parts/example.jpg"
}
```

### 9) Delete All Spare Part Images

- **DELETE** `/api/spare-parts/<part_id>/images/`
- Roles: `staff`, `admin`
- Body:

```json
{
  "delete_all": true
}
```

---

## Inventory Module

### 1) List Inventory

- **GET** `/api/inventory/`
- Roles: any authenticated role

Example success response:

```json
{
  "success": true,
  "message": "Inventory fetched successfully",
  "data": [
    {
      "id": "67ce7ddd17f2eb210aa0a8b3",
      "spare_part_id": "67ce7d3917f2eb210aa0a8b2",
      "spare_part_name": "Headlight",
      "quantity": 5,
      "updated_by": "67ce77ce17f2eb210aa0a8aa",
      "updated_at": "2026-03-10T10:50:03.302000"
    }
  ]
}
```

### 2) Update Inventory Quantity

- **PATCH** `/api/inventory/<inventory_id>/`
- Roles: `staff`, `admin`

Body:

```json
{
  "quantity": 10
}
```

Example success response:

```json
{
  "success": true,
  "message": "Inventory updated successfully",
  "data": {
    "id": "67ce7ddd17f2eb210aa0a8b3",
    "spare_part_id": "67ce7d3917f2eb210aa0a8b2",
    "spare_part_name": "Headlight",
    "quantity": 10,
    "updated_by": "67ce77ce17f2eb210aa0a8aa",
    "updated_at": "2026-03-10T10:55:00.111000"
  }
}
```

---

## Orders Module

### 1) Create Order

- **POST** `/api/orders/`
- Roles: `customer`

Body:

```json
{
  "spare_part_ids": [
    "67ce7d3917f2eb210aa0a8b2",
    "67ce7f2617f2eb210aa0a8b4"
  ]
}
```

Example success response:

```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "id": "67ce807517f2eb210aa0a8b5",
    "customer_id": "67ce801717f2eb210aa0a8b6",
    "spare_parts": [
      {
        "id": "67ce7d3917f2eb210aa0a8b2",
        "name": "Headlight",
        "price": 120.5
      },
      {
        "id": "67ce7f2617f2eb210aa0a8b4",
        "name": "Brake Pad",
        "price": 80.0
      }
    ],
    "total_price": 200.5,
    "status": "pending",
    "created_at": "2026-03-10T11:02:45.990000"
  }
}
```

### 2) List Orders

- **GET** `/api/orders/`
- Roles:
  - `customer`: sees own orders only
  - `staff`, `admin`: see all orders

### 3) Get Order By ID

- **GET** `/api/orders/<order_id>/`
- Roles:
  - `customer`: own order only
  - `staff`, `admin`: any order

### 4) Update Order Status

- **PATCH** `/api/orders/<order_id>/`
- Roles: `staff`, `admin`

Body:

```json
{
  "status": "confirmed"
}
```

Allowed status values:

- `pending`
- `confirmed`
- `cancelled`
- `completed`

---

## Postman Testing Instructions

1. Create environment variables:
- `base_url` = `http://127.0.0.1:8000`
- `access_token` = (set after login)
- `car_id`, `spare_part_id`, `inventory_id`, `order_id` (set from responses)

2. Add collection-level auth:
- Type: Bearer Token
- Token: `{{access_token}}`

3. Suggested test flow:
- Login as staff/admin -> create car
- Create spare part (used with `car_id`)
- Login as customer -> create order using `spare_part_ids`
- Login as staff/admin -> patch order status
- Staff/admin -> patch inventory quantity
- Test forbidden actions:
  - customer creating car
  - customer creating spare part
  - customer patching inventory
  - customer patching order status

4. Verify response shape for every request:
- Success => `success: true`, `message`, `data`
- Error => `success: false`, `error`

---

## cURL Examples

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"staff@example.com","password":"password123"}'
```

### List Users By Role (admin)

```bash
curl -X GET "http://127.0.0.1:8000/api/users/getall?role=all" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Create Car (staff/admin)

```bash
curl -X POST "http://127.0.0.1:8000/api/cars/create/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"number_plate":"ABC123","color":"Red","brand":"Toyota","model":"Corolla","year":2018}'
```

### Create Spare Part With Images (staff/admin)

```bash
curl -X GET "http://127.0.0.1:8000/api/spare-parts/create-data/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Create Spare Part With Images (staff/admin)

```bash
curl -X POST "http://127.0.0.1:8000/api/spare-parts/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "name=Headlight" \
  -F "description=Front right headlight" \
  -F "price=120.5" \
  -F "quantity=3" \
  -F "condition=used" \
  -F "car_id=CAR_OBJECT_ID" \
  -F "images=@C:/path/image1.jpg" \
  -F "images=@C:/path/image2.jpg"
```

### List Inventory

```bash
curl -X GET "http://127.0.0.1:8000/api/inventory/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### List Cars (public, paginated)

```bash
curl -X GET "http://127.0.0.1:8000/api/cars/get-all/?page=1&page_size=10"
```

### Get Car By ID (public)

```bash
curl -X GET "http://127.0.0.1:8000/api/cars/CAR_ID/"
```

### Update Car (staff/admin)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/cars/CAR_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"color":"Black"}'
```

### Add Car Images (staff/admin)

```bash
curl -X POST "http://127.0.0.1:8000/api/cars/CAR_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "images=@C:/path/car1.jpg" \
  -F "images=@C:/path/car2.jpg"
```

### Delete One Car Image (staff/admin)

```bash
curl -X DELETE "http://127.0.0.1:8000/api/cars/CAR_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/cars/example.jpg"}'
```

### Delete All Car Images (staff/admin)

```bash
curl -X DELETE "http://127.0.0.1:8000/api/cars/CAR_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delete_all":true}'
```

### List Spare Parts (public, paginated)

```bash
curl -X GET "http://127.0.0.1:8000/api/spare-parts/?page=1&page_size=10"
```

### List Used Spare Parts Only (public)

```bash
curl -X GET "http://127.0.0.1:8000/api/spare-parts/?condition=used&page=1&page_size=10"
```

### Get Spare Part By ID (public)

```bash
curl -X GET "http://127.0.0.1:8000/api/spare-parts/PART_ID/"
```

### Update Spare Part (staff/admin)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/spare-parts/PART_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5,"price":140}'
```

### Add Spare Part Images (staff/admin)

```bash
curl -X POST "http://127.0.0.1:8000/api/spare-parts/PART_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "images=@C:/path/image1.jpg" \
  -F "images=@C:/path/image2.jpg"
```

### Delete One Spare Part Image (staff/admin)

```bash
curl -X DELETE "http://127.0.0.1:8000/api/spare-parts/PART_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://shop-project-images-bucket.sfo3.digitaloceanspaces.com/spare-parts/example.jpg"}'
```

### Delete All Spare Part Images (staff/admin)

```bash
curl -X DELETE "http://127.0.0.1:8000/api/spare-parts/PART_ID/images/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delete_all":true}'
```

### Patch Inventory Quantity (staff/admin)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/inventory/INVENTORY_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":10}'
```

### Create Order (customer)

```bash
curl -X POST "http://127.0.0.1:8000/api/orders/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"spare_part_ids":["SPARE_PART_ID_1","SPARE_PART_ID_2"]}'
```

### Patch Order Status (staff/admin)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/orders/ORDER_ID/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"confirmed"}'
```
