from flask import jsonify, current_app
import logging

logger = logging.getLogger(__name__)

def handle_get_prefs(user_id): 
    logger.info(f"Getting prefs for user_id: {user_id}")
    try:
        db_user_info = current_app.supabase_client.table('users').select('*').eq('user_id', user_id).execute()
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    current_app.user_info = db_user_info.data[0]
    logger.info(f"Retrieved user info: {current_app.user_info}")
    return jsonify({'success': True, 'backgroundInfo': current_app.user_info['custom_background'], 'agentPreferences': current_app.user_info['custom_behavior'], 'gender': current_app.user_info['custom_gender']})


def handle_set_prefs(data):
    user_id = data.get('userId')
    background_info = data.get('backgroundInfo')
    agent_preferences = data.get('agentPreferences')
    gender = data.get('gender')
    logger.info(f"Saving prefs for user_id: {user_id}, background_info: {background_info}, agent_preferences: {agent_preferences}, gender: {gender}")
    try: 
        current_app.supabase_client.table("users").update({
            "custom_background": background_info,
            "custom_behavior": agent_preferences,
            "custom_gender": gender
        }).eq("user_id", user_id).execute()
    except Exception as e:
        logger.error(f"Error setting prefs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': True})
