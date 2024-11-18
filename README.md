# COMFYUI-MODELS-SERCH-IN-FOLDER
Search for files in the Comfyui models folder

# COMFYUI Model Scanner
A model scanner for COMFYUI Portable that enables easy searching and management of models across different folders.

*INSTALLATION*
1. Create a new virtual environment:

python -m venv comfyui_scanner_env

2. Activate the virtual environment:

**Windows:**
comfyui_scanner_env\Scripts\activate

**Linux/Mac:**
source comfyui_scanner_env/bin/activate

3. Install requirements:

pip install -r requirements.txt

4. The pip install -e . command installs a Python project in 'editable' mode, allowing immediate code changes to reflect without reinstallation.
   
pip install -e .

**USAGE**
1. Start the server:
2. 
python src/server.py

or

python -m src.server


4. Access in browser at:
   
http://localhost:3000


**FEATURES**
- Model folder scanning
- Model search
- Detailed model information
- Smart caching for improved performance  
- User-friendly interface

**PROJECT STRUCTURE**
- static/: HTML and UI files
- src/: Server source code
  - server.py: Main Flask server
  - cache.py: Caching system
  - directory_state.py: Directory change tracking

API

POST /scan
Scans directory for models.
{
  "path": "path/to/scan",
  "force_refresh": false
}

POST /cache/clear
Clears the cache.
{
  "path": "path/to/clear"  // Optional, clears specific directory only
}

GET /health
Checks server status.

![ex-1](https://raw.githubusercontent.com/lior007/COMFYUI-MODELS-SERCH-IN-FOLDER/main/ex-1.png)

![ex-2](https://raw.githubusercontent.com/lior007/COMFYUI-MODELS-SERCH-IN-FOLDER/main/ex-2.png)
