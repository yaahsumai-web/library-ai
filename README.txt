LibraryBot AI — Smart Library Assistant

Files included:
- app.py: Flask server and Gemini API integration
- chatbot_config.py: domain system prompt
- requirements.txt: Python dependencies including Gunicorn
- .env: API/model configuration template (replace the placeholder key)
- .gitignore: protects .env and local Python files
- templates/index.html: complete responsive UI with CSS and JavaScript

The app accepts text and an optional image in /api/chat. Images are sent to Gemini for multimodal analysis.
