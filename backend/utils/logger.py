import logging
import json
import traceback
from functools import wraps
from flask import request, g
import time
import sys
from pathlib import Path

# Add the parent directory to the Python path if it's not already there
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import API_LOG_FILE, ERROR_LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configure API logger
api_logger = logging.getLogger('api')
api_logger.setLevel(getattr(logging, LOG_LEVEL))
api_handler = logging.FileHandler(API_LOG_FILE)
api_handler.setFormatter(logging.Formatter(LOG_FORMAT))
api_logger.addHandler(api_handler)

# Configure error logger
error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(ERROR_LOG_FILE)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
error_logger.addHandler(error_handler)

# Add console handler for development
if LOG_LEVEL == 'DEBUG':
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    api_logger.addHandler(console_handler)
    error_logger.addHandler(console_handler)

def log_api_call(func):
    """
    Decorator to log API calls with request and response details
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate a unique request ID
        request_id = str(time.time())
        g.request_id = request_id

        # Log request
        request_data = {
            'request_id': request_id,
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'args': request.args.to_dict(),
        }

        # Log request body for POST/PUT/PATCH
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            request_data['json'] = request.get_json()

        api_logger.info(f"API Request: {json.dumps(request_data, default=str)}")

        start_time = time.time()
        try:
            # Execute the API function
            response = func(*args, **kwargs)

            # Log response
            end_time = time.time()
            response_data = {
                'request_id': request_id,
                'status_code': response[1] if isinstance(response, tuple) else 200,
                'response_time_ms': round((end_time - start_time) * 1000, 2),
                'response': response[0].json if isinstance(response, tuple) else response.json
            }
            api_logger.info(f"API Response: {json.dumps(response_data, default=str)}")

            return response
        except Exception as e:
            # Log exception
            end_time = time.time()
            error_data = {
                'request_id': request_id,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'response_time_ms': round((end_time - start_time) * 1000, 2)
            }
            error_logger.error(f"API Exception: {json.dumps(error_data, default=str)}")
            api_logger.error(f"API Exception: {request_id} - {str(e)}")

            # Re-raise the exception to be handled by the route's exception handler
            raise

    return wrapper

def log_exception(e, context=None):
    """
    Log an exception with context information
    """
    error_data = {
        'request_id': getattr(g, 'request_id', 'unknown'),
        'error': str(e),
        'traceback': traceback.format_exc(),
        'context': context
    }
    error_logger.error(f"Exception: {json.dumps(error_data, default=str)}")
    api_logger.error(f"Exception: {getattr(g, 'request_id', 'unknown')} - {str(e)}")
