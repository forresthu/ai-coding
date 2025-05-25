import React from 'react';
import './ModelCard.css';

const getCompanyLogo = (company) => {
    const logos = {
        'OpenAI': '🤖',
        'Google': 'G',
        'Anthropic': 'A',
        'Meta': 'M',
        'Microsoft': '⚡',
        'Stability AI': 'S'
    };
    return logos[company] || '🔬';
};

const formatNumber = (num) => {
    if (num === 'N/A' || !num) return 'N/A';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
};

const ModelCard = ({ model, category, companyClass }) => {
    const openHuggingFaceLink = () => {
        window.open(`https://huggingface.co/${model.hf_id}`, '_blank');
    };

    const handleLinkClick = (e) => {
        e.stopPropagation();
    };

    return (
        <div
            className={`model-card ${companyClass}`}
            onClick={openHuggingFaceLink}
        >
            <div className="model-header">
                <div className="company-logo">
                    {getCompanyLogo(model.company)}
                </div>
                <div>
                    <div className="model-name">{model.display_name}</div>
                    <div className="company-name">{model.company}</div>
                </div>
            </div>

            <div className="model-description">
                {model.description || 'Advanced AI model with cutting-edge capabilities and performance.'}
            </div>

            <div className="model-stats">
                <div className="stat">
                    <div className="stat-value">{formatNumber(model.downloads)}</div>
                    <div className="stat-label">Downloads</div>
                </div>
                <div className="stat">
                    <div className="stat-value">{formatNumber(model.likes)}</div>
                    <div className="stat-label">Likes</div>
                </div>
            </div>

            <div className="model-tags">
                {model.tags && model.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="tag">{tag}</span>
                ))}
                {model.model_size !== 'N/A' && (
                    <span className="tag">{model.model_size}</span>
                )}
            </div>

            <a
                href={`https://huggingface.co/${model.hf_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="hf-link"
                onClick={handleLinkClick}
            >
                🤗 View on HF
            </a>
        </div>
    );
};

export default ModelCard;