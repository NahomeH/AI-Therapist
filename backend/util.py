import logging
from logging_config import setup_logging
import prompt_lib as pl

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

CRISIS_MESSAGE = "It sounds like you're going through a really difficult time. As an AI, I'm not equipped to provide crisis support, and I would highly recommend seeking out professional resources. If you need immediate help, you can contact Crisis Text Line by texting HOME to 741741, call the Suicide & Crisis Lifeline at 988, or even go to the emergency room you feel like you need. Please let me know if there's anything else I can do for you. You can get through this."
MIN_CONVO_LEN = 10
CONTEXT_LEN = 3

def get_response(client, sys_prompt, messages):
    """
    Send a message to the OpenAI API and return the response.

    Args:
        client (OpenAI): The OpenAI client instance.
        messages (list): The conversation history to send to the API.

    Returns:
        str: The response from the API.
    """
    conversation = [{"role": "system", "content": sys_prompt}, *messages]
    try:
        logger.debug("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation
        )
        response_content = response.choices[0].message.content
        logger.debug(f"Received API response: {response_content[:50]}...")
        return response_content
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        logger.error(error_msg)
        return error_msg

def handle_crisis_message(session_id, client, temp_db):
    logger.info(f"SENT_CRISIS original status: {temp_db[session_id]['crisis_status']}")
    if not temp_db[session_id]['crisis_status']:
        temp_db[session_id]['crisis_status'] = True
        return CRISIS_MESSAGE
    return get_response(client, pl.handle_crisis_prompt_v0(), temp_db[session_id]["history"])

def generate_response(session_id, client, temp_db):
    """
    Generate a response to a conversation using OpenAI's API.

    Args:
        client (OpenAI): The OpenAI client instance.
        session_id (str): The ID of the conversation.
        temp_db (dict): The temporary database.

    Returns:
        str: The generated response.
    """
    intent = get_response(client, pl.classify_intent_prompt_v0() + str(temp_db[session_id]["history"][-CONTEXT_LEN:]), [])
    logger.info(f"Detected intent: {intent}")
    if "2" in intent:
        return handle_crisis_message(session_id, client, temp_db)
    elif "3" in intent:
        return get_response(client, pl.systemprompt_v1_mini() + pl.robust_v0(), temp_db[session_id]["history"])

    convo_len = len(temp_db[session_id]["history"])
    logger.info(f"Convo length: {convo_len}")
    if convo_len >= MIN_CONVO_LEN:
        should_end = get_response(client, pl.idenfity_end_prompt_v0() + str(temp_db[session_id]["history"][-CONTEXT_LEN:]), [])
        logger.info(f"should_end: {should_end}")
        if "1" in should_end:
            return get_response(client, pl.close_convo_prompt_v0(), temp_db[session_id]["history"])

    return get_response(client, pl.systemprompt_v1(), temp_db[session_id]["history"])
