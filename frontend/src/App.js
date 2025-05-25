import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ModelCard from './components/ModelCard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

const API_BASE = process.env.NODE_ENV === 'production'
    ? 'https://ai-models-dashboard.uc.r.appspot.com/api'  // Your App Engine URL
    : 'http://localhost:5000/api';

// Or use environment variables
// const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const categoryConfig = {
    'language_models': {
        title: '💬 Large Language Models',
        companyMap: {
            'OpenAI': 'openai',
            'Google': 'google',
            'Anthropic': 'anthropic',
            'Meta': 'meta'
        }
    },
    'image_models': {
        title: '🎨 Image Generation',
        companyMap: {
            'Stability AI': 'stability',
            'OpenAI': 'openai'
        }
    },
    'code_models': {
        title: '💻 Code Generation',
        companyMap: {
            'Microsoft': 'microsoft',
            'Anthropic': 'anthropic'
        }
    }
};

function App() {
    const [models, setModels] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadModels = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE}/models`);
            setModels(response.data);
        } catch (err) {
            console.error('Error loading models:', err);
            setError('Unable to fetch model data. Please check if the backend server is running.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadModels();
    }, []);

    return (
        <div className="App">
            <div className="header">
                <h1>🤖 AI Models Dashboard</h1>
                <p>Live data from Hugging Face Hub</p>
            </div>

            {loading && <LoadingSpinner />}

            {error && <ErrorMessage message={error} onRetry={loadModels} />}

            {!loading && !error && (
                <div className="dashboard">
                    {Object.keys(categoryConfig).map(category => {
                        const categoryData = models[category];
                        const config = categoryConfig[category];

                        if (!categoryData || categoryData.length === 0) {
                            return null;
                        }

                        return (
                            <div key={category} className="category">
                                <h2 className="category-title">{config.title}</h2>
                                <div className="models-grid">
                                    {categoryData.map(model => (
                                        <ModelCard
                                            key={model.id}
                                            model={model}
                                            category={category}
                                            companyClass={config.companyMap[model.company] || 'default'}
                                        />
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default App;