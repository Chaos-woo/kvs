from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import time
import json
import traceback
import sys
from pathlib import Path

# Add the current directory to the Python path if it's not already there
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from routes.api import api_bp
from routes.kv import kv_bp
from models import Base, engine
from models.key_value import create_fts5_table, Key, Val, KVRelation
from utils.logger import api_logger, error_logger

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
Base.metadata.create_all(bind=engine)

# Create FTS5 virtual table
create_fts5_table()

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api/v1')
app.register_blueprint(kv_bp, url_prefix='/api/v1')

# Logging middleware
@app.before_request
def before_request():
    # Skip logging for non-API routes
    if not request.path.startswith('/api'):
        return

    # Generate a unique request ID
    request_id = str(time.time())
    g.request_id = request_id
    g.start_time = time.time()

    # Log request
    request_data = {
        'request_id': request_id,
        'method': request.method,
        'url': request.url,
        'path': request.path,
        'args': request.args.to_dict(),
    }

    # Log request body for POST/PUT/PATCH
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            request_data['json'] = request.get_json()
        except Exception as e:
            request_data['json_error'] = str(e)

    api_logger.info(f"API Request: {json.dumps(request_data, default=str)}")

@app.after_request
def after_request(response):
    # Skip logging for non-API routes
    if not request.path.startswith('/api'):
        return response

    # Log response
    try:
        end_time = time.time()
        response_time_ms = round((end_time - g.start_time) * 1000, 2)

        response_data = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'status_code': response.status_code,
            'response_time_ms': response_time_ms,
        }

        # Try to parse response JSON
        try:
            response_data['response'] = json.loads(response.get_data(as_text=True))
        except:
            response_data['response'] = '[non-JSON response]'

        api_logger.info(f"API Response: {json.dumps(response_data, default=str)}")
    except Exception as e:
        api_logger.error(f"Error logging response: {str(e)}")

    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    error_data = {
        'request_id': getattr(g, 'request_id', 'unknown'),
        'error': str(e),
        'traceback': traceback.format_exc(),
    }
    error_logger.error(f"Unhandled Exception: {json.dumps(error_data, default=str)}")

    # Return a JSON response
    return jsonify({
        "status": "error",
        "message": str(e)
    }), 500

@app.route('/')
def index():
    return {"status": "ok", "message": "KVs API is running"}

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the Flask application"""
    try:
        # Get the shutdown function from the Werkzeug server
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            # If we're not running with the Werkzeug server, try to exit
            import os
            import signal
            api_logger.info("Shutting down Flask application via signal")
            os.kill(os.getpid(), signal.SIGTERM)
            return {"status": "ok", "message": "Shutting down..."}
        else:
            api_logger.info("Shutting down Flask application via Werkzeug")
            func()
            return {"status": "ok", "message": "Shutting down..."}
    except Exception as e:
        error_logger.error(f"Error during shutdown: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
