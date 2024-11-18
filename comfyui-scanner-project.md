COMFYUI Model Scanner - Project Structure

📁 comfyui_model_scanner/
├── 📁 src/
│   ├── 📄 __init__.py     # Module initialization file
│   ├── 📄 server.py       # Main Flask server
│   ├── 📄 cache.py        # Cache management
│   └── 📄 directory_state.py  # Directory change tracking
│
├── 📁 static/
│   ├── 📄 index.html      # Interface page
│   ├── 📄 styles.css      # Styling
│   └── 📄 scripts.js      # Client-side logic
│
├── 📄 setup.py            # Installation settings
├── 📄 requirements.txt    # Project dependencies
├── 📄 README.txt          # Documentation
└── 📄 .gitignore         # Files to ignore in git

Main Dependencies:
- Flask: Web server
- Flask-CORS: Browser request support
- python-dotenv: Environment variable management
- watchdog: File change monitoring
