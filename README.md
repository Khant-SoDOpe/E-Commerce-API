# E-Commerce API

This project is a FastAPI-based backend for an e-commerce platform. It includes user authentication, product and category management, email notifications, and database integration.

---

## Features

### 1. **User Authentication**
- JWT-based authentication using `fastapi-users`.
- Routes for:
  - Login (`/auth/jwt/login`)
  - Registration (`/auth/register`)
  - Password reset (`/auth/forgot-password`, `/auth/reset-password`)
  - Email verification (`/auth/verify`)
- Custom error handling for login failures with descriptive error messages.

### 2. **Product Management**
- CRUD operations for products:
  - Create (`/products/`)
  - Read (`/products/` and `/products/{product_id}`)
  - Update (`/products/{product_id}`)
  - Delete (`/products/{product_id}`)
- Superuser-only access for creating, updating, and deleting products.

### 3. **Category Management**
- CRUD operations for categories:
  - Create (`/categories/`)
  - Read (`/categories/` and `/categories/{category_id}`)
  - Update (`/categories/{category_id}`)
  - Delete (`/categories/{category_id}`)
- Superuser-only access for creating, updating, and deleting categories.

### 4. **Email Notifications**
- Email verification and password reset emails using `fastapi-mail`.
- Configurable email templates with links for verification and password reset.

### 5. **Database Integration**
- PostgreSQL database with `SQLAlchemy` and `asyncpg`.
- Models for `User`, `Product`, and `Category` with UUID primary keys.
- Automatic timestamps for `created_at` and `updated_at` fields.

### 6. **Datetime Formatting**
- All datetime fields are serialized in Japan Standard Time (JST) format (`Year-Month-Date-Hour-Minutes-Second`).

### 7. **Environment Configuration**
- `.env` file for managing sensitive configurations like database URL, email settings, and CORS origins.

### 8. **CORS Middleware**
- Configured to allow requests from specific origins.

---

## Project Structure

```
E-Commerce-API/
├── app/
│   ├── app.py               # Main FastAPI application
│   ├── db.py                # Database models and session management
│   ├── email.py             # Email notification logic
│   ├── schemas.py           # Pydantic models for request/response validation
│   ├── users.py             # User management and authentication
├── main.py                  # Entry point for running the application
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
```

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- PostgreSQL database
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Environment Variables
Create a `.env` file in the root directory with the following content:
```properties
# Database configuration
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<host>:<port>/<database>

# Email Settings
MAIL_USERNAME=<your-email-username>
MAIL_PASSWORD=<your-email-password>
MAIL_FROM=<your-email-address>
MAIL_SERVER=<your-smtp-server>
MAIL_PORT=587

# Application Settings
SECRET=<your-secret-key>
FRONTEND_URL=http://localhost:3000

# API URL for email verification
API_URL=http://127.0.0.1:8000

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Running the Application
1. Run database migrations:
   ```bash
   python -m app.db
   ```
2. Start the application:
   ```bash
   python main.py
   ```

### Running in Development Mode
Use `uvicorn` with the `--reload` flag for development:
```bash
uvicorn app.app:app --reload
```

---

## API Endpoints

### Authentication
- **POST** `/auth/jwt/login`: Login with email and password.
  - Custom error response for invalid credentials:
    ```json
    {
        "status": "error",
        "message": "Invalid login credentials. Please check your email and password.",
        "error_type": "authentication_error"
    }
    ```
- **POST** `/auth/register`: Register a new user.
- **POST** `/auth/forgot-password`: Request a password reset email.
- **POST** `/auth/reset-password`: Reset the user's password.
- **GET** `/auth/verify`: Verify the user's email.

### Products
- **POST** `/products/`: Create a new product (superuser only).
- **GET** `/products/`: List all products.
- **GET** `/products/{product_id}`: Get details of a specific product.
- **PUT** `/products/{product_id}`: Update a product (superuser only).
- **DELETE** `/products/{product_id}`: Delete a product (superuser only).

### Categories
- **POST** `/categories/`: Create a new category (superuser only).
- **GET** `/categories/`: List all categories.
- **GET** `/categories/{category_id}`: Get details of a specific category.
- **PUT** `/categories/{category_id}`: Update a category (superuser only).
- **DELETE** `/categories/{category_id}`: Delete a category (superuser only).

---

## Code Overview

### 1. **`app/app.py`**
- Main FastAPI application.
- Includes routes for authentication, products, and categories.
- Configures CORS middleware and exception handling.

### 2. **`app/db.py`**
- Defines database models for `User`, `Product`, and `Category`.
- Configures `SQLAlchemy` with PostgreSQL.
- Provides session management and database initialization.

### 3. **`app/email.py`**
- Handles email notifications for user actions like registration and password reset.
- Uses `fastapi-mail` for sending emails.

### 4. **`app/schemas.py`**
- Defines Pydantic models for request and response validation.
- Customizes datetime serialization to Japan Standard Time (JST).

### 5. **`app/users.py`**
- Implements user management and authentication using `fastapi-users`.
- Customizes error handling for login failures.

### 6. **`main.py`**
- Entry point for running the application in production mode with `uvicorn`.