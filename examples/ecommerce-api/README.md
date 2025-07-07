# E-commerce API Example

A comprehensive e-commerce API built with ZestAPI demonstrating:

- **Product Management**: CRUD operations for products with categories
- **Shopping Cart**: Add/remove items, update quantities
- **Order Management**: Create orders, track status, order history
- **User Authentication**: JWT-based authentication
- **Inventory Management**: Stock tracking and validation
- **Payment Processing**: Mock payment integration
- **Search & Filtering**: Product search with filters

## Features

### Products
- Create, read, update, delete products
- Category management
- Inventory tracking
- Product search and filtering
- Image URL support

### Shopping Cart
- Add products to cart
- Update item quantities
- Remove items from cart
- Calculate totals with tax

### Orders
- Create orders from cart
- Order status tracking (pending, processing, shipped, delivered, cancelled)
- Order history
- Order details with line items

### Authentication
- User registration and login
- JWT token authentication
- Protected routes for user-specific operations

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Products
- `GET /products` - List all products (with search/filter)
- `GET /products/{id}` - Get product by ID
- `POST /products` - Create new product (admin only)
- `PUT /products/{id}` - Update product (admin only)
- `DELETE /products/{id}` - Delete product (admin only)

### Categories
- `GET /categories` - List all categories
- `POST /categories` - Create category (admin only)

### Cart
- `GET /cart` - Get user's cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item quantity
- `DELETE /cart/items/{item_id}` - Remove item from cart
- `DELETE /cart` - Clear entire cart

### Orders
- `GET /orders` - Get user's order history
- `GET /orders/{id}` - Get specific order details
- `POST /orders` - Create order from cart
- `PUT /orders/{id}/status` - Update order status (admin only)

## Installation

```bash
cd examples/ecommerce-api
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Get products
```bash
curl http://localhost:8000/products
```

### Add item to cart (requires authentication)
```bash
curl -X POST http://localhost:8000/cart/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Create order from cart
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"shipping_address": "123 Main St, City, State 12345"}'
```

## Default Data

The example includes sample data for testing:
- Sample products in various categories
- Admin user (admin@example.com / admin123)
- Regular user (user@example.com / user123)

## Production Notes

This is an example application. For production use:
- Replace in-memory storage with a real database
- Implement proper payment processing
- Add proper logging and monitoring
- Implement proper error handling
- Add input sanitization
- Use environment variables for secrets
- Add API rate limiting
- Implement proper inventory management
- Add email notifications
- Implement proper admin panel
