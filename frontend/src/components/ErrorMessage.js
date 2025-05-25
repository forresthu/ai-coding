import React from 'react';
import './ErrorMessage.css';

const ErrorMessage = ({ message, onRetry }) => {
    return (
        <div className="error">
            <h3>Error Loading Data</h3>
            <p>{message}</p>
            <button onClick={onRetry} className="retry-button">
                Retry
            </button>
        </div>
    );
};

export default ErrorMessage;