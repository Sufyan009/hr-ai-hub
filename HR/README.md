# Candidate Management Platform

This application consists of a Django backend and a React frontend for managing candidates in a recruitment process.

## Project Structure

- `candidate_mcp/` - Django backend
- `candidate_ui/` - React frontend

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd candidate_mcp
   ```

2. Install dependencies (if not already installed):
   ```
   pip install django djangorestframework django-cors-headers
   ```

3. Apply migrations:
   ```
   python manage.py migrate
   ```

4. Create a test user:
   ```
   python create_test_user.py
   ```
   This will create a user with the following credentials:
   - Username: testuser
   - Password: password123
   - And will display the authentication token

5. Start the backend server:
   ```
   python manage.py runserver
   ```
   The backend will be available at http://localhost:8000/

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd candidate_ui
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will be available at http://localhost:3000/

## Authentication

The application uses token-based authentication. When you log in, a token is generated and stored in localStorage. This token is included in all subsequent API requests.

## Features

- User authentication (login/logout)
- Protected routes that require authentication
- User profile management
- Candidate management
- Dashboard with metrics

## API Endpoints

- `/candidates/api/token/` - Obtain authentication token
- `/candidates/api/profile/` - User profile management
- `/candidates/api/` - Candidate list and creation
- `/candidates/api/<id>/` - Candidate detail, update, and deletion

## Troubleshooting

- If you encounter CORS issues, make sure the frontend URL is included in the `CORS_ALLOWED_ORIGINS` setting in the backend's `settings.py`.
- If authentication fails, check that the token is being correctly included in the request headers.