const uploadForm = document.getElementById('uploadForm');
const csvFile = document.getElementById('csvFile');
const studentTableBody = document.querySelector('#studentTable tbody');
const resultsSection = document.getElementById('results');
const loadingSection = document.getElementById('loading');

// Function to display student data in the table
const displayStudents = (students) => {
  studentTableBody.innerHTML = '';
  if (students.length === 0) {
    studentTableBody.innerHTML = '<tr><td colspan="6">No student data available.</td></tr>';
    return;
  }
  students.forEach(student => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${student.name}</td>
      <td>${student.attendance}</td>
      <td>${student.marks}</td>
      <td><span class="risk-${student.riskLevel}">${student.riskLevel.toUpperCase()}</span></td>
      <td>${student.riskScore}%</td>
      <td>${student.reasons.join(', ')}</td>
    `;
    studentTableBody.appendChild(row);
  });
};

// Handles file upload and communication with the backend
uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = csvFile.files[0];
  if (!file) {
    alert('Please select a CSV file.');
    return;
  }
  loadingSection.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await fetch('http://localhost:3000/api/data/upload', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    displayStudents(result.students);
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
  } catch (error) {
    console.error('Error:', error);
    loadingSection.classList.add('hidden');
    alert('An error occurred. See console for details.');
  }
});

// Fetches and displays existing data on page load
const fetchDashboardData = async () => {
    try {
        const response = await fetch('http://localhost:3000/api/dashboard');
        const result = await response.json();
        displayStudents(result.students);
    } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
    }
};
fetchDashboardData();