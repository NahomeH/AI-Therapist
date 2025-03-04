from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sounddevice as sd
from supabase import create_client
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import texttospeech
import logging
from logging_config import setup_logging
from util import generate_response, tts_config

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()
chat_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
tts_client = texttospeech.TextToSpeechClient()
supabase_client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_API_KEY'))

# Store state objects in memory
# TODO: replace with a database
temp_db = {}

def generate_and_play_audio(text):
    """
    Generate speech from text using Google Cloud TTS and play it.
    
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
        
        audio_data = np.frombuffer(response.audio_content, dtype=np.int16)
        sd.play(audio_data, samplerate=48000)
        sd.wait()  # Wait until audio finishes playing
        return None
    except Exception as e:
        print(f"Unexpected error in text-to-speech: {str(e)}")
        return str(e)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the client.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the chat session
        - message (str): User's message
        - isVoiceMode (bool): True if the message is a voice input, False otherwise
        
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
    
    if session_id not in temp_db:
        init_convo = [{"role": "assistant", "content": "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"}]
        temp_db[session_id] = {"history": init_convo, "crisis_status": False}
    
    temp_db[session_id]["history"].append({"role": "user", "content": user_message})
    agent_response = generate_response(session_id, chat_client, temp_db)
    temp_db[session_id]["history"].append({"role": "assistant", "content": agent_response})
    logger.info(f"Response: {agent_response}")

    if is_voice_mode:
        error = generate_and_play_audio(agent_response)
        if error:
            return jsonify({
                "message": agent_response,
                "sessionId": session_id,
                "error": error
            })
    
    return jsonify({
        "message": agent_response,
        "sessionId": session_id
    })

@app.route('/api/newUser', methods=['POST'])
def newUser():
    """
    Add user info to the Supabase table
    
    Expects JSON payload with:
        - userID (str): Unique identifier for the user
        - email (str): User's email
        - fullName (str): User's full name
        - preferredName (str): User's preferred name
    """
    data = request.json
    user_id = data.get('userID')
    email = data.get('email')
    full_name = data.get('fullName')
    preferred_name = data.get('preferredName')
    logger.info(f"Adding user: {user_id}, {email}, {full_name}, {preferred_name}")
    try:
        supabase_client.table("users").insert({
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "preferred_name": preferred_name
        }).execute()
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({"success": False, "error": str(e)})

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
