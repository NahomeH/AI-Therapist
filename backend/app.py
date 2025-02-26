from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
from logging_config import setup_logging
from util import generate_response

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Store state objects in memory
# TODO: replace with a database
temp_db = {}
conversations = {}
crisis_status = {}

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
    logger.info(f"Received message: {user_message}. Session ID: {session_id}")
    
    if session_id not in temp_db:
        init_convo = [{"role": "assistant", "content": "Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"}]
        temp_db[session_id] = {"history": init_convo, "crisis_status": False}
    
    temp_db[session_id]["history"].append({"role": "user", "content": user_message})
    agent_response = generate_response(session_id, client, temp_db)
    temp_db[session_id]["history"].append({"role": "assistant", "content": agent_response})
    logger.info(f"Response: {agent_response}")
    
    return jsonify({
        "message": agent_response,
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
    logger.info("Resetting conversation...")
    data = request.json
    session_id = data.get('sessionId', 'default')
    if session_id in temp_db:
        del temp_db[session_id]
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
