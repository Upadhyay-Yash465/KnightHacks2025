import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

const Report = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const data = location.state || {};

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
              Analysis Report
            </h1>
            <div className="w-20"></div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-50 mb-6">
            Your Speech Analysis
          </h2>
          <p className="text-xl text-gray-300">
            Here's your personalized feedback and recommendations
          </p>
        </div>

        {/* Analysis Results */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <h3 className="text-xl font-semibold text-gray-100">Strengths</h3>
            </div>
            <ul className="space-y-2 text-gray-300">
              <li>• Clear pronunciation</li>
              <li>• Good pacing</li>
              <li>• Confident delivery</li>
            </ul>
          </div>

          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <AlertCircle className="w-6 h-6 text-yellow-500" />
              <h3 className="text-xl font-semibold text-gray-100">Areas for Improvement</h3>
            </div>
            <ul className="space-y-2 text-gray-300">
              <li>• Reduce filler words</li>
              <li>• Vary your tone</li>
              <li>• Add more pauses</li>
            </ul>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="text-center space-x-4">
          <button
            onClick={() => navigate('/record')}
            className="btn-primary"
          >
            Record Again
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default Report;
