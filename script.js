const API_URL = 'http://localhost:5000/api';

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'candidates') loadCandidates();
    if (tabName === 'jobs') loadJobs();
}

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('phone', document.getElementById('phone').value);
    formData.append('job_id', document.getElementById('job_id').value);
    formData.append('resume', document.getElementById('resume').files[0]);
    
    try {
        const response = await fetch(`${API_URL}/upload-resume`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        const resultDiv = document.getElementById('uploadResult');
        resultDiv.className = response.ok ? 'success' : 'error';
        resultDiv.textContent = response.ok ? 
            `Resume uploaded! Screening Score: ${data.score}%` : 
            data.error;
        e.target.reset();
    } catch (error) {
        document.getElementById('uploadResult').className = 'error';
        document.getElementById('uploadResult').textContent = 'Upload failed';
    }
});

document.getElementById('jobForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const jobData = {
        title: document.getElementById('jobTitle').value,
        required_skills: document.getElementById('requiredSkills').value,
        min_experience: parseInt(document.getElementById('minExperience').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/job-requirements`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(jobData)
        });
        if (response.ok) {
            e.target.reset();
            loadJobs();
            loadJobsDropdown();
        }
    } catch (error) {
        console.error('Error adding job:', error);
    }
});

async function loadCandidates() {
    try {
        const response = await fetch(`${API_URL}/candidates`);
        const candidates = await response.json();
        const list = document.getElementById('candidatesList');
        list.innerHTML = candidates.map(c => `
            <div class="candidate-card">
                <h3>${c.name}</h3>
                <p><strong>Email:</strong> ${c.email}</p>
                <p><strong>Phone:</strong> ${c.phone}</p>
                <p><strong>Skills Found:</strong> ${c.skills || 'N/A'}</p>
                <span class="score ${c.score >= 70 ? 'high' : c.score >= 40 ? 'medium' : 'low'}">
                    Score: ${c.score}%
                </span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading candidates:', error);
    }
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_URL}/job-requirements`);
        const jobs = await response.json();
        const list = document.getElementById('jobsList');
        list.innerHTML = '<h3>Available Positions</h3>' + jobs.map(j => `
            <div class="job-card">
                <h4>${j.title}</h4>
                <p><strong>Required Skills:</strong> ${j.required_skills}</p>
                <p><strong>Min Experience:</strong> ${j.min_experience} years</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

async function loadJobsDropdown() {
    try {
        const response = await fetch(`${API_URL}/job-requirements`);
        const jobs = await response.json();
        const select = document.getElementById('job_id');
        select.innerHTML = '<option value="1">Select Job Position</option>' + 
            jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
    } catch (error) {
        console.error('Error loading jobs dropdown:', error);
    }
}

loadJobsDropdown();
