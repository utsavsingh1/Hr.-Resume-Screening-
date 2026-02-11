# HR Automated Resume Screening System

## Features
- Upload resumes (PDF/DOCX)
- Automated keyword-based screening
- Score candidates based on job requirements
- Manage job positions and requirements
- View all candidates sorted by score

## Setup Instructions

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Backend Server
```bash
cd backend
python app.py
```
Server runs on: http://localhost:5000

### 3. Open Frontend
Open `frontend/index.html` in your browser

## API Endpoints

- POST `/api/upload-resume` - Upload and screen resume
- GET `/api/candidates` - Get all candidates
- POST `/api/job-requirements` - Add job position
- GET `/api/job-requirements` - Get all jobs

## Database
SQLite database (`hr_screening.db`) stores:
- Candidates information
- Resume screening scores
- Job requirements

## Usage
1. Add job requirements with required skills
2. Upload candidate resumes
3. System automatically screens and scores resumes
4. View ranked candidates by score
