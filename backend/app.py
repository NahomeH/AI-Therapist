from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import texttospeech
import logging
from logging_config import setup_logging
from util import generate_response, tts_config, normalize_text

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()
chat_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
tts_client = texttospeech.TextToSpeechClient()

# Store state objects in memory
# TODO: replace with a database
temp_db = {}

def generate_audio(text):
    """
    Generate speech from text using Google Cloud TTS and returns it.
    
    Args:
        text (str): Text to convert to speech
    """
    try:
        text2speech_audio_config, voice = tts_config()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=text2speech_audio_config
        )
        return response.audio_content
    except Exception as e:
        print(f"Unexpected error in text-to-speech: {str(e)}")
        return None

@app.route('/api/normalize-text', methods=['POST'])
def add_punctuation_text():
    """
    Normalize text from speech-to-text by adding punctuation and proper formatting.
    
    Expects JSON payload with:
        - text (str): Text to normalize
        
    Returns:
        JSON containing:
        - normalizedText (str): Normalized text
    """
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        normalized = normalize_text(text, chat_client)
        return jsonify({'normalizedText': normalized})
    except Exception as e:
        logger.error(f"Error normalizing text: {str(e)}")
        return jsonify({'error': 'Failed to normalize text'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the client.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the chat session
        - message (str): User's message
        
    Returns:
        JSON containing:
        - message (str): AI's response
        - sessionId (str): Session identifier
    """
    data = request.json
    session_id = data.get('sessionId', 'default')
    user_message = data.get('message')
    is_voice_mode = data.get('isVoiceMode', False)
    logger.info(f"Received message: {user_message}. Session ID: {session_id}")

    normalized_message = None
    if is_voice_mode:
        normalized_message = normalize_text(user_message, chat_client)
        user_message = normalized_message
        logger.info(f"Normalized message: {user_message}. Session ID: {session_id}")
    
    if session_id not in temp_db:
        init_convo = [{"role": "assistant", "content": "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"}]
        temp_db[session_id] = {"history": init_convo, "crisis_status": False}
    
    temp_db[session_id]["history"].append({"role": "user", "content": user_message})
    agent_response = generate_response(session_id, chat_client, temp_db)
    temp_db[session_id]["history"].append({"role": "assistant", "content": agent_response})
    logger.info(f"Response: {agent_response}")

    response_data = {
        "message": agent_response,
        "sessionId": session_id
    }

    if is_voice_mode:
        response_data["normalizedMessage"] = normalized_message
        audio_content = generate_audio(agent_response)
        if audio_content:
            import base64
            response_data["audioData"] = base64.b64encode(audio_content).decode("utf-8")
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
