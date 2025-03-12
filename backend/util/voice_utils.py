from flask import current_app
from google.cloud import texttospeech
import logging

logger = logging.getLogger(__name__)

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


def generate_audio(text):
    """
    Generate speech from text using Google Cloud TTS and returns it.
    
    Args:
        text (str): Text to convert to speech
    """
    try:
        text2speech_audio_config, voice = tts_config()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        response = current_app.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=text2speech_audio_config
        )
        return response.audio_content
    except Exception as e:
        print(f"Unexpected error in text-to-speech: {str(e)}")
        return None

