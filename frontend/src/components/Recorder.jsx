import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Play, Square, Upload } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'https://your-cloud-run-url.run.app';

const Recorder = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [recordingBlob, setRecordingBlob] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true, 
        video: true 
      });
      
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      const chunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setRecordingBlob(blob);
        setRecordedChunks(chunks);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordedChunks([]);
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      console.error('Error starting recording:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      setIsRecording(false);
      setIsPaused(false);
    }
  }, [isRecording]);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
  }, [isRecording, isPaused]);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    }
  }, [isRecording, isPaused]);

  const uploadRecording = async () => {
    if (!recordingBlob) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", recordingBlob, "speech.webm");

      const response = await axios.post(`${API_BASE}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onRecordingComplete(response.data);
    } catch (err) {
      setError('Failed to upload recording. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const resetRecording = () => {
    setRecordingBlob(null);
    setRecordedChunks([]);
    setError(null);
  };

  return (
    <div className="card-elevated max-w-2xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center space-x-2 mb-6">
          <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
          <span className="text-orange-500 font-medium text-sm uppercase tracking-wider">Live Recording</span>
        </div>
        <h2 className="text-3xl md:text-4xl font-bold text-gray-50 mb-4">
          Record Your Speech
        </h2>
        <p className="text-lg text-gray-300 leading-relaxed">
          Click the microphone to start recording your public speaking practice
        </p>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500/30 text-red-300 px-6 py-4 rounded-xl mb-8">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="font-medium">{error}</span>
          </div>
        </div>
      )}

      <div className="flex flex-col items-center space-y-6">
        {/* Recording Controls */}
        {!recordingBlob && (
          <div className="flex items-center space-x-4">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="btn-primary flex items-center space-x-2 text-lg px-8 py-4"
              >
                <Mic className="w-6 h-6" />
                <span>Start Recording</span>
              </button>
            ) : (
              <div className="flex items-center space-x-4">
                <button
                  onClick={isPaused ? resumeRecording : pauseRecording}
                  className="btn-secondary flex items-center space-x-2 px-6 py-3"
                >
                  {isPaused ? <Play className="w-5 h-5" /> : <Square className="w-5 h-5" />}
                  <span>{isPaused ? 'Resume' : 'Pause'}</span>
                </button>
                <button
                  onClick={stopRecording}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
                >
                  <MicOff className="w-5 h-5" />
                  <span>Stop Recording</span>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Recording Status */}
        {isRecording && (
          <div className="flex items-center space-x-3 text-orange-500">
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
            <span className="font-medium text-lg">
              {isPaused ? 'Recording Paused' : 'Recording...'}
            </span>
          </div>
        )}

        {/* Recording Preview and Upload */}
        {recordingBlob && (
          <div className="w-full space-y-6">
            <div className="card bg-gradient-to-r from-orange-500/10 to-blue-500/10 border-orange-500/20">
              <h3 className="text-xl font-semibold text-gray-100 mb-2">Recording Complete!</h3>
              <p className="text-gray-300">
                Duration: {Math.round(recordingBlob.size / 1000)} KB
              </p>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={uploadRecording}
                disabled={isUploading}
                className="btn-primary flex items-center space-x-2 flex-1 justify-center"
              >
                <Upload className="w-5 h-5" />
                <span>{isUploading ? 'Uploading...' : 'Upload & Analyze'}</span>
              </button>
              
              <button
                onClick={resetRecording}
                disabled={isUploading}
                className="btn-secondary flex items-center space-x-2 px-6"
              >
                <span>Record Again</span>
              </button>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="w-full">
            <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20">
              <div className="flex items-center space-x-4">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-100 font-medium text-lg">
                  Analyzing your speech...
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recorder;
