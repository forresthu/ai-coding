from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
import logging

app = Flask(__name__)

# Configure CORS for production
if os.environ.get('GAE_ENV', '').startswith('standard'):
    # Production on App Engine
    CORS(app, origins=['https://a-test-6ef42.web.app'])
else:
    # Local development
    CORS(app)

# Configure logging for App Engine
if os.environ.get('GAE_ENV', '').startswith('standard'):
    # Production logging
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
else:
    # Local logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('api.log'),
            logging.StreamHandler()  # Also print to console
        ]
    )

logger = logging.getLogger(__name__)

# Hugging Face API configuration
HF_API_BASE = "https://huggingface.co/api"
HF_TOKEN = os.getenv('HF_TOKEN')  # Optional: for higher rate limits

# Cache to avoid hitting API too frequently
cache = {}
CACHE_DURATION = timedelta(hours=1)

def log_request(endpoint_name, **kwargs):
    """Log API request details"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_data = {
        'endpoint': endpoint_name,
        'method': request.method,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add any additional data passed to the function
    log_data.update(kwargs)
    
    logger.info(f"API Call: {log_data}")

def get_huggingface_model_info(model_id):
    """Fetch model information from Hugging Face API"""
    cache_key = f"model_{model_id}"
    
    # Check cache first
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if datetime.now() - timestamp < CACHE_DURATION:
            logger.info(f"Cache hit for model: {model_id}")
            return cached_data
    
    logger.info(f"Fetching data from Hugging Face API for model: {model_id}")
    
    try:
        # Get model info
        headers = {}
        if HF_TOKEN:
            headers['Authorization'] = f'Bearer {HF_TOKEN}'
        
        response = requests.get(f"{HF_API_BASE}/models/{model_id}", headers=headers)
        
        if response.status_code == 200:
            model_data = response.json()
            
            # Get additional stats
            downloads = model_data.get('downloads', 0)
            likes = model_data.get('likes', 0)
            created_at = model_data.get('createdAt', '')
            updated_at = model_data.get('lastModified', '')
            
            # Extract tags and pipeline info
            tags = model_data.get('tags', [])
            pipeline_tag = model_data.get('pipeline_tag', '')
            
            # Get model size if available
            model_size = 'Unknown'
            if 'siblings' in model_data:
                total_size = sum(file.get('size', 0) for file in model_data['siblings'])
                if total_size > 0:
                    model_size = format_bytes(total_size)
            
            processed_data = {
                'id': model_id,
                'downloads': downloads,
                'likes': likes,
                'tags': tags,
                'pipeline_tag': pipeline_tag,
                'model_size': model_size,
                'created_at': created_at,
                'updated_at': updated_at,
                'description': model_data.get('description', ''),
                'author': model_data.get('author', ''),
                'library_name': model_data.get('library_name', '')
            }
            
            # Cache the result
            cache[cache_key] = (processed_data, datetime.now())
            logger.info(f"Successfully fetched and cached data for model: {model_id}")
            return processed_data
        else:
            logger.warning(f"HF API returned status {response.status_code} for model: {model_id}")
            
    except Exception as e:
        logger.error(f"Error fetching model {model_id}: {str(e)}")
        return None

def format_bytes(bytes_count):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f}PB"

# Model mappings to Hugging Face model IDs
MODEL_MAPPINGS = {
    'language_models': {
        'gpt-4': {
            'hf_id': 'microsoft/DialoGPT-large',  # Placeholder since GPT-4 isn't on HF
            'company': 'OpenAI',
            'display_name': 'GPT-4 Turbo'
        },
        'gemini': {
            'hf_id': 'google/gemma-7b',
            'company': 'Google',
            'display_name': 'Gemini Ultra'
        },
        'claude': {
            'hf_id': 'anthropic/claude-instant-v1',  # Placeholder
            'company': 'Anthropic',
            'display_name': 'Claude 3 Opus'
        },
        'llama': {
            'hf_id': 'meta-llama/Llama-2-70b-hf',
            'company': 'Meta',
            'display_name': 'Llama 2 70B'
        }
    },
    'image_models': {
        'stable-diffusion': {
            'hf_id': 'stabilityai/stable-diffusion-xl-base-1.0',
            'company': 'Stability AI',
            'display_name': 'SDXL Turbo'
        },
        'dalle': {
            'hf_id': 'openai/clip-vit-base-patch32',  # Placeholder
            'company': 'OpenAI',
            'display_name': 'DALL-E 3'
        }
    },
    'code_models': {
        'copilot': {
            'hf_id': 'microsoft/CodeBERT-base',
            'company': 'Microsoft',
            'display_name': 'GitHub Copilot'
        },
        'claude-code': {
            'hf_id': 'codellama/CodeLlama-34b-Python-hf',
            'company': 'Anthropic',
            'display_name': 'Claude 3 (Code)'
        }
    }
}

@app.route('/api/models/<category>')
def get_models_by_category(category):
    """Get models for a specific category"""
    log_request('get_models_by_category', category=category)
    
    if category not in MODEL_MAPPINGS:
        logger.warning(f"Category not found: {category}")
        return jsonify({'error': 'Category not found'}), 404
    
    logger.info(f"Processing category: {category} with {len(MODEL_MAPPINGS[category])} models")
    
    models = []
    for model_key, model_info in MODEL_MAPPINGS[category].items():
        hf_data = get_huggingface_model_info(model_info['hf_id'])
        
        model_data = {
            'id': model_key,
            'display_name': model_info['display_name'],
            'company': model_info['company'],
            'hf_id': model_info['hf_id']
        }
        
        if hf_data:
            model_data.update({
                'downloads': hf_data['downloads'],
                'likes': hf_data['likes'],
                'model_size': hf_data['model_size'],
                'tags': hf_data['tags'],
                'description': hf_data['description'],
                'last_updated': hf_data['updated_at']
            })
        else:
            # Fallback data if HF API fails
            model_data.update({
                'downloads': 'N/A',
                'likes': 'N/A',
                'model_size': 'N/A',
                'tags': [],
                'description': 'Model information unavailable',
                'last_updated': 'N/A'
            })
        
        models.append(model_data)
    
    logger.info(f"Successfully processed {len(models)} models for category: {category}")
    return jsonify({'category': category, 'models': models})

@app.route('/api/models')
def get_all_models():
    """Get all models across categories"""
    log_request('get_all_models')
    
    logger.info(f"Fetching all models across {len(MODEL_MAPPINGS)} categories")
    
    all_models = {}
    
    for category in MODEL_MAPPINGS.keys():
        logger.info(f"Processing category: {category}")
        try:
            # Call the category endpoint internally
            with app.test_request_context(f'/api/models/{category}'):
                response = get_models_by_category(category)
                if hasattr(response, 'status_code') and response.status_code == 200:
                    all_models[category] = response.get_json()['models']
                else:
                    # Direct call since we're internal
                    models = []
                    for model_key, model_info in MODEL_MAPPINGS[category].items():
                        hf_data = get_huggingface_model_info(model_info['hf_id'])
                        
                        model_data = {
                            'id': model_key,
                            'display_name': model_info['display_name'],
                            'company': model_info['company'],
                            'hf_id': model_info['hf_id']
                        }
                        
                        if hf_data:
                            model_data.update({
                                'downloads': hf_data['downloads'],
                                'likes': hf_data['likes'],
                                'model_size': hf_data['model_size'],
                                'tags': hf_data['tags'],
                                'description': hf_data['description'],
                                'last_updated': hf_data['updated_at']
                            })
                        else:
                            model_data.update({
                                'downloads': 'N/A',
                                'likes': 'N/A',
                                'model_size': 'N/A',
                                'tags': [],
                                'description': 'Model information unavailable',
                                'last_updated': 'N/A'
                            })
                        
                        models.append(model_data)
                    
                    all_models[category] = models
        except Exception as e:
            logger.error(f"Error processing category {category}: {str(e)}")
            all_models[category] = []
    
    total_models = sum(len(models) for models in all_models.values())
    logger.info(f"Successfully fetched {total_models} total models across all categories")
    
    return jsonify(all_models)

@app.route('/api/model/<model_id>')
def get_model_details(model_id):
    """Get detailed information about a specific model"""
    log_request('get_model_details', model_id=model_id)
    
    logger.info(f"Looking for model details: {model_id}")
    
    # Find the model across all categories
    for category, models in MODEL_MAPPINGS.items():
        for key, model_info in models.items():
            if key == model_id:
                logger.info(f"Found model {model_id} in category {category}")
                hf_data = get_huggingface_model_info(model_info['hf_id'])
                
                if hf_data:
                    logger.info(f"Successfully retrieved details for model: {model_id}")
                    return jsonify({
                        'id': model_id,
                        'display_name': model_info['display_name'],
                        'company': model_info['company'],
                        'category': category,
                        **hf_data
                    })
                else:
                    logger.error(f"Model data unavailable for: {model_id}")
                    return jsonify({'error': 'Model data unavailable'}), 404
    
    logger.warning(f"Model not found: {model_id}")
    return jsonify({'error': 'Model not found'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    log_request('health_check')
    
    logger.info("Health check performed")
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.before_request
def before_request():
    """Log all incoming requests"""
    if request.endpoint:  # Only log actual endpoints, not static files
        logger.info(f"Incoming request: {request.method} {request.path} from {request.environ.get('REMOTE_ADDR', 'Unknown')}")

@app.after_request
def after_request(response):
    """Log response status"""
    if request.endpoint:
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

if __name__ == '__main__':
    logger.info("🚀 Starting AI Models Dashboard Backend...")
    logger.info("🌐 API will be available at: http://localhost:5000")
    logger.info("📊 Frontend should connect to: http://localhost:5000/api")
    logger.info("📝 Logging to console and api.log file")
    
    # This is used when running locally only
    app.run(host='127.0.0.1', port=8080, debug=True)