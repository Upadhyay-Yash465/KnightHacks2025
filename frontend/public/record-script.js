// Record page specific JavaScript with backend integration
let isRecording = false;
let mediaRecorder = null;
let recordedChunks = [];
let audioBlob = null;

const API_BASE_URL = 'http://localhost:8000';

// Initialize recording functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set active navigation state
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
});

async function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingPreview = document.getElementById('recordingPreview');
    const uploadProgress = document.getElementById('uploadProgress');
    
    if (!isRecording) {
        try {
            await startRecording();
        } catch (error) {
            console.error('Error starting recording:', error);
            showError('Failed to start recording. Please check microphone permissions.');
        }
    } else {
        stopRecording();
    }
}

async function startRecording() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            } 
        });
        
        // Create MediaRecorder
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        recordedChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(recordedChunks, { type: 'audio/webm' });
            showRecordingComplete();
            
            // Stop all tracks to release microphone
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        recordBtn.innerHTML = `
            <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/>
            </svg>
            <span class="record-text">Stop Recording</span>
        `;
        recordBtn.classList.add('recording');
        recordingStatus.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        throw error;
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
    isRecording = false;
}

function showRecordingComplete() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingPreview = document.getElementById('recordingPreview');
    
    // Reset record button
    recordBtn.innerHTML = `
        <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1C13.1 1 14 1.9 14 3V11C14 12.1 13.1 13 12 13C10.9 13 10 12.1 10 11V3C10 1.9 10.9 1 12 1Z" fill="currentColor"/>
            <path d="M19 10V12C19 15.9 15.9 19 12 19C8.1 19 5 15.9 5 12V10H7V12C7 14.8 9.2 17 12 17C14.8 17 17 14.8 17 12V10H19Z" fill="currentColor"/>
            <path d="M11 22H13V24H11V22Z" fill="currentColor"/>
        </svg>
        <span class="record-text">Start Recording</span>
    `;
    recordBtn.classList.remove('recording');
    
    // Hide recording status, show preview
    recordingStatus.classList.add('hidden');
    recordingPreview.classList.remove('hidden');
}

async function uploadRecording() {
    if (!audioBlob) {
        showError('No recording to upload');
        return;
    }
    
    const uploadProgress = document.getElementById('uploadProgress');
    const recordingPreview = document.getElementById('recordingPreview');
    
    try {
        // Show upload progress
        recordingPreview.classList.add('hidden');
        uploadProgress.classList.remove('hidden');
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        
        // Upload and analyze audio
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Analysis result:', result);
        
        // Handle both real analysis and test responses
        if (result.transcript === 'This is a test transcript') {
            // This is a test response, show a message
            showTestModeMessage();
        }
        
        // Hide upload progress
        uploadProgress.classList.add('hidden');
        
        // Show analysis results
        showAnalysisResults(result);
        
    } catch (error) {
        console.error('Error uploading recording:', error);
        uploadProgress.classList.add('hidden');
        showError('Failed to analyze recording. Please try again.');
    }
}

function showAnalysisResults(analysis) {
    const reportContent = document.getElementById('report-content');
    const uploadProgress = document.getElementById('uploadProgress');
    
    // Update the report with actual data
    updateReportMetrics(analysis);
    
    // Show the report
    reportContent.classList.remove('hidden');
    
    // Scroll to report
    reportContent.scrollIntoView({ behavior: 'smooth' });
}

function updateReportMetrics(analysis) {
    // Update overall score (calculate from clarity score)
    const scoreNumber = document.querySelector('.score-number');
    if (scoreNumber) {
        scoreNumber.textContent = analysis.clarity_score ? analysis.clarity_score.toFixed(1) : '8.5';
    }
    
    // Update individual metrics based on actual backend response
    const metrics = [
        { label: 'Clarity', value: analysis.clarity_score || 8.5 },
        { label: 'Filler Words', value: analysis.filler_count ? Math.max(0, 10 - analysis.filler_count) : 7.5 }, // Convert filler count to score
        { label: 'Overall', value: analysis.clarity_score || 8.5 }
    ];
    
    const metricItems = document.querySelectorAll('.metric-item');
    metricItems.forEach((item, index) => {
        if (metrics[index]) {
            const label = item.querySelector('.metric-label');
            const value = item.querySelector('.metric-value');
            const fill = item.querySelector('.metric-fill');
            
            if (label) label.textContent = metrics[index].label;
            if (value) value.textContent = `${metrics[index].value.toFixed(1)}/10`;
            if (fill) fill.style.width = `${Math.min(100, metrics[index].value * 10)}%`;
        }
    });
    
    // Update feedback content
    updateFeedbackContent(analysis);
}

function updateFeedbackContent(analysis) {
    const strengthsList = document.querySelector('.feedback-positive ul');
    const improvementsList = document.querySelector('.feedback-improvements ul');
    
    // Update strengths based on backend suggestions
    if (strengthsList) {
        if (analysis.suggestions && analysis.suggestions.length > 0) {
            // Filter positive suggestions
            const positiveSuggestions = analysis.suggestions.filter(suggestion => 
                suggestion.toLowerCase().includes('good') || 
                suggestion.toLowerCase().includes('excellent') ||
                suggestion.toLowerCase().includes('well') ||
                suggestion.toLowerCase().includes('strong')
            );
            
            if (positiveSuggestions.length > 0) {
                strengthsList.innerHTML = positiveSuggestions.map(strength => `<li>${strength}</li>`).join('');
            } else {
                strengthsList.innerHTML = '<li>Clear speech delivery</li><li>Good microphone quality</li>';
            }
        } else {
            strengthsList.innerHTML = '<li>Clear speech delivery</li><li>Good microphone quality</li>';
        }
    }
    
    // Update improvements based on backend suggestions
    if (improvementsList) {
        if (analysis.suggestions && analysis.suggestions.length > 0) {
            // Filter improvement suggestions
            const improvementSuggestions = analysis.suggestions.filter(suggestion => 
                suggestion.toLowerCase().includes('improve') || 
                suggestion.toLowerCase().includes('reduce') ||
                suggestion.toLowerCase().includes('try') ||
                suggestion.toLowerCase().includes('consider')
            );
            
            if (improvementSuggestions.length > 0) {
                improvementsList.innerHTML = improvementSuggestions.map(improvement => `<li>${improvement}</li>`).join('');
            } else {
                improvementsList.innerHTML = '<li>Consider reducing filler words</li><li>Try varying your pace</li>';
            }
        } else {
            improvementsList.innerHTML = '<li>Consider reducing filler words</li><li>Try varying your pace</li>';
        }
    }
    
    // Show transcript if available
    if (analysis.transcript) {
        showTranscript(analysis.transcript);
    }
}

function showTranscript(transcript) {
    // Create or update transcript display
    let transcriptDiv = document.getElementById('transcript-display');
    if (!transcriptDiv) {
        transcriptDiv = document.createElement('div');
        transcriptDiv.id = 'transcript-display';
        transcriptDiv.className = 'transcript-display';
        transcriptDiv.style.cssText = `
            background: rgba(31, 41, 55, 0.8);
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(75, 85, 99, 0.5);
        `;
        
        const reportCard = document.querySelector('.report-card');
        if (reportCard) {
            reportCard.appendChild(transcriptDiv);
        }
    }
    
    transcriptDiv.innerHTML = `
        <h4 style="color: #f97316; margin-bottom: 1rem;">Transcript</h4>
        <p style="color: #d1d5db; line-height: 1.6;">${transcript}</p>
    `;
}

function showTestModeMessage() {
    const uploadProgress = document.getElementById('uploadProgress');
    uploadProgress.innerHTML = `
        <div class="progress-content">
            <h3>🎉 Integration Working!</h3>
            <p>Your recording was successfully sent to the backend!</p>
            <p><strong>Note:</strong> This is a test response. The full AI analysis features require additional dependencies to be installed.</p>
            <button class="btn-primary" onclick="showAnalysisResults({transcript: 'This is a test transcript', filler_count: 2, clarity_score: 8.5, suggestions: ['Great job!', 'Try to reduce filler words'], summary: 'Good overall performance'})">View Test Results</button>
        </div>
    `;
}

function resetRecording() {
    const recordingPreview = document.getElementById('recordingPreview');
    const uploadProgress = document.getElementById('uploadProgress');
    const reportContent = document.getElementById('report-content');
    
    // Hide all status elements
    recordingPreview.classList.add('hidden');
    uploadProgress.classList.add('hidden');
    reportContent.classList.add('hidden');
    
    // Reset variables
    audioBlob = null;
    recordedChunks = [];
    isRecording = false;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    // Create or update error message
    let errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error-message';
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc2626;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            z-index: 1000;
            max-width: 300px;
        `;
        document.body.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.remove();
        }
    }, 5000);
}

// Make functions globally available
window.toggleRecording = toggleRecording;
window.uploadRecording = uploadRecording;
window.resetRecording = resetRecording;