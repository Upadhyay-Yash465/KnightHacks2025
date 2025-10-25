import React, { useState, useRef, useCallback } from 'react';
import styled from 'styled-components';
import Webcam from 'react-webcam';
import { AudioRecorder } from 'react-audio-voice-recorder';
import { FaPlay, FaStop, FaDownload, FaUpload } from 'react-icons/fa';
import { motion } from 'framer-motion';

const RecordingContainer = styled.div`
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const VideoContainer = styled.div`
  position: relative;
  margin-bottom: 30px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
`;

const WebcamStyled = styled(Webcam)`
  width: 100%;
  max-width: 600px;
  height: auto;
  transform: scaleX(-1); /* Mirror the camera preview */
`;

const VideoPreview = styled.video`
  width: 100%;
  max-width: 600px;
  height: auto;
  transform: scaleX(-1); /* Mirror the recorded video preview */
  border-radius: 15px;
`;

const ControlsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
`;

const RecordButton = styled(motion.button)`
  background: ${props => props.isRecording ? '#ff4757' : '#2ed573'};
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const DownloadButton = styled(motion.button)`
  background: #3742fa;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background: #2f3542;
    transform: translateY(-2px);
  }
`;

const UploadButton = styled(motion.button)`
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background: #ee5a52;
    transform: translateY(-2px);
  }
`;

const StatusText = styled.div`
  color: #666;
  font-size: 0.9rem;
  margin-top: 10px;
`;

const RecordingTime = styled.div`
  color: #ff4757;
  font-size: 1.2rem;
  font-weight: bold;
  margin: 10px 0;
`;

const FileInfo = styled.div`
  background: #f8f9fa;
  border-radius: 10px;
  padding: 15px;
  margin: 20px 0;
  text-align: left;
`;

const RecordingInterface = ({ onFilesRecorded, onRecordingStateChange }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedVideo, setRecordedVideo] = useState(null);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const fileInputRef = useRef(null);

  const startRecording = useCallback(() => {
    if (webcamRef.current) {
      const stream = webcamRef.current.video.srcObject;
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      onRecordingStateChange(true);
      
      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          const videoBlob = event.data;
          const videoUrl = URL.createObjectURL(videoBlob);
          setRecordedVideo(videoUrl);
          
          // Notify parent component about recorded files
          onFilesRecorded({
            video: videoBlob,
            audio: recordedAudio,
            videoUrl: videoUrl
          });
        }
      };
      
      mediaRecorder.onstop = () => {
        clearInterval(interval);
        onRecordingStateChange(false);
      };
    }
  }, [recordedAudio, onFilesRecorded, onRecordingStateChange]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, []);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const videoUrl = URL.createObjectURL(file);
      setRecordedVideo(videoUrl);
      
      // Notify parent component about uploaded file
      onFilesRecorded({
        video: file,
        audio: recordedAudio,
        videoUrl: videoUrl
      });
    }
  };

  const clearRecording = () => {
    setRecordedVideo(null);
    setRecordedAudio(null);
    setIsRecording(false);
    setRecordingTime(0);
    onFilesRecorded({ video: null, audio: null });
  };

  const downloadVideo = () => {
    if (recordedVideo) {
      const link = document.createElement('a');
      link.href = recordedVideo;
      link.download = `recording-${Date.now()}.webm`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleAudioRecording = (audioBlob) => {
    setRecordedAudio(audioBlob);
    
    // Notify parent component about audio recording
    onFilesRecorded({
      video: recordedVideo,
      audio: audioBlob,
      videoUrl: recordedVideo
    });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <RecordingContainer>
      <h2>🎤 Record Your Speech</h2>
      <p>Record a video of yourself speaking to prepare for transcription and analysis</p>
      
      <VideoContainer>
        {!recordedVideo ? (
          <WebcamStyled
            ref={webcamRef}
            audio={true}
            videoConstraints={{
              width: 1280,
              height: 720,
              facingMode: "user"
            }}
          />
        ) : (
          <VideoPreview
            src={recordedVideo}
            controls
            autoPlay
            muted
          />
        )}
        
        {isRecording && (
          <RecordingTime>
            🔴 Recording: {formatTime(recordingTime)}
          </RecordingTime>
        )}
        
        <StatusText>
          {!recordedVideo ? "Camera Preview (Mirrored)" : "Recorded Video (Mirrored)"}
        </StatusText>
      </VideoContainer>

      <ControlsContainer>
        {!isRecording ? (
          <RecordButton
            onClick={startRecording}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaPlay />
            Start Recording
          </RecordButton>
        ) : (
          <RecordButton
            onClick={stopRecording}
            isRecording={true}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaStop />
            Stop Recording
          </RecordButton>
        )}

        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <UploadButton
            onClick={() => fileInputRef.current?.click()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaUpload />
            Upload Video
          </UploadButton>

          {recordedVideo && (
            <DownloadButton
              onClick={downloadVideo}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FaDownload />
              Download Video
            </DownloadButton>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />

        <div style={{ marginTop: '20px' }}>
          <h4>🎵 Audio Recording (Optional)</h4>
          <AudioRecorder
            onRecordingComplete={handleAudioRecording}
            audioTrackConstraints={{
              noiseSuppression: true,
              echoCancellation: true,
            }}
            downloadOnSavePress={true}
            downloadFileExtension="webm"
          />
        </div>

        {recordedVideo && (
          <FileInfo>
            <h4>📁 File Information</h4>
            <p><strong>Video:</strong> Ready for transcription</p>
            <p><strong>Format:</strong> WebM (VP9 codec)</p>
            <p><strong>Audio:</strong> {recordedAudio ? 'Included' : 'Not recorded'}</p>
            <p><strong>Status:</strong> ✅ Ready for analysis</p>
          </FileInfo>
        )}
      </ControlsContainer>
    </RecordingContainer>
  );
};

export default RecordingInterface;