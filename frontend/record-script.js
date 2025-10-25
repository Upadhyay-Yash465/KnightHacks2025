// Record page specific JavaScript
let isRecording = false;

function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingPreview = document.getElementById('recordingPreview');
    
    if (!isRecording) {
        // Start recording
        isRecording = true;
        recordBtn.innerHTML = `
            <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/>
            </svg>
            <span class="record-text">Stop Recording</span>
        `;
        recordBtn.classList.add('recording');
        recordingStatus.classList.remove('hidden');
        
        // Simulate recording for 3 seconds
        setTimeout(() => {
            stopRecording();
        }, 3000);
    } else {
        stopRecording();
    }
}

function stopRecording() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingPreview = document.getElementById('recordingPreview');
    
    isRecording = false;
    recordBtn.innerHTML = `
        <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1C13.1 1 14 1.9 14 3V11C14 12.1 13.1 13 12 13C10.9 13 10 12.1 10 11V3C10 1.9 10.9 1 12 1Z" fill="currentColor"/>
            <path d="M19 10V12C19 15.9 15.9 19 12 19C8.1 19 5 15.9 5 12V10H7V12C7 14.8 9.2 17 12 17C14.8 17 17 14.8 17 12V10H19Z" fill="currentColor"/>
            <path d="M11 22H13V24H11V22Z" fill="currentColor"/>
        </svg>
        <span class="record-text">Start Recording</span>
    `;
    recordBtn.classList.remove('recording');
    recordingStatus.classList.add('hidden');
    recordingPreview.classList.remove('hidden');
}

function uploadRecording() {
    const uploadProgress = document.getElementById('uploadProgress');
    const recordingPreview = document.getElementById('recordingPreview');
    const reportContent = document.getElementById('report-content');
    
    recordingPreview.classList.add('hidden');
    uploadProgress.classList.remove('hidden');
    
    // Simulate upload and analysis
    setTimeout(() => {
        uploadProgress.classList.add('hidden');
        if (reportContent) {
            reportContent.classList.remove('hidden');
        }
    }, 2000);
}

function resetRecording() {
    const recordingPreview = document.getElementById('recordingPreview');
    const uploadProgress = document.getElementById('uploadProgress');
    const reportContent = document.getElementById('report-content');
    
    recordingPreview.classList.add('hidden');
    uploadProgress.classList.add('hidden');
    if (reportContent) {
        reportContent.classList.add('hidden');
    }
}

// Initialize page
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
