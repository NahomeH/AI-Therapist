from datetime import datetime, timedelta
import logging
from logging_config import setup_logging
from google.cloud import texttospeech
import prompt_lib as pl

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

CRISIS_MESSAGE = "It sounds like you're going through a really difficult time. As an AI, I'm not equipped to provide crisis support, and I would highly recommend seeking out professional resources. If you need immediate help, you can contact Crisis Text Line by texting HOME to 741741, call the Suicide & Crisis Lifeline at 988, or even go to the emergency room you feel like you need. Please let me know if there's anything else I can do for you. You can get through this."
MIN_CONVO_LEN = 1
LONG_CONTEXT_LEN = 20
SHORT_CONTEXT_LEN = 3

def schedule_appointment(user_id, supabase_client):
    '''
    Schedule an appointment for a user if no future appointments exist.

    This function checks the Supabase database for any future appointments
    for the given user. If no future appointments are found, it schedules
    a new appointment exactly one week from the current date and time,
    adjusting the time to be between 6 AM and 11 PM. The new appointment
    is then inserted into the Supabase database.

    Args:
        user_id (str): The unique identifier for the user.
        supabase_client: The Supabase client instance used to interact with the database.

    Returns:
        tuple: A tuple containing:
            - suggestedAppointment (bool): True if a new appointment was scheduled, False otherwise.
            - suggestedTime (str): The ISO formatted string of the scheduled appointment time, or None if no appointment was scheduled.
    '''
    try:
        # future_appointments = supabase_client.table("appointments").select("*")\
        #         .eq("user_id", user_id)\
        #         .gte("appointment_time", datetime.now().isoformat())\
        #         .execute()
        future_appointments = None
        if not future_appointments or not future_appointments.data:
            next_appointment = datetime.now() + timedelta(days=7)
            next_appointment = next_appointment.replace(minute = 0, second=0, microsecond=0)
            
            # Adjust time to be between 6am and 11pm
            hour = next_appointment.hour
            if hour >= 23:
                next_appointment = next_appointment.replace(hour=23, minute=0)
            elif hour < 6:
                next_appointment = next_appointment.replace(hour=8, minute=0)
            
            # supabase_client.table("appointments").insert({
            #     "user_id": user_id,
            #     "appointment_time": next_appointment.isoformat(),
            #     "created_at_time": datetime.now().isoformat()
            # }).execute()

            return True, next_appointment.isoformat()
    except Exception as e:
        logger.error(f"Error querying supabase appointments table: {str(e)}")
        return False, None



def normalize_text(text, chat_client):
    """
    Use OpenAI to normalize and add proper punctuation to the text.
    """
    try:
        response = chat_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a text normalizer. Your task is to add proper punctuation, "
                              "fix capitalization, and correct common speech-to-text artifacts. "
                              "Maintain the exact meaning but make it read naturally. "
                              "Return ONLY the corrected text with no explanations."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.0  # Keep it consistent
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error normalizing text: {str(e)}")
        return text  # Return original text if normalization fails


def tts_config():
    text2speech_audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
    )
    voice = texttospeech.VoiceSelectionParams(
                            language_code="en-US",
                            name="Leda",
                            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                        )
    return text2speech_audio_config, voice

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
        logger.info(f"Sending request to OpenAI API with sys_prompt: {sys_prompt}")
        logger.info(f"Sending request to OpenAI API with messages: {messages}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation
        )
        response_content = response.choices[0].message.content
        logger.info(f"Received API response: {response_content[:50]}...")
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
    return get_response(client, pl.handle_crisis_prompt_v0(), temp_db[session_id]["history"][-LONG_CONTEXT_LEN:])

def generate_response(session_id, client, temp_db, sys_prompt):
    """
    Generate a response to a conversation using OpenAI's API.

    Args:
        client (OpenAI): The OpenAI client instance.
        session_id (str): The ID of the conversation.
        temp_db (dict): The temporary database.

    Returns:
        dict: "messages": the generated response string,
              "endingConvo": optional, boolean flag for ending conversation
    """
    intent = get_response(client, pl.classify_intent_prompt_v0() + str(temp_db[session_id]["history"][-SHORT_CONTEXT_LEN:]), [])
    logger.info(f"Detected intent: {intent}")
    if "2" in intent: # Crisis
        return {"messages": handle_crisis_message(session_id, client, temp_db)}
    elif "3" in intent: # Robust
        return {"messages": get_response(client, pl.systemprompt_v1_mini() + pl.robust_v0(), temp_db[session_id]["history"][-SHORT_CONTEXT_LEN:])}

    convo_len = len(temp_db[session_id]["history"])
    logger.info(f"Convo length: {convo_len}")
    if convo_len >= MIN_CONVO_LEN:
        should_end = get_response(client, pl.idenfity_end_prompt_v0() + str(temp_db[session_id]["history"][-SHORT_CONTEXT_LEN:]), [])
        logger.info(f"should_end: {should_end}")
        if "1" in should_end:
            return {
                "messages": get_response(client, pl.close_convo_prompt_v0(), temp_db[session_id]["history"][-LONG_CONTEXT_LEN:]),
                "endingConvo": True
            }

    return {"messages": get_response(client, sys_prompt, temp_db[session_id]["history"][-LONG_CONTEXT_LEN:])}

def get_history_summary(supabase_client, user_id):
    response = supabase_client.table('users').select('history_summary').eq('user_id', user_id).execute()
    logger.info(f"History summary: {response.data}")
    if not response.data:
        return None
    return response.data[0].get('history_summary')

def get_first_message(chat_client, user_name, sys_prompt, history):
    first_message = f"Hi {user_name}! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"
    if history:
        first_message = get_response(chat_client, sys_prompt + pl.start_convo_prompt_v0(user_name, history), [])
    logger.info(f"First message: {first_message}")
    return first_message  

def save_session(supabase_client, chat_client, user_id, past_history, chat_history):
    logger.info(f"Saving session for user_id: {user_id}, past_history: {past_history}, chat_history: {chat_history}")
    summary = get_response(chat_client, pl.summary_prompt_v0(chat_history), [])
    logger.info(f"Summary: {summary}")
    supabase_client.table("sessions").insert({
        "user_id": user_id,
        "full_conversation": chat_history,
        "summary": summary
    }).execute()
    supabase_client.table("users").update({
        "history_summary": str([*past_history, summary])
    }).eq("user_id", user_id).execute()
    return
