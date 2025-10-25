import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mic, Target, Clock } from 'lucide-react';
import Recorder from '../components/Recorder';

const Record = () => {
  const navigate = useNavigate();

  const handleRecordingComplete = (data) => {
    navigate('/report', { state: data });
  };

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <div className="glass border-b border-dark-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="btn-ghost flex items-center space-x-2"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Home</span>
            </button>
            <h1 className="text-xl font-semibold text-gray-100">
              AI Public Speaking Coach
            </h1>
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Instructions */}
        <div className="mb-12">
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 mb-6">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
              <span className="text-orange-500 font-medium text-sm uppercase tracking-wider">Ready to Record</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-50 mb-6">
              Record Your Speech
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
              Practice your public speaking skills and get instant AI feedback on your performance
            </p>
          </div>

          {/* Tips Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="card text-center group hover:scale-105 transition-all duration-300">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-orange-500/20 to-orange-500/10 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                <Mic className="w-8 h-8 text-orange-500" />
              </div>
              <h3 className="text-xl font-semibold text-gray-100 mb-4">Speak Clearly</h3>
              <p className="text-gray-300 leading-relaxed">
                Enunciate your words and speak at a comfortable pace
              </p>
            </div>

            <div className="card text-center group hover:scale-105 transition-all duration-300">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500/20 to-blue-500/10 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                <Target className="w-8 h-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold text-gray-100 mb-4">Be Confident</h3>
              <p className="text-gray-300 leading-relaxed">
                Project your voice and maintain good posture
              </p>
            </div>

            <div className="card text-center group hover:scale-105 transition-all duration-300">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500/20 to-purple-500/10 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                <Clock className="w-8 h-8 text-purple-500" />
              </div>
              <h3 className="text-xl font-semibold text-gray-100 mb-4">Take Your Time</h3>
              <p className="text-gray-300 leading-relaxed">
                Don't rush - speak naturally and pause when needed
              </p>
            </div>
          </div>
        </div>

        {/* Recording Component */}
        <Recorder onRecordingComplete={handleRecordingComplete} />

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="card max-w-2xl mx-auto bg-gradient-to-r from-blue-500/5 to-purple-500/5 border-blue-500/20">
            <h3 className="text-xl font-semibold text-gray-100 mb-4">
              Privacy & Security
            </h3>
            <p className="text-gray-300 leading-relaxed">
              Your recordings are processed securely and are not stored permanently. 
              We only analyze your speech to provide feedback and then delete the audio data.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Record;
