import logging
import prompts
from logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

CRISIS_MESSAGE = """
It sounds like you're going through a really difficult time. As an AI, I'm not equipped to provide 
crisis support, and I would highly recommend seeking out professional resources. If you need immediate help,
you can contact Crisis Text Line by texting HOME to 741741, call the Suicide & Crisis Lifeline at 988, or even
go to the emergency room you feel like you need. Please let me know if there's anything else I can do for you. You can get through this.
"""

MIN_CONVO_LEN = 10
SENT_CRISIS = False
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

def handle_crisis_message(client, messages):
    global SENT_CRISIS
    logger.info(f"SENT_CRISIS original status: {SENT_CRISIS}")
    if not SENT_CRISIS:
        SENT_CRISIS = True
        return CRISIS_MESSAGE
    return get_response(client, prompts.handle_crisis_prompt_v0(), messages)

def generate_response(client, messages):
    """
    Generate a response to a conversation using OpenAI's API.

    Args:
        client (OpenAI): The OpenAI client instance.
        messages (list): The conversation history.

    Returns:
        str: The generated response.
    """
    intent = get_response(client, prompts.classify_intent_prompt_v0() + str(messages[-CONTEXT_LEN:]), [])
    logger.info(f"Detected intent: {intent}")
    if "2" in intent:
        return handle_crisis_message(client, messages)
    elif "3" in intent:
        return get_response(client, prompts.systemprompt_v1_mini() + prompts.robust_v0(), messages)

    logger.info(f"Convo length: {len(messages)}")
    if len(messages) >= MIN_CONVO_LEN:
        should_end = get_response(client, prompts.idenfity_end_prompt_v0() + str(messages[-CONTEXT_LEN:]), [])
        logger.info(f"should_end: {should_end}")
        if "1" in should_end:
            return get_response(client, prompts.close_convo_prompt_v0(), messages)

    return get_response(client, prompts.systemprompt_v1(), messages)
