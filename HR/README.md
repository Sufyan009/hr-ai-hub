# Candidate Management Platform

This application consists of a Django backend and a React frontend for managing candidates in a recruitment process.

## Project Structure

- `candidate_mcp/` - Django backend
- `candidate_ui/` - React frontend

## Features

### File Upload Functionality

The platform supports multiple file upload methods:

1. **Individual Candidate Upload**: Upload resume and avatar files when adding/editing candidates
2. **Bulk Upload**: Upload CSV/Excel files with multiple candidates via the Bulk Upload Modal
3. **Chatbot File Upload**: Upload files directly through the chatbot interface

#### Chatbot File Upload

Users can now upload files directly through the chatbot interface:

- **Supported File Types**:
  - CSV/Excel files (.csv, .xlsx, .xls) for bulk candidate data
  - Resume files (.pdf, .doc, .docx, .txt) for individual candidates
- **File Size Limit**: 10MB maximum
- **Features**:
  - Drag & drop or click to upload
  - Automatic file type detection
  - Real-time upload progress
  - AI-powered file processing
  - Integration with candidate management system
  - **Standardized Template System**: Download template for consistent data format

#### Template System

The platform provides a standardized candidate template to ensure consistent data mapping:

- **Template Download**: Available in the chat interface (Plus dropdown → Download Template)
- **Standardized Columns**:
  - `first_name`, `last_name`, `email` (required)
  - `phone_number`, `job_title`, `candidate_stage`
  - `communication_skills`, `years_of_experience`
  - `expected_salary`, `current_salary`, `city`, `source`, `notes`
- **Smart Field Mapping**: Automatically maps various column names to standard fields
- **Data Validation**: Checks for data quality, missing fields, and duplicates
- **Quality Metrics**: Provides data quality score and suggestions for improvement

#### Enhanced File Processing

**CSV/Excel Processing:**
- **Multiple Encodings**: Supports UTF-8, Latin-1, CP1252 for better compatibility
- **Smart Field Mapping**: Maps various column names to standard fields
- **Data Validation**: Checks email format, duplicates, required fields
- **Quality Scoring**: Provides data quality percentage and suggestions
- **Preview Data**: Shows first 10 rows for review before import

**Resume Processing:**
- **PDF/DOC/DOCX**: Extracts text and candidate information
- **Smart Parsing**: Uses regex patterns to find candidate details
- **Information Extraction**: Name, email, phone, experience, skills
- **Content Analysis**: Provides insights on candidate qualifications

#### How to Use Chatbot File Upload

1. **Download Template** (Recommended):
   - Click the Plus button (➕) in chat
   - Select "Download Template"
   - Fill in candidate data using the template format
   - Upload the completed file

2. **Upload Files**:
   - Click the Plus button (➕) in chat
   - Select "Upload files"
   - Choose CSV, Excel, PDF, DOC, or TXT file
   - System automatically processes and analyzes the file

3. **Review Results**:
   - System shows extracted information
   - Displays data quality metrics
   - Provides suggestions for improvement
   - Offers relevant next steps

4. **Take Action**:
   - Add candidates to the system
   - Analyze data for insights
   - Check for duplicates
   - Export or modify data

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
- **File upload through chatbot interface**
- Bulk candidate import
- Advanced search and filtering

## API Endpoints

- `/candidates/api/token/` - Obtain authentication token
- `/candidates/api/profile/` - User profile management
- `/candidates/api/` - Candidate list and creation
- `/candidates/api/<id>/` - Candidate detail, update, and deletion
- `/chat/upload` - Bulk file upload for candidates
- `/chat/upload/file` - Single file upload for resumes/documents
- `/chat/process/file` - Process uploaded files for candidate extraction

## Troubleshooting

- If you encounter CORS issues, make sure the frontend URL is included in the `CORS_ALLOWED_ORIGINS` setting in the backend's `settings.py`.
- If authentication fails, check that the token is being correctly included in the request headers.
- For file upload issues, ensure the file type is supported and file size is under 5MB.