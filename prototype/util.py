import logging
import openai
from openai import OpenAI

import prompts

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CRISIS_MESSAGE = """
It sounds like you're going through a really difficult time. As an AI, I'm not equipped to provide 
crisis support, and I would highly recommend seeking out professional resources. If you need immediate help,
you can contact Crisis Text Line by texting HOME to 741741 or call the Suicide & Crisis Lifeline at 988.
Please let me know if there's anything else I can do for you. You're not alone.
"""

def get_response(client, sys_prompt, messages):
    """
    Send a message to the OpenAI API and return the response.

    Args:
        client (OpenAI): The OpenAI client instance.
        sys_prompt (str): The system prompt to send to the API.
        messages (list): The conversation history to send to the API.

    Returns:
        str: The response from the API.
    """
    conversation = [{"role": "system", "content": sys_prompt}]
    conversation.extend(messages)
    try:
        logger.debug("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation
        )
        response_content = response.choices[0].message.content
        logger.debug(f"Received API response: {response_content[:50]}...")
        return response_content
    except openai.error.OpenAIError as e:
        error_msg = f"An error occurred: {e}"
        logger.error(error_msg)
        return error_msg

def generate_response(client, messages):
    """
    Generate a response to a conversation using OpenAI's API.

    Args:
        client (OpenAI): The OpenAI client instance.
        messages (list): The conversation history.

    Returns:
        str: The generated response.
    """
    intent = get_response(client, prompts.classify_intent_prompt_v0(), messages[-1])
    logger.info(f"Detected intent: {intent}")
    
    if "2" in intent:
        return CRISIS_MESSAGE
    elif "3" in intent:
        return get_response(client, prompts.systemprompt_v1_mini() + prompts.robust_v0(), messages)
    return get_response(client, prompts.systemprompt_v1(), messages)
    