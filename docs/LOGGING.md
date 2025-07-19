# Flask API Logging Documentation

This document explains the logging implementation for the KVs Flask backend.

## Overview

The logging system captures detailed information about:
- All API requests (input)
- All API responses (output)
- All exceptions and errors

Logs are stored in the `logs` directory with separate files for API logs and error logs.

## Log Files

- **API Log File**: `logs/api.log`
  - Contains information about all API requests and responses
  - Includes request details (method, URL, headers, arguments, JSON body)
  - Includes response details (status code, response time, response body)

- **Error Log File**: `logs/error.log`
  - Contains detailed information about exceptions and errors
  - Includes stack traces for debugging
  - Includes request context for error analysis

## Log Format

Logs are formatted as follows:
```
[timestamp] - [logger_name] - [log_level] - [message]
```

Example:
```
2023-07-13 08:30:45,123 - api - INFO - API Request: {"request_id": "1689231045.123", "method": "GET", "url": "http://localhost:5000/api/v1/kv", "path": "/api/v1/kv", "args": {}}
```

## Implementation Details

### Middleware Approach

The logging system uses Flask middleware to automatically log all API requests and responses:

1. **Before Request**: Captures and logs request details
   - Generates a unique request ID
   - Logs request method, URL, headers, arguments, and JSON body

2. **After Request**: Captures and logs response details
   - Logs response status code, response time, and response body
   - Links response to request using the request ID

3. **Error Handler**: Captures and logs exceptions
   - Logs exception details with stack trace
   - Links exception to request using the request ID

### Utility Functions

The `utils/logger.py` module provides utility functions for logging:

- `log_api_call`: Decorator for logging API calls (alternative to middleware)
- `log_exception`: Function for logging exceptions with context

## How to Use

### Automatic Logging

All API requests and responses are automatically logged by the middleware. No additional code is required.

### Manual Logging

For additional logging in your code:

```python
from utils.logger import api_logger, error_logger

# Log info message
api_logger.info("Custom info message")

# Log error message
error_logger.error("Custom error message")

# Log exception with context
try:
    # Some code that might raise an exception
    result = some_function()
except Exception as e:
    from utils.logger import log_exception
    log_exception(e, context={"function": "some_function", "params": {...}})
    raise
```

## Testing the Logging System

A test script is provided to verify the logging implementation:

```bash
python test_logging.py
```

This script:
1. Makes requests to different API endpoints
2. Checks if log files are created
3. Displays the last few lines of each log file

## Configuration

Logging configuration is defined in `config.py`:

- `LOG_DIR`: Directory for log files
- `API_LOG_FILE`: Path to API log file
- `ERROR_LOG_FILE`: Path to error log file
- `LOG_FORMAT`: Format for log messages
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)