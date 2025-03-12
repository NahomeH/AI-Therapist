from flask import Blueprint, request
from .util.db_utils import handle_new_user, handle_save_session
from .util.chat_utils import handle_first_chat, handle_chat, handle_add_punctuation
import logging

api_blueprint = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_blueprint.route('/api/newUser', methods=['POST'])
def newUser():
    """
    Add user info to the Supabase table
    
    Expects JSON payload with:
        - userID (str): Unique identifier for the user
        - email (str): User's email
        - fullName (str): User's full name
        - preferredName (str): User's preferred name

    Returns:
        jsonify: JSON response with success status
    """
    data = request.json
    logger.info(f"Adding user: {data}")
    return handle_new_user(data)


@api_blueprint.route('/api/firstChat', methods=['POST'])
def firstChat():
    """
    Retrieves the first message for a new session.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the session (currently the same as userId)
        - userId (str): Unique identifier for the user
        - userName (str): User's preferred name
        - isVoiceMode (bool): True if voice mode, False otherwise
        
    Returns:
        JSON containing:
        - message (str): AI's response
        - audioData (str): Base64-encoded audio data for the response
    """
    data = request.json
    logger.info(f"Handling first chat. Data: {data}")
    return handle_first_chat(data)


@api_blueprint.route('/api/chat', methods=['POST'])
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
    logger.info(f"Handling chat. Data: {data}")
    return handle_chat(data)


@api_blueprint.route('/api/add-punct', methods=['POST'])
def add_punctuation_text():
    """
    Normalize text from speech-to-text by adding punctuation and proper formatting.
    
    Expects JSON payload with:
        - text (str): Text to normalize
        
    Returns:
        JSON containing:
        - success (bool): True if successful, False otherwise
        - newText (str): Normalized text
    """
    data = request.json
    return handle_add_punctuation(data)
    

@api_blueprint.route('/api/save', methods=['POST'])
def save():
    """
    Saves session to Supabase DB.
    
    Expects JSON payload with:
        - sessionId (str): Unique identifier for the session (currently the same as userId)
        
    Returns:
        JSON containing:
        - success (bool): True if the save was successful, False otherwise
        - error (str): Error message if the save failed, empty string otherwise
    """
    session_id = request.json.get('sessionId')
    logger.info(f"Saving session for session ID {session_id}")
    return handle_save_session(session_id)

