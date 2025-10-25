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
    initializeEmotionGraphInteractivity();
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

// Audio Analysis Functions - Easy plug and play for backend integration
function updateAudioAnalysis(audioData) {
    // Update metric values
    updateMetric('prosodyValue', audioData.prosody.value);
    updateMetric('prosodyScore', audioData.prosody.score);
    updateMetric('prosodyExplanation', audioData.prosody.explanation);
    
    updateMetric('toneValue', audioData.tone.value);
    updateMetric('toneScore', audioData.tone.score);
    updateMetric('toneExplanation', audioData.tone.explanation);
    
    updateMetric('pitchValue', audioData.pitch.value);
    updateMetric('pitchScore', audioData.pitch.score);
    updateMetric('pitchExplanation', audioData.pitch.explanation);
    
    updateMetric('speedValue', audioData.speed.value);
    updateMetric('speedScore', audioData.speed.score);
    updateMetric('speedExplanation', audioData.speed.explanation);
}

function updateMetric(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

// Example usage for backend integration:
// const audioData = {
//     prosody: { value: "Excellent", score: "9.2/10", explanation: "..." },
//     tone: { value: "Confident", score: "8.7/10", explanation: "..." },
//     pitch: { value: "Dynamic", score: "8.9/10", explanation: "..." },
//     speed: { value: "Optimal", score: "8.4/10", explanation: "..." }
// };
// updateAudioAnalysis(audioData);

// Visual Analysis Functions - Easy plug and play for backend integration
function updateVisualAnalysis(visualData) {
    // Update ratings
    updateElement('emotionRating', visualData.emotions.rating);
    updateElement('emotionDescription', visualData.emotions.description);
    updateElement('gestureRating', visualData.gestures.rating);
    updateElement('gestureDescription', visualData.gestures.description);
    
    // Update graph data
    updateEmotionGraph(visualData.emotionProgression);
    
    // Update breakdown content
    updateBreakdownContent(visualData.breakdown);
}

function updateElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

// Global variable to store emotion data
window.emotionData = null;

function updateEmotionGraph(emotionData) {
    window.emotionData = emotionData;
    renderEmotionGraph();
}

function renderEmotionGraph() {
    const graphContainer = document.getElementById('emotionGraph');
    if (!graphContainer || !window.emotionData) return;
    
    // Clear existing graph content but keep the structure
    const emotionLine = document.getElementById('emotionLine');
    const dataPoints = document.getElementById('dataPoints');
    
    if (emotionLine) emotionLine.innerHTML = '';
    if (dataPoints) dataPoints.innerHTML = '';
    
    // Get active emotions from legend
    const activeEmotions = getActiveEmotions();
    
    // Create SVG for multiple emotion lines
    if (emotionLine) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.pointerEvents = 'none';
        
        // Define emotion colors
        const emotionColors = {
            'Happy': '#F59E0B',
            'Angry': '#DC2626',
            'Disgust': '#10B981',
            'Fear': '#8B5CF6',
            'Surprise': '#EC4899',
            'Sad': '#3B82F6',
            'Neutral': '#6B7280'
        };
        
        // Create lines for each active emotion
        activeEmotions.forEach(emotion => {
            const emotionPoints = window.emotionData.filter(point => point.emotion === emotion);
            if (emotionPoints.length > 1) {
                // Sort points by time to ensure proper line connection
                emotionPoints.sort((a, b) => {
                    const timeA = parseFloat(a.time.replace(':', '.'));
                    const timeB = parseFloat(b.time.replace(':', '.'));
                    return timeA - timeB;
                });
                
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                let pathData = '';
                
                emotionPoints.forEach((point, index) => {
                    const x = point.xPosition;
                    const y = point.yPosition;
                    
                    if (index === 0) {
                        pathData += `M ${x} ${y}`;
                    } else {
                        pathData += ` L ${x} ${y}`;
                    }
                });
                
                path.setAttribute('d', pathData);
                path.setAttribute('stroke', emotionColors[emotion]);
                path.setAttribute('stroke-width', '3');
                path.setAttribute('fill', 'none');
                path.setAttribute('opacity', '0.8');
                path.setAttribute('stroke-linecap', 'round');
                path.setAttribute('stroke-linejoin', 'round');
                path.setAttribute('data-emotion', emotion);
                
                svg.appendChild(path);
            }
        });
        
        emotionLine.appendChild(svg);
    }
    
    // Add data points for active emotions only
    if (dataPoints) {
        window.emotionData.forEach((point, index) => {
            if (activeEmotions.includes(point.emotion)) {
                const dataPoint = document.createElement('div');
                dataPoint.className = 'data-point';
                dataPoint.style.top = `${point.yPosition}%`;
                dataPoint.style.left = `${point.xPosition}%`;
                dataPoint.style.backgroundColor = emotionColors[point.emotion];
                dataPoint.style.borderColor = emotionColors[point.emotion];
                dataPoint.setAttribute('data-time', point.time);
                dataPoint.setAttribute('data-emotion', point.emotion);
                dataPoint.setAttribute('data-intensity', point.intensity || '5');
                dataPoints.appendChild(dataPoint);
            }
        });
    }
}

function getActiveEmotions() {
    const legendItems = document.querySelectorAll('.legend-item.active');
    return Array.from(legendItems).map(item => item.getAttribute('data-emotion'));
}

function initializeEmotionGraphInteractivity() {
    const legendItems = document.querySelectorAll('.legend-item');
    const toggleAllBtn = document.getElementById('toggleAllBtn');
    
    // Individual emotion toggle
    legendItems.forEach(item => {
        item.addEventListener('click', function() {
            const emotion = this.getAttribute('data-emotion');
            
            // Toggle active state
            if (this.classList.contains('active')) {
                this.classList.remove('active');
                this.classList.add('inactive');
            } else {
                this.classList.remove('inactive');
                this.classList.add('active');
            }
            
            // Update toggle all button text
            updateToggleAllButton();
            
            // Re-render graph with updated active emotions
            renderEmotionGraph();
        });
    });
    
    // Toggle all button
    if (toggleAllBtn) {
        toggleAllBtn.addEventListener('click', function() {
            const allActive = areAllEmotionsActive();
            
            legendItems.forEach(item => {
                if (allActive) {
                    // Turn all off
                    item.classList.remove('active');
                    item.classList.add('inactive');
                } else {
                    // Turn all on
                    item.classList.remove('inactive');
                    item.classList.add('active');
                }
            });
            
            // Update button text
            updateToggleAllButton();
            
            // Re-render graph
            renderEmotionGraph();
        });
    }
}

function areAllEmotionsActive() {
    const legendItems = document.querySelectorAll('.legend-item');
    return Array.from(legendItems).every(item => item.classList.contains('active'));
}

function updateToggleAllButton() {
    const toggleAllBtn = document.getElementById('toggleAllBtn');
    if (toggleAllBtn) {
        const allActive = areAllEmotionsActive();
        toggleAllBtn.textContent = allActive ? 'Hide All' : 'Show All';
    }
}

function updateBreakdownContent(breakdownData) {
    const breakdownContent = document.getElementById('breakdownContent');
    if (!breakdownContent || !breakdownData) return;
    
    // Clear existing content
    breakdownContent.innerHTML = '';
    
    // Add breakdown items
    breakdownData.forEach(item => {
        const breakdownItem = document.createElement('div');
        breakdownItem.className = 'breakdown-item';
        
        const category = document.createElement('div');
        category.className = 'breakdown-category';
        category.textContent = item.category;
        
        const text = document.createElement('div');
        text.className = 'breakdown-text';
        text.textContent = item.text;
        
        breakdownItem.appendChild(category);
        breakdownItem.appendChild(text);
        breakdownContent.appendChild(breakdownItem);
    });
}

// Example usage for backend integration:
// const visualData = {
//     emotions: { rating: "9.1/10", description: "Highly expressive" },
//     gestures: { rating: "8.7/10", description: "Very effective" },
//     emotionProgression: [
//         { xPosition: 10, yPosition: 20, time: "0:05", emotion: "Confident" },
//         { xPosition: 30, yPosition: 30, time: "0:15", emotion: "Enthusiastic" },
//         { xPosition: 50, yPosition: 40, time: "0:25", emotion: "Calm" },
//         { xPosition: 70, yPosition: 25, time: "0:35", emotion: "Confident" },
//         { xPosition: 90, yPosition: 35, time: "0:45", emotion: "Engaged" }
//     ],
//     breakdown: [
//         { category: "Emotional Range", text: "Your speech demonstrated..." },
//         { category: "Gesture Effectiveness", text: "Your hand gestures were..." },
//         { category: "Facial Expressions", text: "Your facial expressions..." },
//         { category: "Overall Impact", text: "The combination of..." }
//     ]
// };
// updateVisualAnalysis(visualData);