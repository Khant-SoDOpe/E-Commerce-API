# E-Commerce-API

## Overview

E-Commerce-API is a FastAPI application that provides user authentication. This README file provides instructions on how to set up and run the project.

## Prerequisites

- Python 3.8+
- MySQL database

## Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Khant-SoDOpe/E-Commerce-API.git
   cd E-Commerce-API
   ```

3. **Install the dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up the environment variables**:
   - Create a `.env` file in the project root directory and add the following environment variables:
     ```env
     DATABASE_URL="mysql+pymysql://username:password@localhost/dbname"
     SECRET_KEY="your-secret-key"
     ```

5. **Set up the database**:
   - Ensure your MySQL database is running.
   - Run the following command to create the database tables:
     ```sh
     python -c "from database import create_tables; create_tables()"
     ```

6. **Run the FastAPI application**:
   ```sh
   uvicorn app:app --reload
   ```

7. **Access the application**:
   - Open your browser and navigate to `http://localhost:8000/docs` to access the FastAPI interactive documentation.

## Endpoints

- **POST /auth/signup**: Create a new user.
- **POST /auth/login**: Login with email and password.
- **POST /auth/token**: Obtain a JWT token.
- **GET /public/users/{user_id}**: Read user information by user ID.
- **GET /auth/users/me**: Get current authenticated user information.

## Testing the Endpoints

### Testing the /auth/signup Endpoint

1. **Make a POST request to the `/auth/signup` endpoint**:
   ```sh
   curl -X POST "http://localhost:8000/auth/signup" -H "Content-Type: application/json" -d '{
     "username": "your_username",
     "email": "your_email@example.com",
     "phone": "1234567890",
     "password": "your_password",
     "address": "123 Main St",
     "city": "Anytown",
     "state": "CA",
     "postal_code": "12345"
   }'
   ```

2. **Check the response**:
   - If the user is created successfully, you should receive a JSON response containing the user ID:
     ```json
     {
       "id": 1
     }
     ```
   - If the email is already registered, you will receive an error message.

### Testing the /auth/login Endpoint

1. **Make a POST request to the `/auth/login` endpoint**:
   ```sh
   curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{
     "email": "your_email@example.com",
     "password": "your_password"
   }'
   ```

2. **Check the response**:
   - If the credentials are correct, you should receive a JSON response containing a success message and user ID:
     ```json
     {
       "message": "Login successful",
       "user_id": 1
     }
     ```
   - If the credentials are incorrect, you will receive an error message.

### Testing the /auth/token Endpoint

1. **Make a POST request to the `/auth/token` endpoint**:
   ```sh
   curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" -d "email=your_email@example.com&password=your_password"
   ```

2. **Check the response**:
   - If the credentials are correct, you should receive a JSON response containing the access token:
     ```json
     {
       "access_token": "your_access_token",
       "token_type": "bearer"
     }
     ```
   - If the credentials are incorrect, you will receive an error message.

### Testing the /public/users/{user_id} Endpoint

1. **Make a GET request to the `/public/users/{user_id}` endpoint**:
   ```sh
   curl -X GET "http://localhost:8000/public/users/1"
   ```

2. **Check the response**:
   - If the user ID exists, you should receive a JSON response containing the user details:
     ```json
     {
       "id": 1,
       "username": "your_username",
       "email": "your_email@example.com",
       "phone": "1234567890",
       "address": "123 Main St",
       "city": "Anytown",
       "state": "CA",
       "postal_code": "12345",
       "is_oauth": false,
       "created_at": "2023-10-01T00:00:00Z",
       "updated_at": "2023-10-01T00:00:00Z"
     }
     ```
   - If the user ID does not exist, you will receive an error message.

### Testing the /auth/users/me Endpoint

1. **Obtain a JWT token** by logging in or signing up (see the steps above).

2. **Make a GET request to the `/auth/users/me` endpoint**:
   ```sh
   curl -X GET "http://localhost:8000/auth/users/me" -H "Authorization: Bearer your_access_token"
   ```

3. **Check the response**:
   - If the token is valid, you should receive a JSON response containing the user details:
     ```json
     {
       "id": 1,
       "username": "your_username",
       "email": "your_email@example.com",
       "phone": "1234567890",
       "address": "123 Main St",
       "city": "Anytown",
       "state": "CA",
       "postal_code": "12345",
       "is_oauth": false,
       "created_at": "2023-10-01T00:00:00Z",
       "updated_at": "2023-10-01T00:00:00Z"
     }
     ```
   - If the token is invalid or expired, you will receive an error message.

## License

This project is licensed under the MIT License.