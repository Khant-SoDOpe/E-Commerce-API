# E-Commerce API

This is an E-Commerce API built with FastAPI. It provides features for user authentication, product management, and category management.

## Features

- User authentication and registration
- Email verification and password reset
- Product management (CRUD operations)
- Category management (CRUD operations)
- JWT-based authentication
- CORS support for frontend integration

## Requirements

- Python 3.9+
- PostgreSQL database
- Environment variables configured in a `.env` file

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/e-commerce-api.git
   cd e-commerce-api
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your database and email settings.

5. Run database migrations:

   ```bash
   python -m app.db
   ```

6. Start the server:

   ```bash
   python main.py
   ```

   The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Authentication

- `POST /auth/jwt/login`: Login with email and password.
- `POST /auth/register`: Register a new user.
- `POST /auth/forgot-password`: Request a password reset.
- `POST /auth/reset-password`: Reset the password.
- `GET /auth/verify`: Verify email with a token.

### Products

- `POST /products/`: Create a new product (superuser only).
- `GET /products/`: List all products.
- `GET /products/{product_id}`: Get a product by ID.
- `PUT /products/{product_id}`: Update a product (superuser only).
- `DELETE /products/{product_id}`: Delete a product (superuser only).

### Categories

- `POST /categories/`: Create a new category (superuser only).
- `GET /categories/`: List all categories.
- `GET /categories/{category_id}`: Get a category by ID.
- `PUT /categories/{category_id}`: Update a category (superuser only).
- `DELETE /categories/{category_id}`: Delete a category (superuser only).

## Environment Variables

Refer to `.env.example` for the required environment variables.

## Development

To enable hot-reloading during development, set `reload=True` in `main.py`:

```python
uvicorn.run(
    "app.app:app",
    host="0.0.0.0",
    port=8000,
    log_level="info",
    reload=True  # Enable reload for development
)
```

## License

This project is licensed under the MIT License.