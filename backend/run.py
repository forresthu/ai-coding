import os
from app import app

if __name__ == '__main__':
    # Set environment variables for development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting AI Models Dashboard Backend...")
    print("🌐 API will be available at: http://localhost:5000")
    print("📊 Frontend should connect to: http://localhost:5000/api")
    print("\n🔗 Available endpoints:")
    print("  - GET /api/health")
    print("  - GET /api/models")
    print("  - GET /api/models/<category>")
    print("  - GET /api/model/<model_id>")
    
    app.run(host='0.0.0.0', port=5000, debug=True)