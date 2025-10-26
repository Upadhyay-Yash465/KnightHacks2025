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
            document.getElementById('contextInput').classList.remove('hidden');
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
        document.getElementById('contextInput').classList.remove('hidden');
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

async function uploadRecording() {
    if (!recordedVideoBlob) {
        alert('No video available to upload');
        return;
    }

    const uploadProgress = document.getElementById('uploadProgress');
    const previewActions = document.getElementById('previewActions');
    const reportContent = document.getElementById('report-content');
    const contextInput = document.getElementById('speechContext');
    
    const context = contextInput ? contextInput.value : '';
    
    previewActions.classList.add('hidden');
    uploadProgress.classList.remove('hidden');
    
    try {
        // Create FormData and append video + context
        const formData = new FormData();
        formData.append('video', recordedVideoBlob, 'speech.webm');
        formData.append('context', context);
        
        // Call backend API
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        const analysisData = await response.json();
        
        // Populate frontend with results
        populateAnalysisResults(analysisData);
        
        uploadProgress.classList.add('hidden');
        if (reportContent) {
            reportContent.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error uploading and analyzing:', error);
        uploadProgress.classList.add('hidden');
        alert('Error analyzing your speech. Please ensure the backend server is running and try again.');
    }
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
    const contextInput = document.getElementById('contextInput');
    const speechContext = document.getElementById('speechContext');
    
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
    contextInput.classList.add('hidden');
    if (speechContext) {
        speechContext.value = '';
    }
    
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

// Store analysis data globally for actionable advice requests
window.currentAnalysisData = null;

// Populate all analysis results from backend
function populateAnalysisResults(data) {
    window.currentAnalysisData = data;
    
    // Populate transcription
    if (data.transcription) {
        const transcriptionText = document.getElementById('transcriptionText');
        if (transcriptionText) {
            transcriptionText.innerHTML = `<p>${data.transcription.text}</p>`;
        }
    }
    
    // Populate voice analysis
    if (data.voice) {
        const voice = data.voice;
        
        // Update metric values and scores
        updateMetric('prosodyValue', getQualityLabel(voice.prosody));
        updateMetric('prosodyScore', `${voice.prosody.toFixed(1)}/10`);
        
        updateMetric('toneValue', getQualityLabel(voice.volume));
        updateMetric('toneScore', `${voice.volume.toFixed(1)}/10`);
        
        updateMetric('pitchValue', getQualityLabel(voice.pitch));
        updateMetric('pitchScore', `${voice.pitch.toFixed(1)}/10`);
        
        updateMetric('speedValue', getQualityLabel(voice.speed));
        updateMetric('speedScore', `${voice.speed.toFixed(1)}/10`);
        
        // Generate and populate dynamic explanations
        updateMetric('prosodyExplanation', generateAudioExplanation('Prosody', voice.prosody));
        updateMetric('toneExplanation', generateAudioExplanation('Volume', voice.volume));
        updateMetric('pitchExplanation', generateAudioExplanation('Pitch', voice.pitch));
        updateMetric('speedExplanation', generateAudioExplanation('Speed', voice.speed));
    }
    
    // Populate emotion analysis
    if (data.emotions) {
        updateElement('emotionRating', `${data.emotions.overall_rating.toFixed(1)}/10`);
        updateElement('emotionDescription', getQualityLabel(data.emotions.overall_rating));
        
        // Populate gesture rating if available
        if (data.emotions.gesture_rating !== undefined) {
            updateElement('gestureRating', `${data.emotions.gesture_rating.toFixed(1)}/10`);
            updateElement('gestureDescription', data.emotions.gesture_description || '');
        }
        
        // Convert timeline data to graph format
        const emotionGraphData = convertEmotionTimelineToGraph(data.emotions.timeline);
        updateEmotionGraph(emotionGraphData);
    }
}

// Convert numeric score to quality label
function getQualityLabel(score) {
    if (score >= 9) return 'Excellent';
    if (score >= 8) return 'Very Good';
    if (score >= 7) return 'Good';
    if (score >= 6) return 'Moderate';
    if (score >= 5) return 'Fair';
    return 'Needs Improvement';
}

// Generate dynamic audio metric explanations based on score
function generateAudioExplanation(metricName, score) {
    const explanations = {
        'Prosody': {
            high: "Your speech rhythm and intonation patterns are excellent, creating engaging delivery with natural emphasis on key points. This dynamic prosody keeps your audience interested.",
            medium: "Your speech rhythm shows good variation with room for improvement. Consider practicing emphasizing key words and varying your intonation to add more dynamism to your delivery.",
            low: "Your speech rhythm could benefit from more variation. Practice varying your intonation and adding pauses for emphasis to create a more engaging delivery pattern."
        },
        'Volume': {
            high: "Your volume consistency is excellent, maintaining steady projection throughout. This creates a confident and professional impression while ensuring clear audibility.",
            medium: "Your volume is generally consistent with minor fluctuations. Work on maintaining steady projection, especially during longer sentences, to ensure all content is equally audible.",
            low: "Your volume shows noticeable inconsistency. Practice breathing exercises and projection techniques to maintain steady volume throughout your speech for better clarity."
        },
        'Pitch': {
            high: "Your vocal pitch variation is optimal, creating natural expressiveness while avoiding monotony. This engaging pitch range maintains listener interest throughout your presentation.",
            medium: "Your pitch variation is adequate but could be more dynamic. Try expanding your vocal range and varying pitch more deliberately to emphasize important points.",
            low: "Your pitch tends toward monotone, which can reduce engagement. Practice vocal exercises to expand your range and consciously vary pitch to add emotion and emphasis."
        },
        'Speed': {
            high: "Your speaking pace is well-balanced, allowing listeners to absorb information while maintaining momentum. This optimal speed demonstrates confidence and consideration for your audience.",
            medium: "Your speaking speed is reasonable but could be optimized. Be mindful of pacing, especially during complex explanations, to ensure comprehension without losing energy.",
            low: "Your speaking pace needs adjustment. If too fast, practice pausing for emphasis; if too slow, work on maintaining energy and momentum to keep your audience engaged."
        }
    };
    
    const category = score >= 8 ? 'high' : (score >= 6 ? 'medium' : 'low');
    return explanations[metricName]?.[category] || 'Your performance in this metric has been analyzed.';
}

// Convert emotion timeline to graph format
function convertEmotionTimelineToGraph(timeline) {
    const graphData = [];
    
    timeline.forEach((entry, index) => {
        // For each emotion in the entry, create a data point
        const emotions = ['Happy', 'Angry', 'Disgust', 'Fear', 'Surprise', 'Sad', 'Neutral'];
        emotions.forEach(emotion => {
            if (entry[emotion] && entry[emotion] > 0) {
                graphData.push({
                    xPosition: (index / (timeline.length - 1)) * 100,
                    yPosition: 100 - entry[emotion],
                    time: entry.time,
                    emotion: emotion,
                    intensity: entry[emotion]
                });
            }
        });
    });
    
    return graphData;
}

// Handle actionable advice button clicks
async function getActionableAdvice(agentType) {
    if (!window.currentAnalysisData) {
        showAdviceModal('Error', 'Please analyze your speech first before requesting advice.');
        return;
    }
    
    // Determine modal title based on agent type
    let modalTitle = 'Actionable Advice';
    if (agentType === 'transcriber') {
        modalTitle = 'Speech Content Advice';
    } else if (agentType === 'voice') {
        modalTitle = 'Voice & Delivery Advice';
    } else if (agentType === 'emotion') {
        modalTitle = 'Expression & Body Language Advice';
    }
    
    // Show modal with loading state
    showAdviceModal(modalTitle, null, true);
    
    try {
        const contextInput = document.getElementById('speechContext');
        const context = contextInput ? contextInput.value : '';
        
        const response = await fetch('http://localhost:8000/actionable-advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_type: agentType,
                analysis_data: window.currentAnalysisData,
                context: context
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get advice: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // If emotion advice and breakdown is available, populate the breakdown sections
        if (agentType === 'emotion' && result.breakdown) {
            updateElement('emotionalRangeText', result.breakdown.emotional_range);
            updateElement('gestureEffectivenessText', result.breakdown.gesture_effectiveness);
            updateElement('facialExpressionsText', result.breakdown.facial_expressions);
            updateElement('overallImpactText', result.breakdown.overall_impact);
        }
        
        // Show advice in modal
        showAdviceModal(modalTitle, result.advice);
        
    } catch (error) {
        console.error('Error getting actionable advice:', error);
        showAdviceModal('Error', `Failed to generate advice. Please try again.\n\nError: ${error.message}`);
    }
}

// Show advice modal
function showAdviceModal(title, content, loading = false) {
    const modal = document.getElementById('adviceModal');
    const modalTitle = document.getElementById('adviceModalTitle');
    const modalBody = document.getElementById('adviceModalBody');
    
    if (!modal || !modalTitle || !modalBody) {
        console.error('Modal elements not found');
        return;
    }
    
    // Set title
    modalTitle.textContent = title;
    
    // Set content or show loading
    if (loading) {
        modalBody.innerHTML = `
            <div class="advice-loading">
                <div class="spinner"></div>
                <p>Generating personalized advice...</p>
            </div>
        `;
    } else {
        modalBody.innerHTML = `<div class="advice-content">${formatAdviceContent(content)}</div>`;
    }
    
    // Show modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Close advice modal
function closeAdviceModal() {
    const modal = document.getElementById('adviceModal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// Format advice content (convert markdown-like formatting to HTML)
function formatAdviceContent(text) {
    if (!text) return '';
    
    // Convert markdown-style formatting to HTML
    let formatted = text
        // Convert **bold** to <strong>
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Convert numbered lists
        .replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>')
        // Convert bullet points
        .replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>')
        // Convert line breaks to paragraphs
        .split('\n\n')
        .map(para => {
            if (para.trim().startsWith('<li>')) {
                return '<ul>' + para + '</ul>';
            }
            return '<p>' + para.replace(/\n/g, '<br>') + '</p>';
        })
        .join('');
    
    return formatted;
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAdviceModal();
    }
});