// Video Recording functionality - Converted from React component
let isRecording = false;
let mediaRecorder = null;
let recordedChunks = [];
let stream = null;
let recordingTimer = null;
let recordingTime = 0;
let recordedVideoBlob = null;

// Initialize camera on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCamera();
    setActiveNavLink();
    initializeTranscriptionFeedback();
});

async function initializeCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: true
        });
        
        const videoElement = document.getElementById('webcamVideo');
        videoElement.srcObject = stream;
        
        console.log('Camera initialized successfully');
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showCameraPermissionMessage();
    }
}

function showCameraPermissionMessage() {
    const videoContainer = document.querySelector('.video-container');
    videoContainer.innerHTML = `
        <div class="camera-permission">
            <h3>Camera Access Required</h3>
            <p>Please allow camera access to record your speech practice. Click the button below to try again.</p>
            <button onclick="initializeCamera()">Enable Camera</button>
        </div>
    `;
}

function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

function startRecording() {
    if (!stream) {
        alert('Camera not available. Please refresh the page and allow camera access.');
        return;
    }
    
    recordedChunks = [];
    recordingTime = 0;
    
    try {
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'video/webm;codecs=vp9'
        });
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            recordedVideoBlob = blob;
            const videoUrl = URL.createObjectURL(blob);
            
            // Show recorded video
            const videoPreview = document.getElementById('videoPreview');
            const videoPlayback = document.getElementById('videoPlayback');
            const recordedVideo = document.getElementById('recordedVideo');
            const statusText = document.getElementById('statusText');
            const downloadButton = document.getElementById('downloadButton');
            const fileInfo = document.getElementById('fileInfo');
            const previewActions = document.getElementById('previewActions');
            
            videoPreview.classList.add('hidden');
            videoPlayback.classList.remove('hidden');
            recordedVideo.src = videoUrl;
            statusText.textContent = 'Recorded Video (Mirrored)';
            downloadButton.classList.remove('hidden');
            fileInfo.classList.remove('hidden');
            previewActions.classList.remove('hidden');
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        updateRecordingUI();
        
        // Start timer
        recordingTimer = setInterval(() => {
            recordingTime++;
            updateRecordingTimer();
        }, 1000);
        
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error starting recording. Please try again.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Clear timer
        if (recordingTimer) {
            clearInterval(recordingTimer);
            recordingTimer = null;
        }
        
        // Update UI
        updateRecordingUI();
    }
}

function updateRecordingUI() {
    const recordButton = document.getElementById('recordButton');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const recordingTimer = document.getElementById('recordingTimer');
    
    if (isRecording) {
        // Recording state
        recordButton.innerHTML = `
            <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/>
            </svg>
            <span class="record-text">Stop Recording</span>
        `;
        recordButton.classList.add('recording');
        recordingIndicator.classList.remove('hidden');
        recordingTimer.classList.remove('hidden');
    } else {
        // Stopped state
        recordButton.innerHTML = `
            <svg class="record-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 5v14l11-7z" fill="currentColor"/>
            </svg>
            <span class="record-text">Start Recording</span>
        `;
        recordButton.classList.remove('recording');
        recordingIndicator.classList.add('hidden');
        recordingTimer.classList.add('hidden');
    }
}

function updateRecordingTimer() {
    const minutes = Math.floor(recordingTime / 60);
    const seconds = recordingTime % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const recordingTimer = document.getElementById('recordingTimer');
    if (recordingTimer) {
        recordingTimer.textContent = timeString;
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const videoUrl = URL.createObjectURL(file);
        recordedVideoBlob = file;
        
        // Show uploaded video
        const videoPreview = document.getElementById('videoPreview');
        const videoPlayback = document.getElementById('videoPlayback');
        const recordedVideo = document.getElementById('recordedVideo');
        const statusText = document.getElementById('statusText');
        const downloadButton = document.getElementById('downloadButton');
        const fileInfo = document.getElementById('fileInfo');
        const previewActions = document.getElementById('previewActions');
        
        videoPreview.classList.add('hidden');
        videoPlayback.classList.remove('hidden');
        recordedVideo.src = videoUrl;
        statusText.textContent = 'Uploaded Video (Mirrored)';
        downloadButton.classList.remove('hidden');
        fileInfo.classList.remove('hidden');
        previewActions.classList.remove('hidden');
    }
}

function downloadVideo() {
    if (recordedVideoBlob) {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(recordedVideoBlob);
        link.download = `recording-${Date.now()}.webm`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function uploadRecording() {
    const uploadProgress = document.getElementById('uploadProgress');
    const previewActions = document.getElementById('previewActions');
    const reportContent = document.getElementById('report-content');
    
    previewActions.classList.add('hidden');
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
    const videoPreview = document.getElementById('videoPreview');
    const videoPlayback = document.getElementById('videoPlayback');
    const recordedVideo = document.getElementById('recordedVideo');
    const statusText = document.getElementById('statusText');
    const downloadButton = document.getElementById('downloadButton');
    const fileInfo = document.getElementById('fileInfo');
    const previewActions = document.getElementById('previewActions');
    const uploadProgress = document.getElementById('uploadProgress');
    const reportContent = document.getElementById('report-content');
    
    // Reset video elements
    videoPreview.classList.remove('hidden');
    videoPlayback.classList.add('hidden');
    if (recordedVideo) {
        recordedVideo.src = '';
    }
    statusText.textContent = 'Camera Preview (Mirrored)';
    downloadButton.classList.add('hidden');
    fileInfo.classList.add('hidden');
    previewActions.classList.add('hidden');
    
    // Reset other elements
    uploadProgress.classList.add('hidden');
    if (reportContent) {
        reportContent.classList.add('hidden');
    }
    
    // Reset recording state
    isRecording = false;
    recordingTime = 0;
    recordedChunks = [];
    recordedVideoBlob = null;
    
    // Update UI
    updateRecordingUI();
}

function setActiveNavLink() {
    // Set active class for record link
    const recordLink = document.querySelector('.nav-link[href="record.html"]');
    if (recordLink) {
        recordLink.classList.add('active');
    }
}

// Transcription feedback functionality
function initializeTranscriptionFeedback() {
    const highlightWords = document.querySelectorAll('.highlight-word');
    
    highlightWords.forEach(word => {
        word.addEventListener('click', function(e) {
            e.preventDefault();
            showSuggestionPopup(this);
        });
    });
    
    // Close popup when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.highlight-word') && !e.target.closest('.suggestion-popup')) {
            closeSuggestionPopup();
        }
    });
    
    // Update popup position on scroll (only add once)
    if (!window.popupScrollListenerAdded) {
        window.addEventListener('scroll', function() {
        if (window.currentWordElement) {
            const popup = document.getElementById('suggestionPopup');
            if (popup && !popup.classList.contains('hidden')) {
                const wordRect = window.currentWordElement.getBoundingClientRect();
                const top = wordRect.top - 300;
                const left = Math.max(10, wordRect.left + 50);
                
                popup.style.top = top + 'px';
                popup.style.left = left + 'px';
            }
        }
        });
        window.popupScrollListenerAdded = true;
    }
}

function showSuggestionPopup(wordElement) {
    const popup = document.getElementById('suggestionPopup');
    const originalWord = document.getElementById('originalWord');
    const suggestedWord = document.getElementById('suggestedWord');
    const reasonText = document.getElementById('reasonText');
    
    // Check if all elements exist
    if (!popup || !originalWord || !suggestedWord || !reasonText) {
        console.error('Required popup elements not found');
        return;
    }
    
    // Store reference to current word element for scroll updates
    window.currentWordElement = wordElement;
    
    // Get data from the clicked word
    const suggestion = wordElement.getAttribute('data-suggestion');
    const reason = wordElement.getAttribute('data-reason');
    const original = wordElement.textContent;
    
    // Populate popup content
    originalWord.textContent = original;
    suggestedWord.textContent = suggestion;
    reasonText.textContent = reason;
    
    // Position popup above the clicked word
    const wordRect = wordElement.getBoundingClientRect();
    
    // Calculate position relative to viewport (well above and to the right of the word)
    const top = wordRect.top - 300;
    const left = Math.max(10, wordRect.left + 50);
    
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
    
    // Show popup
    popup.classList.remove('hidden');
}

function closeSuggestionPopup() {
    const popup = document.getElementById('suggestionPopup');
    popup.classList.add('hidden');
    window.currentWordElement = null;
}