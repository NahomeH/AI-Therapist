from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sounddevice as sd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import texttospeech
from prompts import cbtprompt_v0, robust_v0

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()
chat_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
tts_client = texttospeech.TextToSpeechClient()
text2speech_audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=48000,
)
voice = texttospeech.VoiceSelectionParams(
                            language_code="en-US",
                            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                        )

# Store conversations in memory (for demo purposes)
conversations = {}

def get_ai_response(conversation):
    """
    Generate an AI response using OpenAI's chat completion API.
    
    Args:
        conversation (list): List of message dictionaries containing the conversation history
        
    Returns:
        str: The AI's response text, or error message if the API call fails
    """
    try:
        response = chat_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def generate_and_play_audio(text):
    """
    Generate speech from text using Google Cloud TTS and play it.
    
    Args:
        text (str): Text to convert to speech
    """
    try:
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
        
    Returns:
        JSON containing:
        - message (str): AI's response
        - sessionId (str): Session identifier
    """
    data = request.json
    session_id = data.get('sessionId', 'default')
    user_message = data.get('message')
    is_voice_mode = data.get('isVoiceMode', False)
    
    if session_id not in conversations:
        system_prompt = cbtprompt_v0() + robust_v0()
        conversations[session_id] = [{"role": "developer", "content": system_prompt}]
    
    conversations[session_id].append({"role": "user", "content": user_message})
    bot_reply = get_ai_response(conversations[session_id])
    conversations[session_id].append({"role": "assistant", "content": bot_reply})

    if is_voice_mode:
        error = generate_and_play_audio(bot_reply)
        if error:
            return jsonify({
                "message": bot_reply,
                "sessionId": session_id,
                "error": error
            })
    
    return jsonify({
        "message": bot_reply,
        "sessionId": session_id
    })

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """
    Reset a conversation session.
    
    Expects JSON payload with:
        - sessionId (str): Session to reset
        
    Returns:
        JSON with status: 'success' if session was reset
    """
    data = request.json
    session_id = data.get('sessionId', 'default')
    if session_id in conversations:
        del conversations[session_id]
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
