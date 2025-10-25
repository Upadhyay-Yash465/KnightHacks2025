import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#1f2937', color: 'white', padding: '2rem' }}>
      <div style={{ maxWidth: '56rem', margin: '0 auto', textAlign: 'center' }}>
        <h1 style={{ fontSize: '3.75rem', fontWeight: 'bold', marginBottom: '2rem', color: '#f97316' }}>
          AI Public Speaking Coach
        </h1>
        <p style={{ fontSize: '1.25rem', color: '#d1d5db', marginBottom: '3rem' }}>
          Transform your speaking skills with intelligent feedback
        </p>
        <button
          onClick={() => navigate('/record')}
          style={{
            backgroundColor: '#f97316',
            color: 'white',
            fontWeight: 'bold',
            padding: '1rem 2rem',
            borderRadius: '0.5rem',
            fontSize: '1.125rem',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Start Recording
        </button>
      </div>
    </div>
  );
};

export default Home;
