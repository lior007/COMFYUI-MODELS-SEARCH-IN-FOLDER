from setuptools import setup, find_packages

setup(
    name="comfyui_model_scanner",
    version="1.0.0",
    packages=find_packages(),  
    install_requires=[
        'Flask>=3.0.0',
        'Flask-CORS>=4.0.0',
        'python-dotenv>=1.0.0',
        'watchdog>=3.0.0'
    ],
    python_requires='>=3.8',
)