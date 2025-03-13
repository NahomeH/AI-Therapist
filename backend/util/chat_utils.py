import ast
import base64
from flask import jsonify, current_app
import logging
import backend.prompt_lib as pl
from .voice_utils import generate_audio
from .appt_utils import suggest_appointment

logger = logging.getLogger(__name__)

CRISIS_MESSAGE = "It sounds like you're going through a really difficult time. As an AI, I'm not equipped to provide crisis support, and I would highly recommend seeking out professional resources. If you need immediate help, you can contact Crisis Text Line by texting HOME to 741741, call the Suicide & Crisis Lifeline at 988, or even go to the emergency room you feel like you need. Please let me know if there's anything else I can do for you. You can get through this."
MIN_CONVO_LEN = 10
LONG_CONTEXT_LEN = 20
SHORT_CONTEXT_LEN = 3
ANALYSIS_CONTEXT_LEN = 5

def get_response(sys_prompt, messages):
    """
    Send a message to the OpenAI API and return the response.

    Args:
        sys_prompt (str): The system prompt to send to the API.
        messages (list): The conversation history to send to the API.

    Returns:
        str: The response from the API.
    """
    conversation = [{"role": "system", "content": sys_prompt}, *messages]
    logger.info(f"Sending request to OpenAI API with sys_prompt: {sys_prompt}")
    logger.info(f"Sending request to OpenAI API with messages: {messages}")
    response = current_app.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation
    )
    response_content = response.choices[0].message.content
    logger.info(f"Received API response: {response_content[:50]}...")
    return response_content


def get_first_message(user_name, sys_prompt, history, gender):
    therapist_name = "Jennifer"
    if gender == "MALE":
        therapist_name = "William"
    first_message = f"Hi {user_name}! I'm {therapist_name}, your AI therapist. What would you like to talk about?"
    if history:
        first_message = get_response(sys_prompt + pl.start_convo_prompt_v0(user_name, history), [])
    logger.info(f"First message: {first_message}")
    return first_message  


def handle_first_chat(data):
    session_id = data.get('sessionId')
    user_id = data.get('userId')
    preferred_name = data.get('userName')
    is_voice_mode = data.get('isVoiceMode', False)

    # Get user info from Supabase
    logger.info(f"Getting prefs for user_id: {user_id}")
    db_user_info = current_app.supabase_client.table('users').select('*').eq('user_id', user_id).execute()
    if not db_user_info:
        return jsonify({"success": False, "error": "User not found"})
    current_app.user_info = db_user_info.data[0]
    current_app.user_info['history_summary'] = ast.literal_eval(current_app.user_info['history_summary'])
    logger.info(f"User info: {current_app.user_info}")

    # Configure custom system prompt
    current_app.custom_sys_prompt = pl.systemprompt_v1()
    if current_app.user_info['history_summary']:
        current_app.custom_sys_prompt = current_app.custom_sys_prompt+ pl.inject_history(preferred_name, current_app.user_info['history_summary'])
    if current_app.user_info['custom_background']:
        current_app.custom_sys_prompt = current_app.custom_sys_prompt+ pl.inject_background(current_app.user_info['custom_background'])
    if current_app.user_info['custom_behavior']:
        current_app.custom_sys_prompt = current_app.custom_sys_prompt+ pl.inject_behavior(current_app.user_info['custom_behavior'])

    logger.info(f"Custom system prompt: {current_app.custom_sys_prompt}")

    response_data = {
        "success": True,
        "sessionId": session_id
    }

    # Retrieve first message and audio content, if applicable
    try:
        first_message = get_first_message(preferred_name, current_app.custom_sys_prompt, current_app.user_info['history_summary'], current_app.user_info['custom_gender'])
        response_data["message"] = first_message
        if is_voice_mode:
            audio_content = generate_audio(first_message)
            if audio_content:
                response_data["audioData"] = base64.b64encode(audio_content).decode("utf-8")
        init_convo = [{"role": "assistant", "content": first_message}]
        current_app.temp_db[session_id] = {"history": init_convo, "crisis_status": False}
        logger.info(f"Temp db: {current_app.temp_db}")
    except Exception as e:
        logger.error(f"Error retrieving first message: {e}")
        return jsonify({"success": False, "error": str(e)})
    
    return jsonify(response_data)


def handle_crisis_message(session_id, temp_db):
    logger.info(f"SENT_CRISIS original status: {temp_db[session_id]['crisis_status']}")
    if not temp_db[session_id]['crisis_status']:
        temp_db[session_id]['crisis_status'] = True
        return CRISIS_MESSAGE
    return get_response(current_app.custom_sys_prompt + pl.handle_crisis_prompt_v0(), temp_db[session_id]["history"][-LONG_CONTEXT_LEN:])


def convo_analysis(convo_str, user_info):
    return ""


def generate_response(session_id, temp_db, sys_prompt, user_info):
    """
    Generate a response to a conversation using OpenAI's API.

    Args:
        session_id (str): The ID of the conversation.
        temp_db (dict): The temporary database.
        sys_prompt (str): The system prompt for the response.

    Returns:
        str: The generated response.
        bool: True if the conversation should end, False otherwise.
    """
    session_history_str = str(temp_db[session_id]["history"][-SHORT_CONTEXT_LEN:])

    # Classify intent
    intent = get_response(pl.classify_intent_prompt_v1(), [{"role": "user", "content": session_history_str}])
    logger.info(f"Detected intent: {intent}")
    if "2" in intent: # Crisis response
        return handle_crisis_message(session_id, temp_db), False
    elif "3" in intent: # Robust response
        return get_response(sys_prompt + pl.robust_v0(), temp_db[session_id]["history"][-SHORT_CONTEXT_LEN:]), False

    # Generate typical response
    convo_len = len(temp_db[session_id]["history"])
    logger.info(f"Convo length: {convo_len}")
    if convo_len >= MIN_CONVO_LEN:
        # Determine if the conversation should end or not
        should_end = get_response(pl.idenfity_end_prompt_v0() + session_history_str, [])
        logger.info(f"should_end: {should_end}")
        if "1" in should_end:
            return get_response(pl.close_convo_prompt_v0() + pl.inject_behavior(current_app.user_info['custom_behavior']), temp_db[session_id]["history"][-LONG_CONTEXT_LEN:]), True

    return get_response(sys_prompt + convo_analysis(str(temp_db[session_id]["history"][-ANALYSIS_CONTEXT_LEN:]), user_info), temp_db[session_id]["history"][-LONG_CONTEXT_LEN:]), False


def handle_chat(data):
    session_id = data.get('sessionId', 'default')
    user_message = data.get('message')
    is_voice_mode = data.get('isVoiceMode', False)
    logger.info(f"Received message: {user_message}. Session ID: {session_id}")
    
    if session_id not in current_app.temp_db:
        return jsonify({"success": False, "error": "Session not found"})
    current_app.temp_db[session_id]["history"].append({"role": "user", "content": user_message})
    try:
        agent_response, end_flag = generate_response(session_id, current_app.temp_db, current_app.custom_sys_prompt, current_app.user_info)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({"success": False, "error": str(e)})
    logger.info(f"Response: {agent_response}")
    current_app.temp_db[session_id]["history"].append({"role": "assistant", "content": agent_response})

    response_data = {
        "success": True,
        "message": agent_response,
        "sessionId": session_id
    }

    if end_flag: 
        suggestedAppointment, suggestedTime = suggest_appointment(current_app.user_info['user_id'])
        if suggestedAppointment:
            response_data['suggestedAppointment'] = suggestedAppointment
            response_data['suggestedTime'] = suggestedTime
            logger.info(f"Scheduling appointment time: {response_data['suggestedTime']}")

    if is_voice_mode:
        audio_content = generate_audio(agent_response)
        if audio_content:
            response_data["audioData"] = base64.b64encode(audio_content).decode("utf-8")
    
    return jsonify(response_data)


def handle_add_punctuation(data):
    text = data.get('text')
    if not text:
        return jsonify({'success': False, 'error': 'No text provided'})
    
    try:   
        new_text = get_response(pl.punctualize_prompt(), [{"role": "user", "content": text}]).strip()
    except Exception as e:
        logger.error(f"Error adding punctuation: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to add punctuation'})
    
    return jsonify({'success': True, 'newText': new_text})
