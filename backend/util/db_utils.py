from flask import jsonify, current_app
from .chat_utils import get_response
import backend.prompt_lib as pl
import logging

logger = logging.getLogger(__name__)

def handle_new_user(data):
    user_id = data.get('userID')
    email = data.get('email')
    full_name = data.get('fullName')
    preferred_name = data.get('preferredName')
    try:
        current_app.supabase_client.table("users").insert({
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


def save_session(user_id, past_history, chat_history):
    logger.info(f"Saving session for user_id: {user_id}, past_history: {past_history}, chat_history: {chat_history}")
    summary = get_response(pl.summary_prompt_v0(chat_history), [])
    logger.info(f"Summary: {summary}")
    current_app.supabase_client.table("sessions").insert({
        "user_id": user_id,
        "full_conversation": chat_history,
        "summary": summary
    }).execute()
    current_app.supabase_client.table("users").update({
        "history_summary": str([*past_history, summary])
    }).eq("user_id", user_id).execute()
    return


def handle_save_session(session_id):
    try:
        save_session(current_app.user_info['user_id'], current_app.user_info['history_summary'], current_app.temp_db[session_id]["history"])
    except Exception as e:
        logger.exception(f"Error saving session: {e}")
        return jsonify({"success": False, "error": str(e)})
    return jsonify({"success": True})
