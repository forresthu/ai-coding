import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
    return (
        <div className="loading">
            <div className="spinner"></div>
            <div>Loading models from Hugging Face...</div>
        </div>
    );
};

export default LoadingSpinner;