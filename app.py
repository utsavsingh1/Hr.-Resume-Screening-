from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import PyPDF2
import docx

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = '../uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('hr_screening.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS candidates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, email TEXT, phone TEXT,
                  resume_path TEXT, score INTEGER,
                  skills TEXT, experience TEXT,
                  created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS job_requirements
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT, required_skills TEXT,
                  min_experience INTEGER)''')
    conn.commit()
    conn.close()

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def screen_resume(text, required_skills):
    text_lower = text.lower()
    skills_found = [skill for skill in required_skills if skill.lower() in text_lower]
    score = int((len(skills_found) / len(required_skills)) * 100) if required_skills else 0
    return score, ', '.join(skills_found)

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    job_id = request.form.get('job_id', 1)
    
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(filepath)
    else:
        return jsonify({'error': 'Unsupported file format'}), 400
    
    conn = sqlite3.connect('hr_screening.db')
    c = conn.cursor()
    c.execute('SELECT required_skills FROM job_requirements WHERE id=?', (job_id,))
    result = c.fetchone()
    required_skills = result[0].split(',') if result else ['Python', 'JavaScript', 'SQL']
    
    score, skills_found = screen_resume(text, required_skills)
    
    c.execute('''INSERT INTO candidates (name, email, phone, resume_path, score, skills, experience, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, email, phone, filepath, score, skills_found, text[:500], datetime.now()))
    conn.commit()
    candidate_id = c.lastrowid
    conn.close()
    
    return jsonify({'message': 'Resume uploaded successfully', 'candidate_id': candidate_id, 'score': score})

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    conn = sqlite3.connect('hr_screening.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone, score, skills, created_at FROM candidates ORDER BY score DESC')
    candidates = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 
                   'score': row[4], 'skills': row[5], 'created_at': row[6]} for row in c.fetchall()]
    conn.close()
    return jsonify(candidates)

@app.route('/api/job-requirements', methods=['POST'])
def add_job():
    data = request.json
    conn = sqlite3.connect('hr_screening.db')
    c = conn.cursor()
    c.execute('INSERT INTO job_requirements (title, required_skills, min_experience) VALUES (?, ?, ?)',
              (data['title'], data['required_skills'], data['min_experience']))
    conn.commit()
    job_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Job added', 'job_id': job_id})

@app.route('/api/job-requirements', methods=['GET'])
def get_jobs():
    conn = sqlite3.connect('hr_screening.db')
    c = conn.cursor()
    c.execute('SELECT id, title, required_skills, min_experience FROM job_requirements')
    jobs = [{'id': row[0], 'title': row[1], 'required_skills': row[2], 'min_experience': row[3]} 
            for row in c.fetchall()]
    conn.close()
    return jsonify(jobs)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
