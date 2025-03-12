from flask import jsonify, current_app, make_response
import logging
import pytz
from datetime import datetime, timedelta
from ics import Calendar, Event

logger = logging.getLogger(__name__)
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')

def suggest_appointment(user_id):
    '''
    Suggest an appointment for a user if no future appointments exist.

    This function checks the Supabase database for any future appointments
    for the given user. If no future appointments are found, it schedules
    a new appointment exactly one week from the current date and time (the same hour).
    If the current time is between 6 AM and 11 PM, it would suggest a time at 8 PM.

    Args:
        user_id (str): The unique identifier for the user.
        supabase_client: The Supabase client instance used to interact with the database.

    Returns:
        tuple: A tuple containing:
            - suggestedAppointment (bool): True if a new appointment was suggested, False otherwise.
            - suggestedTime (str): The ISO formatted string of the suggested appointment time, or None if no appointment was suggested.
    '''
    try:
        future_appointments = current_app.supabase_client.table("appointments").select("*")\
                .eq("user_id", user_id)\
                .gte("appointment_time", datetime.now().isoformat())\
                .execute()
    except Exception as e:
        logger.error(f"Error querying/inserting into Supabase appointments table: {str(e)}")
        return False, None
    if future_appointments and future_appointments.data:
        logger.info(f"User {user_id} already has an appointment time.")
        return False, None
    current_time = datetime.now(pytz.UTC)
    local_time = current_time.astimezone(PACIFIC_TZ)
    next_appointment = (local_time + timedelta(days=7)).replace(minute = 0, second=0, microsecond=0)
    
    # Adjust time to be between 6am and 11pm
    hour = next_appointment.hour
    if hour >= 23 or hour < 6:
        # Late night users (11 PM - 6 AM) likely prefer evening appointments
        next_appointment = next_appointment.replace(hour=20)  # 8 PM
    
    utc_appointment = next_appointment.astimezone(pytz.UTC)
    logger.info(f"Suggesting to user_id: {user_id} for local_appointment_time: {next_appointment.isoformat()}, utc_appointment_time: {utc_appointment.isoformat()}")

    return True, next_appointment.isoformat()


def handle_generate_calendar(data):
    appointment_time = data.get('appointmentTime')
    start_time = datetime.fromisoformat(appointment_time)
    if start_time.tzinfo is None:
        start_time = PACIFIC_TZ.localize(start_time)

    c = Calendar()
    e = Event()
    e.name = "Therapy Session with Talk2Me"
    e.begin = start_time
    e.end = start_time + timedelta(minutes=30)
    e.description = f"Virtual therapy session with Talk2Me AI therapist"
    e.created = datetime.now(pytz.UTC)
    
    c.events.add(e)
    calendar_content = str(c)
    
    response = make_response(calendar_content)
    response.headers["Content-Disposition"] = "attachment; filename=therapy_session.ics"
    response.headers["Content-Type"] = "text/calendar"
    return response


def handle_save_appointment(data):
    user_id = data.get('userId')
    appointment_time = data.get('appointmentTime')
    if not user_id or not appointment_time:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Convert to UTC for storage
    local_time = datetime.fromisoformat(appointment_time)
    utc_time = local_time.astimezone(pytz.UTC)

    try:
        current_app.supabase_client.table("appointments").insert({
            "user_id": user_id,
            "appointment_time": utc_time.isoformat(),
            "created_at_time": datetime.now(pytz.UTC).isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Error saving appointment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': True})


def handle_get_appointments(user_id):
    try:
        response = current_app.supabase_client.table("appointments").select("*")\
            .eq("user_id", user_id)\
            .gte("appointment_time", datetime.now(pytz.UTC).isoformat())\
            .order("appointment_time", desc=False)\
            .execute()
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    appointments = response.data if response else []    
    return jsonify({'success': True, 'appointments': appointments})
