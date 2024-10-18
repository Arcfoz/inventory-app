# Inventory Management API Documentation

## Endpoints

### Categories
- `GET /categories`: Retrieve all categories with their items
- `GET /categories/names`: Retrieve category names and IDs
- `POST /categories`: Create a new category

### Items
- `GET /items`: Retrieve items with pagination
- `GET /items/{item_id}`: Retrieve a single item
- `POST /items`: Create a new item
- `PUT /items/{item_id}`: Update an existing item
- `DELETE /items/{item_id}`: Delete an item

### Authentication
- `POST /login`: Login and retrieve a token
- `POST /register`: Register a new user

## Request/Response Examples

### Categories

#### GET /categories
Response:
```json
[
  {
    "id": 1,
    "name": "Category 1",
    "items": [...]
  },
  ...
]
```

#### POST /categories
Request:
```json
{
  "name": "New Category"
}
```
Response:
```json
{
  "message": "Category created successfully"
}
```

### Items

#### GET /items
Response:
```json
{
  "items": [...],
  "pagination": {
    "total_items": 10,
    "total_pages": 2,
    "current_page": 1
  }
}
```

#### POST /items
Request:
```json
{
  "category_id": 1,
  "name": "New Item",
  "description": "New Item Description",
  "price": 10.99
}
```
Response:
```json
{
  "message": "Item created successfully"
}
```

### Authentication

#### POST /login
Request:
```json
{
  "username": "Username",
  "password": "Password"
}
```
Response:
```json
{
  "token": "Authentication Token"
}
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/Arcfoz/inventory-app.git
   cd inventory-app
   ```
2. Database Migration:
  ```
  python .\migration.py migrate up
  ```

3. Build and run with Docker:
   ```
   docker build -t inventory-app .
   docker run -p 8000:8000 inventory-app
   ```

4. Clean data:
  ```
  python .\migration.py migrate down
  ```

## Testing

Run tests with coverage:
```
python migration.py test tests/testing.py --coverage
```

Postman Collection: [Inventory API Tests](https://elements.getpostman.com/redirect?entityId=28552659-b7adb724-e437-4200-9934-7951317a864a&entityType=collection)
