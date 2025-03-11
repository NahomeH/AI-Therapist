import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import texttospeech
import logging
from logging_config import setup_logging
from supabase import create_client
from util import generate_response, tts_config, get_first_message, save_session, normalize_text
import ast
import prompt_lib as pl

app = Flask(__name__)
CORS(app, supports_credentials=True)

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
user_info = {}
custom_sys_prompt = None

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
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
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
    global custom_sys_prompt
    global temp_db
    global user_info

    data = request.json
    session_id = data.get('sessionId', 'default')
    user_message = data.get('message')
    is_voice_mode = data.get('isVoiceMode', False)
    logger.info(f"Received message: {user_message}. Session ID: {session_id}")
    
    if session_id not in temp_db:
        init_convo = [{"role": "assistant", "content": "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"}]
        temp_db[session_id] = {"history": init_convo, "crisis_status": False}
    
    temp_db[session_id]["history"].append({"role": "user", "content": user_message})
    agent_response = generate_response(session_id, chat_client, temp_db, custom_sys_prompt)
    temp_db[session_id]["history"].append({"role": "assistant", "content": agent_response})
    logger.info(f"Response: {agent_response}")

    response_data = {
        "message": agent_response,
        "sessionId": session_id
    }

    if is_voice_mode:
        audio_content = generate_audio(agent_response)
        if audio_content:
            response_data["audioData"] = base64.b64encode(audio_content).decode("utf-8")
    
    return jsonify(response_data)

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
            "preferred_name": preferred_name,
            "history_summary": "[]"
        }).execute()
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({"success": False, "error": str(e)})

    return jsonify({"success": True})


@app.route('/api/firstChat', methods=['POST', 'OPTIONS'])
def firstChat():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    Retrieves the first message for a new session.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the session (currently the same as userId)
        - userId (str): Unique identifier for the user
        - userName (str): User's preferred name
        
    Returns:
        JSON containing:
        - message (str): AI's response
        - audioData (str): Base64-encoded audio data for the response
    """
    global custom_sys_prompt
    global temp_db
    global user_info

    session_id = request.json.get('sessionId')
    user_id = request.json.get('userId')
    preferred_name = request.json.get('userName')
    is_voice_mode = request.json.get('isVoiceMode', False)
    logger.info(f"Session ID: {session_id}, User ID: {user_id}, Preferred name: {preferred_name}, Is voice mode: {is_voice_mode}")
    
    db_user_info = supabase_client.table('users').select('*').eq('user_id', user_id).execute()
    if not db_user_info:
        return jsonify({"success": False, "error": "User not found"})
    user_info = db_user_info.data[0]
    user_info['history_summary'] = ast.literal_eval(user_info['history_summary'])
    logger.info(f"User info: {user_info}")
    if user_info['history_summary']:
        custom_sys_prompt = pl.systemprompt_v1() + pl.inject_history(preferred_name, user_info['history_summary'])
    else:
        custom_sys_prompt = pl.systemprompt_v1()

    response_data = {
        "success": True,
        "sessionId": session_id
    }
    
    try:
        first_message = get_first_message(chat_client, preferred_name, custom_sys_prompt, user_info['history_summary'])
        if is_voice_mode:
            first_message = first_message + ' You can press space to start or stop speaking.'
            audio_content = generate_audio(first_message)
            if audio_content:
                response_data["audioData"] = base64.b64encode(audio_content).decode("utf-8")
        response_data["message"] = first_message
        init_convo = [{"role": "assistant", "content": first_message}]
        temp_db[session_id] = {"history": init_convo, "crisis_status": False}
    except Exception as e:
        logger.error(f"Error retrieving first message: {e}")
        return jsonify({"success": False, "error": str(e)})
    
    return jsonify(response_data)

@app.route('/api/save', methods=['POST', 'OPTIONS'])
def save():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    Saves session to Supabase DB.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the session (currently the same as userId)
        
    Returns:
        JSON containing:
        - success (bool): True if the save was successful, False otherwise
        - error (str): Error message if the save failed, empty string otherwise
    """
    global temp_db
    global user_info

    session_id = request.json.get('sessionId')
    try:
        save_session(supabase_client, chat_client, user_info['user_id'], user_info['history_summary'], temp_db[session_id]["history"])
    except Exception as e:
        logger.exception(f"Error saving session: {e}")
        return jsonify({"success": False, "error": str(e)})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
