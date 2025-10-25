// SpeechCoach AI Frontend JavaScript

class SpeechCoachApp {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationId = null;
        this.apiBaseUrl = 'http://localhost:8002';
        
        this.initializeApp();
    }

    initializeApp() {
        this.setupEventListeners();
        this.setupNavigation();
        this.initializeCharts();
        this.loadProgressData();
        this.setupAnimations();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('audioFileInput');
        const browseBtn = document.getElementById('browseBtn');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        browseBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Recording
        const recordBtn = document.getElementById('recordBtn');
        const stopRecordBtn = document.getElementById('stopRecordBtn');

        recordBtn.addEventListener('click', this.startRecording.bind(this));
        stopRecordBtn.addEventListener('click', this.stopRecording.bind(this));

        // Text analysis
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        analyzeTextBtn.addEventListener('click', this.analyzeText.bind(this));

        // Start analysis button
        const startAnalysisBtn = document.getElementById('startAnalysisBtn');
        startAnalysisBtn.addEventListener('click', () => {
            document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
        });
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('section[id]');

        // Smooth scrolling
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Active navigation highlighting
        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (window.pageYOffset >= sectionTop - 200) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processAudioFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processAudioFile(file);
        }
    }

    async processAudioFile(file) {
        if (!file.type.startsWith('audio/')) {
            this.showError('Please select a valid audio file.');
            return;
        }

        this.showLoading();
        
        try {
            const formData = new FormData();
            formData.append('audio_file', file);

            const response = await fetch(`${this.apiBaseUrl}/analyze-speech`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayResults(result);
            this.saveSession(result);
            this.showSuccess('Audio analysis completed successfully!');
            
        } catch (error) {
            console.error('Error analyzing audio:', error);
            this.showError('Failed to analyze audio file. Please try again.', this.processAudioFile.bind(this, file));
        } finally {
            this.hideLoading();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.processAudioFile(audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateRecordingUI();
            this.startAudioVisualization(stream);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Failed to access microphone. Please check permissions.');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI();
            this.stopAudioVisualization();
        }
    }

    updateRecordingUI() {
        const recordBtn = document.getElementById('recordBtn');
        const recordingStatus = document.getElementById('recordingStatus');
        const audioVisualizer = document.getElementById('audioVisualizer');

        if (this.isRecording) {
            recordBtn.style.display = 'none';
            recordingStatus.style.display = 'flex';
            audioVisualizer.style.display = 'block';
        } else {
            recordBtn.style.display = 'flex';
            recordingStatus.style.display = 'none';
            audioVisualizer.style.display = 'none';
        }
    }

    startAudioVisualization(stream) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        const source = this.audioContext.createMediaStreamSource(stream);
        
        source.connect(this.analyser);
        this.analyser.fftSize = 256;
        
        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
        
        this.drawVisualization();
    }

    stopAudioVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
    }

    drawVisualization() {
        if (!this.isRecording) return;

        this.animationId = requestAnimationFrame(() => this.drawVisualization());
        
        this.analyser.getByteFrequencyData(this.dataArray);
        
        const canvas = document.getElementById('visualizerCanvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        ctx.clearRect(0, 0, width, height);
        
        const barWidth = (width / this.dataArray.length) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < this.dataArray.length; i++) {
            barHeight = (this.dataArray[i] / 255) * height;
            
            const gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
            gradient.addColorStop(0, '#6366f1');
            gradient.addColorStop(1, '#ec4899');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }

    async analyzeText() {
        const textInput = document.getElementById('textInput');
        const text = textInput.value.trim();

        if (!text) {
            this.showError('Please enter some text to analyze.');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze-text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayResults(result, true);
            this.showSuccess('Text analysis completed successfully!');
            
        } catch (error) {
            console.error('Error analyzing text:', error);
            this.showError('Failed to analyze text. Please try again.', this.analyzeText.bind(this));
        } finally {
            this.hideLoading();
        }
    }

    displayResults(data, isTextOnly = false) {
        const resultsContainer = document.getElementById('resultsContainer');
        
        // Show transcription if available
        if (!isTextOnly && data.transcription) {
            document.getElementById('transcriptionText').textContent = data.transcription.text;
            document.getElementById('transcriptionLanguage').textContent = `Language: ${data.transcription.language}`;
            document.getElementById('transcriptionDuration').textContent = `Duration: ${data.transcription.duration}s`;
            
            const confidenceBadge = document.getElementById('confidenceBadge');
            const confidence = Math.round(data.transcription.confidence * 100);
            confidenceBadge.textContent = `${confidence}% confidence`;
            confidenceBadge.style.background = confidence > 80 ? '#10b981' : confidence > 60 ? '#f59e0b' : '#ef4444';
        } else {
            // Hide transcription card for text-only analysis
            const transcriptionCard = document.querySelector('.transcription-card');
            if (transcriptionCard) {
                transcriptionCard.style.display = 'none';
            }
        }

        // Display analysis results
        const analysis = data.analysis;
        
        // Clarity score
        document.getElementById('clarityScore').textContent = analysis.clarity_score;
        const clarityScoreFill = document.getElementById('clarityScoreFill');
        clarityScoreFill.style.width = `${(analysis.clarity_score / 10) * 100}%`;
        
        // Filler words
        document.getElementById('fillerCount').textContent = analysis.filler_count;
        document.getElementById('fillerDensity').textContent = `${analysis.filler_density}%`;
        
        // Word count
        document.getElementById('wordCount').textContent = analysis.total_words;
        const wordRate = isTextOnly ? 'N/A' : Math.round(analysis.total_words / (data.transcription.duration / 60));
        document.getElementById('wordRate').textContent = wordRate;
        
        // Suggestions
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';
        analysis.suggestions.forEach((suggestion, index) => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item fade-in-up';
            suggestionItem.style.animationDelay = `${index * 0.1}s`;
            suggestionItem.innerHTML = `
                <h4>${index + 1}. ${suggestion}</h4>
            `;
            suggestionsList.appendChild(suggestionItem);
        });
        
        // Summary
        document.getElementById('summaryText').textContent = analysis.summary;
        
        // Create filler chart
        this.createFillerChart(analysis.filler_count, analysis.total_words);
        
        // Show results with animation
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
        
        // Animate cards
        const cards = resultsContainer.querySelectorAll('.result-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    createFillerChart(fillerCount, totalWords) {
        const ctx = document.getElementById('fillerChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.fillerChart) {
            this.fillerChart.destroy();
        }
        
        const fillerPercentage = totalWords > 0 ? (fillerCount / totalWords) * 100 : 0;
        const cleanPercentage = 100 - fillerPercentage;
        
        this.fillerChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Clean Words', 'Filler Words'],
                datasets: [{
                    data: [cleanPercentage, fillerPercentage],
                    backgroundColor: ['#10b981', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    initializeCharts() {
        // Initialize progress chart
        const progressCtx = document.getElementById('progressChart');
        if (progressCtx) {
            this.progressChart = new Chart(progressCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Clarity Score',
                        data: [6.5, 7.2, 7.8, 8.5],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Filler Count',
                        data: [12, 9, 6, 3],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            min: 0,
                            max: 10
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            min: 0,
                            max: 15,
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        }
    }

    loadProgressData() {
        // Load saved sessions from localStorage
        const savedSessions = JSON.parse(localStorage.getItem('speechSessions') || '[]');
        const sessionsList = document.getElementById('sessionsList');
        
        if (savedSessions.length > 0) {
            sessionsList.innerHTML = '';
            savedSessions.slice(-5).reverse().forEach(session => {
                const sessionItem = document.createElement('div');
                sessionItem.className = 'session-item';
                sessionItem.innerHTML = `
                    <div class="session-date">${new Date(session.timestamp).toLocaleDateString()}</div>
                    <div class="session-score">${session.clarityScore}/10</div>
                    <div class="session-fillers">${session.fillerCount} fillers</div>
                `;
                sessionsList.appendChild(sessionItem);
            });
        }
    }

    saveSession(data) {
        const session = {
            timestamp: new Date().toISOString(),
            clarityScore: data.analysis.clarity_score,
            fillerCount: data.analysis.filler_count,
            wordCount: data.analysis.total_words
        };
        
        const savedSessions = JSON.parse(localStorage.getItem('speechSessions') || '[]');
        savedSessions.push(session);
        localStorage.setItem('speechSessions', JSON.stringify(savedSessions));
        
        // Update progress display
        this.loadProgressData();
    }

    showLoading() {
        document.getElementById('loadingState').style.display = 'block';
        document.getElementById('resultsContainer').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loadingState').style.display = 'none';
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => errorDiv.remove(), 300);
        }, 4000);
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, observerOptions);

        // Observe all cards and sections
        document.querySelectorAll('.result-card, .tip-card, .progress-card').forEach(el => {
            observer.observe(el);
        });

        // Add hover effects to interactive elements
        this.addHoverEffects();
    }

    addHoverEffects() {
        // Add ripple effect to buttons
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to analyze text
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const textInput = document.getElementById('textInput');
                if (textInput === document.activeElement) {
                    this.analyzeText();
                }
            }
            
            // Space to start/stop recording (when not in input fields)
            if (e.key === ' ' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
                e.preventDefault();
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            }
            
            // Escape to stop recording
            if (e.key === 'Escape' && this.isRecording) {
                this.stopRecording();
            }
        });
    }

    // Add typing animation for suggestions
    typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    // Enhanced error handling with retry options
    showError(message, retryCallback = null) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
        `;
        
        errorDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
            ${retryCallback ? '<button onclick="this.parentElement.remove(); ' + retryCallback.name + '()" style="margin-top: 8px; padding: 4px 8px; background: rgba(255,255,255,0.2); border: none; border-radius: 4px; color: white; cursor: pointer;">Retry</button>' : ''}
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => errorDiv.remove(), 300);
            }
        }, 5000);
    }

    // Add success notifications
    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-notification';
        successDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
        `;
        
        successDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            if (successDiv.parentElement) {
                successDiv.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => successDiv.remove(), 300);
            }
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SpeechCoachApp();
});

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
