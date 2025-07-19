import sys
from pathlib import Path

# Add the current directory to the Python path if it's not already there
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Try to import the modules that were causing issues
try:
    from routes.api import api_bp
    print("Successfully imported api_bp from routes.api")
except ImportError as e:
    print(f"Error importing api_bp from routes.api: {e}")

try:
    from routes.kv import kv_bp
    print("Successfully imported kv_bp from routes.kv")
except ImportError as e:
    print(f"Error importing kv_bp from routes.kv: {e}")

try:
    from models import SessionLocal
    print("Successfully imported SessionLocal from models")
except ImportError as e:
    print(f"Error importing SessionLocal from models: {e}")