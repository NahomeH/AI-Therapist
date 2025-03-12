from flask import Blueprint, request
from .util.db_utils import handle_new_user, handle_save_session
from .util.chat_utils import handle_first_chat, handle_chat, handle_add_punctuation
from .util.appt_utils import handle_get_appointments, handle_generate_calendar, handle_save_appointment
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


@api_blueprint.route('/api/generate-calendar', methods=['POST'])
def generate_calendar():
    """
    Generate an ICS file for a therapy appointment
    
    Expects JSON payload with:
        - appointmentTime (str): ISO 8601 formatted appointment time
        - userName (str): User's name for the event
    
    Returns:
        ICS file for download
    """
    data = request.json
    return handle_generate_calendar(data)
    

@api_blueprint.route('/api/save-appointment', methods=['POST'])
def save_appointment():
    """
    Save an accepted appointment to the database.
    
    Expects JSON payload with:
        - userId (str): User ID
        - appointmentTime (str): ISO formatted appointment time
    """
    data = request.json
    return handle_save_appointment(data)


@api_blueprint.route('/api/get-appointments', methods=['POST'])
def get_appointments():
    """
    Retrieve upcoming appointments for a user.
    
    Expects JSON payload with:
        - userId (str): Unique identifier for the user
        
    Returns:
        JSON containing:
        - success (bool): True if successful
        - appointments (list): List of appointment objects
        - error (str): Error message if any
    """
    user_id = request.json.get('userId')
    return handle_get_appointments(user_id)
    