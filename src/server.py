from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from datetime import datetime
from typing import List, Dict
import time
import sys

# Setting the path to the static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(os.path.dirname(current_dir), 'static')

# Logger definition
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Creating an instance of the cache
from src.cache import ScanCache
cache = ScanCache()

@app.route('/')
def index():
    """home page"""
    try:
        logger.info("Serving index.html")
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        return f"Error: {str(e)}", 500

def get_file_info(file_path: str) -> Dict:
    """Gets a file path and returns the relevant information about it"""
    try:
        stats = os.stat(file_path)
        file_info = {
            "name": os.path.basename(file_path),
            "path": str(file_path),
            "size": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        }
        logger.debug(f"File info for {file_path}: {file_info}")
        return file_info
    except Exception as e:
        logger.error(f"Error getting info for file {file_path}: {str(e)}")
        return None

def scan_directory(base_path: str) -> List[Dict]:
    try:
        logger.info(f"Starting to scan directory: {base_path}")
        base_path = os.path.abspath(base_path)
        logger.info(f"Absolute path: {base_path}")
        
        files_info = []
        
        if not os.path.exists(base_path):
            logger.error(f"Path {base_path} does not exist!")
            return []
        
        try:
            dir_content = os.listdir(base_path)
            logger.info(f"Successfully read directory. Found {len(dir_content)} items")
        except Exception as e:
            logger.error(f"Cannot read directory: {str(e)}")
            return []
        
        model_extensions = {'.ckpt', '.safetensors', '.pt', '.bin', '.yaml', '.vae', '.sft', '.gguf'}
        
        for root, dirs, files in os.walk(base_path):
            logger.info(f"Scanning folder: {root}")
            logger.info(f"Found {len(files)} files")
            
            for filename in files:
                try:
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in model_extensions:
                        full_path = os.path.join(root, filename)
                        logger.info(f"Processing model file: {filename}")
                        
                        try:
                            stats = os.stat(full_path)
                            file_info = {
                                "name": filename,
                                "path": str(full_path),
                                "size": stats.st_size,
                                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
                            }
                            files_info.append(file_info)
                            logger.info(f"Successfully added file: {filename}")
                            logger.debug(f"File info: {file_info}")  # Log for testing
                        except Exception as file_e:
                            logger.error(f"Error getting file info for {filename}: {str(file_e)}")
                            continue
                        
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {str(e)}")
                    continue
        
        logger.info(f"Scan completed. Found {len(files_info)} files")
        logger.debug(f"All files info: {files_info}")  # Log for testing
        return files_info
        
    except Exception as e:
        logger.error(f"Error in scan_directory: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

@app.route('/scan', methods=['POST'])
def handle_scan():
    """The endpoint for scanning a folder"""
    try:
        data = request.get_json()
        logger.info(f"Received scan request with data: {data}")
        
        if not data or 'path' not in data:
            return jsonify({"error": "No path provided"}), 400

        path = data['path']
        logger.info(f"Processing scan request for: {path}")
        
        if not os.path.exists(path):
            error_msg = f"Path does not exist: {path}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 404
        
        files = scan_directory(path)
        
        response_data = {
            "files": files,
            "total": len(files)
        }
        
        logger.info(f"Sending response with {len(files)} files")
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error processing scan request: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """An endpoint for wiping the cache"""
    try:
        data = request.get_json()
        path = data.get('path')
        
        if path:
            logger.info(f"Clearing cache for path: {path}")
            cache.invalidate(path)
            message = f"Cleared cache for path: {path}"
        else:
            logger.info("Clearing entire cache")
            cache.clear()
            message = "Cleared entire cache"
            
        return jsonify({"message": message})

    except Exception as e:
        logger.error(f"Error in clear_cache endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """An endpoint for checking the health of the server"""
    stats = cache.get_stats()
    logger.info(f"Health check - Cache stats: {stats}")
    return jsonify({
        "status": "healthy",
        **stats
    })

if __name__ == '__main__':
    # Checking that the index.html file exists
    index_path = os.path.join(static_folder, 'index.html')
    if not os.path.exists(index_path):
        logger.error(f"index.html not found at {index_path}")
    else:
        logger.info(f"Found index.html at {index_path}")
    
    app.run(port=3000, debug=True)
