# Debugging the KVs Application

This document provides instructions for debugging the KVs application, particularly for viewing Flask and Python backend logs.

## Viewing Backend Logs

When developing the KVs application, you might need to see the Flask backend logs for debugging purposes. The standard `npm run tauri dev` command doesn't show these logs because it only starts the Tauri frontend.

### Solution: Using the dev-with-backend Script

We've added a special script that runs both the Flask backend and Tauri frontend simultaneously, showing logs from both processes in the same terminal window.

To use this script:

1. Make sure you have activated your Python virtual environment:
   ```
   .venv\Scripts\activate
   ```

2. Run the following command from the `frontend` directory:
   ```
   npm run dev-with-backend
   ```

This command will:
- Start the Flask backend with debug mode enabled
- Start the Tauri frontend in development mode
- Show logs from both processes in the terminal

### What You'll See

With this setup, you'll be able to see:
- Flask startup messages
- API request logs
- Python error messages and stack traces
- Any custom logging from your backend code

### Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed:
   ```
   npm install
   cd ..\backend
   pip install -r requirements.txt
   ```

2. Ensure the Python virtual environment is activated
3. Check that port 5000 is not already in use by another application