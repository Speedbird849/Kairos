# Makefile for FastAPI backend with Google Gemini + SerpAPI integration

# Variables
APP = main.py
PORT = 8000
HOST = 127.0.0.1

# Create virtual environment
venv:
	python -m venv venv
	@echo "✅ Virtual environment created."

# Install dependencies
install:
	pip install --upgrade pip
	pip install fastapi uvicorn python-multipart pillow requests pydantic google-generativeai python-dotenv

# Run the FastAPI app
run:
	uvicorn $(APP):app --reload --host $(HOST) --port $(PORT)

# Lint with flake8 (optional)
lint:
	flake8 $(APP) --max-line-length=100

# Clean temporary files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
	rm -rf tmp.*

# Set environment variable for SerpAPI key (temporary, dev only)
setenv:
	@echo "export SERPAPI_KEY=your_serpapi_key_here" >> .env

# Help
help:
	@echo "Usage:"
	@echo "  make venv       - Create a virtual environment"
	@echo "  make install    - Install Python dependencies"
	@echo "  make run        - Run FastAPI server at http://$(HOST):$(PORT)"
	@echo "  make lint       - Lint code with flake8 (optional)"
	@echo "  make clean      - Remove cache/temporary files"
	@echo "  make setenv     - Set SerpAPI environment key in .env (optional)"
