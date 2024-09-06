# Advanced File Processing System

## Overview
The Advanced File Processing System is designed to handle various file types, including PDF, Excel, and CAD files. It extracts relevant data, generates forms, and integrates with Microsoft Dynamics for data transfer. The system is built using FastAPI for the backend and React for the frontend.

## Features
- **File Upload**: Supports uploading multiple files simultaneously.
- **File Processing**: Processes PDF, Excel, and CAD files to extract data.
- **Form Generation**: Automatically generates forms based on extracted data.
- **Microsoft Dynamics Integration**: Sends processed data to Microsoft Dynamics.
- **User Authentication**: Secure access using OAuth2.
- **Unit and Integration Testing**: Comprehensive tests to ensure functionality.

## Technologies Used
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, PyPDF2, pandas, ezdxf, cryptography
- **Frontend**: React, Axios
- **Testing**: pytest, FastAPI TestClient

## Installation

### Prerequisites
- Python 3.7+
- Node.js and npm
- PostgreSQL (for the backend database)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Update the `SQLALCHEMY_DATABASE_URL` in `main.py` with your PostgreSQL credentials.
   - Run the database migrations:
     ```bash
     python -m main
     ```

5. Create a `.env` file in the backend directory and add your secret key:
   ```plaintext
   SECRET_KEY=your-secret-key
   ```

6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required packages:
   ```bash
   npm install
   ```

3. Start the React application:
   ```bash
   npm start
   ```

## Usage
- Access the frontend at `http://localhost:3000`.
- Use the file upload form to upload PDF, Excel, or CAD files.
- The processed results will be displayed after the upload.

## Testing
To run the tests for the backend:
```bash
cd tests
pytest
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.