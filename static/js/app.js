// Main JavaScript for ML Pipeline Web Application

const API_BASE_URL = window.location.origin;

// State management
let appState = {
    modelsLoaded: false,
    currentTab: 'grade',
    modelInfo: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    checkAPIHealth();
    loadModelInfo();
    setupEventListeners();
});

// Tab Navigation
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`${target}-tab`).classList.add('active');
            
            appState.currentTab = target;
        });
    });
}

// API Health Check
async function checkAPIHealth() {
    const statusBadge = document.getElementById('status-badge');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy' && data.models_loaded) {
            statusBadge.textContent = '🟢 Online';
            statusBadge.classList.add('online');
            statusBadge.classList.remove('offline');
            appState.modelsLoaded = true;
        } else {
            statusBadge.textContent = '🟡 Initializing...';
            statusBadge.classList.remove('online', 'offline');
        }
    } catch (error) {
        statusBadge.textContent = '🔴 Offline';
        statusBadge.classList.add('offline');
        statusBadge.classList.remove('online');
        showAlert('API server is not responding. Please start the server.', 'error');
    }
}

// Load Model Info
async function loadModelInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/models/info`);
        const data = await response.json();
        
        appState.modelInfo = data;
        displayModelInfo(data);
    } catch (error) {
        console.error('Failed to load model info:', error);
    }
}

// Display Model Info
function displayModelInfo(data) {
    const container = document.getElementById('model-info-container');
    
    const html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">🎯 Grading Model</h3>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-item-label">Baseline Model</div>
                    <div class="info-item-value">${data.grading_pipeline.baseline_model}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Advanced Model</div>
                    <div class="info-item-value">${data.grading_pipeline.advanced_model}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Features</div>
                    <div class="info-item-value">${data.grading_pipeline.features.length}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Classes</div>
                    <div class="info-item-value">${data.grading_pipeline.classes.join(', ')}</div>
                </div>
            </div>
            ${data.grading_pipeline.performance ? `
                <div style="margin-top: 20px; padding: 15px; background: var(--light-bg); border-radius: 8px;">
                    <strong>Performance Metrics:</strong><br>
                    Baseline Accuracy: ${(data.grading_pipeline.performance.baseline_accuracy * 100).toFixed(2)}%<br>
                    Advanced Accuracy: ${(data.grading_pipeline.performance.advanced_accuracy * 100).toFixed(2)}%
                </div>
            ` : ''}
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">💬 Triage Model</h3>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-item-label">Classifier</div>
                    <div class="info-item-value">${data.triage_pipeline.classifier}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Priority Classes</div>
                    <div class="info-item-value">${data.triage_pipeline.classes.join(', ')}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Departments</div>
                    <div class="info-item-value">${data.triage_pipeline.departments.length}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Confidence Threshold</div>
                    <div class="info-item-value">${(data.triage_pipeline.confidence_threshold * 100).toFixed(0)}%</div>
                </div>
            </div>
            ${data.triage_pipeline.performance ? `
                <div style="margin-top: 20px; padding: 15px; background: var(--light-bg); border-radius: 8px;">
                    <strong>Performance Metrics:</strong><br>
                    Accuracy: ${(data.triage_pipeline.performance.accuracy * 100).toFixed(2)}%<br>
                    Auto-approval Rate: ${(data.triage_pipeline.performance.auto_approval_rate * 100).toFixed(2)}%
                </div>
            ` : ''}
        </div>
    `;
    
    container.innerHTML = html;
}

// Event Listeners
function setupEventListeners() {
    // Grade Prediction Form
    document.getElementById('grade-form').addEventListener('submit', handleGradePrediction);
    
    // Triage Prediction Form
    document.getElementById('triage-form').addEventListener('submit', handleTriagePrediction);
    
    // Batch Prediction
    document.getElementById('batch-form').addEventListener('submit', handleBatchPrediction);
    
    // Quick fill buttons
    document.querySelectorAll('.quick-fill-btn').forEach(btn => {
        btn.addEventListener('click', () => quickFillForm(btn.dataset.profile));
    });
}

// Handle Grade Prediction
async function handleGradePrediction(e) {
    e.preventDefault();
    
    const formData = {
        attendance_percentage: parseFloat(document.getElementById('attendance').value),
        quiz_average: parseFloat(document.getElementById('quiz_avg').value),
        assignment_average: parseFloat(document.getElementById('assignment_avg').value),
        midterm_score: parseFloat(document.getElementById('midterm').value),
        participation_score: parseFloat(document.getElementById('participation').value),
        study_hours_per_week: parseFloat(document.getElementById('study_hours').value),
        previous_gpa: parseFloat(document.getElementById('gpa').value)
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/grade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayGradeResult(data);
        } else {
            showAlert(data.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        showAlert('Failed to connect to API: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display Grade Result
function displayGradeResult(data) {
    const container = document.getElementById('grade-result');
    
    const gradeColors = {
        'A': '#10b981',
        'B': '#3b82f6',
        'C': '#f59e0b',
        'D': '#ef4444'
    };
    
    const html = `
        <div class="result-header">
            📊 Prediction Results
        </div>
        
        <div class="result-item">
            <span class="result-label">Predicted Grade</span>
            <span class="result-value" style="font-size: 2rem; color: ${gradeColors[data.predicted_grade]}">
                ${data.predicted_grade}
            </span>
        </div>
        
        <div class="result-item">
            <span class="result-label">Confidence Score</span>
            <span class="result-value">${(data.confidence_score * 100).toFixed(2)}%</span>
        </div>
        
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${data.confidence_score * 100}%">
                ${(data.confidence_score * 100).toFixed(0)}%
            </div>
        </div>
        
        <div class="result-item">
            <span class="result-label">Model Used</span>
            <span class="result-value">${data.model_used}</span>
        </div>
        
        <div class="result-item">
            <span class="result-label">Routing Decision</span>
            <span class="badge ${data.auto_approve ? 'badge-success' : 'badge-warning'}">
                ${data.routing_decision.replace('_', ' ').toUpperCase()}
            </span>
        </div>
        
        ${data.engineered_features ? `
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <strong style="display: block; margin-bottom: 10px;">Engineered Features:</strong>
                <div style="font-size: 0.9rem;">
                    Engagement Score: ${data.engineered_features.engagement_score.toFixed(2)}<br>
                    Academic Consistency: ${data.engineered_features.academic_consistency.toFixed(2)}<br>
                    Performance Trend: ${data.engineered_features.performance_trend.toFixed(2)}
                </div>
            </div>
        ` : ''}
    `;
    
    container.innerHTML = html;
    container.style.display = 'block';
    container.classList.add('fade-in');
}

// Handle Triage Prediction
async function handleTriagePrediction(e) {
    e.preventDefault();
    
    const formData = {
        student_query: document.getElementById('student_query').value,
        department: document.getElementById('department').value,
        days_to_deadline: parseInt(document.getElementById('days_to_deadline').value)
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/triage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayTriageResult(data);
        } else {
            showAlert(data.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        showAlert('Failed to connect to API: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display Triage Result
function displayTriageResult(data) {
    const container = document.getElementById('triage-result');
    
    const priorityColors = {
        'High': '#ef4444',
        'Medium': '#f59e0b',
        'Low': '#10b981'
    };
    
    const html = `
        <div class="result-header">
            💬 Triage Results
        </div>
        
        <div class="result-item">
            <span class="result-label">Priority Level</span>
            <span class="badge" style="background: ${priorityColors[data.predicted_priority]}; font-size: 1.2rem; padding: 8px 16px;">
                ${data.predicted_priority}
            </span>
        </div>
        
        <div class="result-item">
            <span class="result-label">Confidence Score</span>
            <span class="result-value">${(data.confidence_score * 100).toFixed(2)}%</span>
        </div>
        
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${data.confidence_score * 100}%">
                ${(data.confidence_score * 100).toFixed(0)}%
            </div>
        </div>
        
        <div class="result-item">
            <span class="result-label">Routing Decision</span>
            <span class="badge ${data.auto_approve ? 'badge-success' : 'badge-warning'}">
                ${data.routing_decision.replace('_', ' ').toUpperCase()}
            </span>
        </div>
        
        ${data.priority_probabilities ? `
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <strong style="display: block; margin-bottom: 10px;">Priority Probabilities:</strong>
                ${Object.entries(data.priority_probabilities).map(([priority, prob]) => `
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 4px;">
                            <span>${priority}</span>
                            <span>${(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div class="confidence-bar" style="height: 10px;">
                            <div class="confidence-fill" style="width: ${prob * 100}%; background: ${priorityColors[priority]}"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
        
        ${data.feature_analysis ? `
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <strong style="display: block; margin-bottom: 10px;">Feature Analysis:</strong>
                <div style="font-size: 0.9rem; line-height: 1.8;">
                    Query Length: ${data.feature_analysis.query_length} words<br>
                    Urgent Keywords: ${data.feature_analysis.has_urgent_keywords ? '✓ Detected' : '✗ Not found'}<br>
                    Technical Keywords: ${data.feature_analysis.has_technical_keywords ? '✓ Detected' : '✗ Not found'}<br>
                    Urgency Score: ${data.feature_analysis.urgency_from_deadline}/3<br>
                    Department: ${data.feature_analysis.department}
                </div>
            </div>
        ` : ''}
    `;
    
    container.innerHTML = html;
    container.style.display = 'block';
    container.classList.add('fade-in');
}

// Handle Batch Prediction
async function handleBatchPrediction(e) {
    e.preventDefault();
    
    const csvText = document.getElementById('batch_csv').value;
    const students = parseCSV(csvText);
    
    if (students.length === 0) {
        showAlert('Please enter valid CSV data', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/batch/grade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ students })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBatchResults(data);
        } else {
            showAlert(data.error || 'Batch prediction failed', 'error');
        }
    } catch (error) {
        showAlert('Failed to connect to API: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Parse CSV
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const students = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => parseFloat(v.trim()));
        
        if (values.length === 7 && values.every(v => !isNaN(v))) {
            students.push({
                attendance_percentage: values[0],
                quiz_average: values[1],
                assignment_average: values[2],
                midterm_score: values[3],
                participation_score: values[4],
                study_hours_per_week: values[5],
                previous_gpa: values[6]
            });
        }
    }
    
    return students;
}

// Display Batch Results
function displayBatchResults(data) {
    const container = document.getElementById('batch-result');
    
    const html = `
        <div class="result-header">
            📊 Batch Prediction Results
        </div>
        
        <div class="result-item">
            <span class="result-label">Total Students</span>
            <span class="result-value">${data.total_students}</span>
        </div>
        
        <div class="result-item">
            <span class="result-label">Successful Predictions</span>
            <span class="result-value">${data.successful_predictions}</span>
        </div>
        
        <div style="margin-top: 20px;">
            <strong style="display: block; margin-bottom: 15px;">Individual Results:</strong>
            <div style="max-height: 400px; overflow-y: auto;">
                ${data.batch_results.map(result => `
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span><strong>Student ${result.student_index + 1}</strong></span>
                            ${result.predicted_grade ? `
                                <span>
                                    Grade: <strong>${result.predicted_grade}</strong> 
                                    (${(result.confidence * 100).toFixed(1)}%)
                                    ${result.auto_approve ? '✓' : '⚠️'}
                                </span>
                            ` : `
                                <span style="color: #ef4444;">Error: ${result.error}</span>
                            `}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    container.style.display = 'block';
    container.classList.add('fade-in');
}

// Quick Fill Form
function quickFillForm(profile) {
    const profiles = {
        'high': {
            attendance: 95,
            quiz_avg: 88.5,
            assignment_avg: 92,
            midterm: 87,
            participation: 9.2,
            study_hours: 20,
            gpa: 3.8
        },
        'average': {
            attendance: 78,
            quiz_avg: 72.5,
            assignment_avg: 75,
            midterm: 74,
            participation: 6.5,
            study_hours: 12,
            gpa: 3.0
        },
        'low': {
            attendance: 65,
            quiz_avg: 58.5,
            assignment_avg: 62,
            midterm: 55,
            participation: 4.2,
            study_hours: 8,
            gpa: 2.3
        }
    };
    
    const data = profiles[profile];
    if (data) {
        document.getElementById('attendance').value = data.attendance;
        document.getElementById('quiz_avg').value = data.quiz_avg;
        document.getElementById('assignment_avg').value = data.assignment_avg;
        document.getElementById('midterm').value = data.midterm;
        document.getElementById('participation').value = data.participation;
        document.getElementById('study_hours').value = data.study_hours;
        document.getElementById('gpa').value = data.gpa;
    }
}

// Utility Functions
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} fade-in`;
    alertContainer.innerHTML = `
        <span>${type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️'}</span>
        <span>${message}</span>
    `;
    
    document.body.insertBefore(alertContainer, document.body.firstChild);
    
    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}
