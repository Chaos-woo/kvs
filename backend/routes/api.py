from flask import Blueprint, jsonify, request
import sys
from pathlib import Path

# Add the parent directory to the Python path if it's not already there
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import using standard Python imports
from models import SessionLocal
# Import Theme directly from the module file
from models.theme import Theme

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the API"""
    return jsonify({
        "status": "ok",
        "message": "API is healthy"
    })

@api_bp.route('/tab1', methods=['GET'])
def tab1_test():
    """Test endpoint for tab1"""
    return jsonify({
        "status": "success",
        "message": "This is a test response from tab1 endpoint"
    })

@api_bp.route('/tab2', methods=['GET'])
def tab2_test():
    """Test endpoint for tab2"""
    return jsonify({
        "status": "success",
        "message": "This is a test response from tab2 endpoint"
    })

@api_bp.route('/theme', methods=['GET'])
def get_theme():
    """Get the current theme mode"""
    db = SessionLocal()
    try:
        theme_mode = Theme.get_current_theme(db)
        return jsonify({
            "status": "success",
            "theme": theme_mode
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()

@api_bp.route('/theme', methods=['POST'])
def set_theme():
    """Set the theme mode"""
    db = SessionLocal()
    try:
        data = request.json
        mode = data.get('mode')

        if not mode:
            return jsonify({
                "status": "error",
                "message": "Mode is required"
            }), 400

        if mode not in ['light', 'dark']:
            return jsonify({
                "status": "error",
                "message": "Mode must be 'light' or 'dark'"
            }), 400

        theme = Theme.set_theme_mode(db, mode)

        return jsonify({
            "status": "success",
            "theme": theme.mode
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()
