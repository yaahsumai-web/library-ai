import os
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

API_KEY = os.getenv('GEMINI_API_KEY')
MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite')

if not API_KEY:
    raise RuntimeError('GEMINI_API_KEY is not set. Add it to your .env file.')

client = genai.Client(api_key=API_KEY)

try:
    from chatbot_config import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = 'You are LibraryBot AI, a library and educational-book assistant.'


def make_contents(message, image_file):
    parts = [types.Part.from_text(text=SYSTEM_PROMPT + '\n\nUSER MESSAGE:\n' + message)]
    if image_file and image_file.filename:
        raw = image_file.read()
        if not raw:
            return parts
        mime = image_file.mimetype or 'image/jpeg'
        parts.append(types.Part.from_bytes(data=raw, mime_type=mime))
        parts.append(types.Part.from_text(text=(
            'The user uploaded an image. Analyze it only in the context of libraries, books, '
            'authors, reading, education, genres, or visible book-related text. Clearly separate '
            'what is visible from what you infer, and say when the image is unclear.'
        )))
    return parts


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/chat')
def chat():
    try:
        message = request.form.get('message', '').strip()
        image = request.files.get('image')
        if not message and not image:
            return jsonify({'error': 'Please enter a message or upload a library-related image.'}), 400

        contents = make_contents(message or 'Please analyze this uploaded image for library or book-related information.', image)
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=900,
            ),
        )
        text = (response.text or '').strip()
        if not text:
            text = 'I could not produce an answer from that input. Please try a clearer book or library question.'
        return jsonify({'response': text})
    except Exception as exc:
        app.logger.exception('Gemini request failed')
        return jsonify({'error': f'Unable to get a response right now: {exc}'}), 500


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'model': MODEL})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
