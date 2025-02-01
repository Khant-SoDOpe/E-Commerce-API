# E-Commerce-API

## Overview

E-Commerce-API is a FastAPI application that provides user authentication and Google OAuth login functionality. This README file provides instructions on how to set up and run the project.

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
- **GET /public/users/{user_id}**: Read user information by user ID.

## License

This project is licensed under the MIT License.