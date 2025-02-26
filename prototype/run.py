import os
import signal
from pynput import keyboard

import sounddevice as sd
import numpy as np

import openai
from openai import OpenAI
from google.cloud import speech
from google.cloud.speech_v2.types import cloud_speech
from google.protobuf import duration_pb2
from google.cloud import texttospeech
from dotenv import load_dotenv

from prompts import systemprompt_v0, cbtprompt_v0, robust_v0
from speech2text import AUDIO_RATE, AUDIO_CHUNK, MicrophoneStream, get_final_transcription


load_dotenv()

class TherapyMode:
    """Constants for therapy interaction modes."""
    TEXT = "text"   # Text-based chat interaction
    VOICE = "voice" # Voice-based conversation

class TherapyStyle:
    """Constants for therapy styles."""
    GENERAL = "1"  # General counseling approach
    CBT = "2"      # Cognitive Behavioral Therapy approach

def setup_clients():
    """Initialize OpenAI and Google speech-to-text clients"""
    chat_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    # speech-to-text setup
    language_code = "en-US"
    speech2text_client = speech.SpeechClient()
    
    # # Sets the flag to enable voice activity events and timeout
    # speech_start_timeout = 30
    # speech_end_timeout = 30
    # speech_start_timeout = duration_pb2.Duration(seconds=speech_start_timeout)
    # speech_end_timeout = duration_pb2.Duration(seconds=speech_end_timeout)
    # voice_activity_timeout = (
    #     speech.StreamingRecognitionConfig.VoiceActivityTimeout(
    #         speech_start_timeout=speech_start_timeout,
    #         speech_end_timeout=speech_end_timeout,
    #     )
    # )

    speech2text_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=AUDIO_RATE,
        language_code=language_code,
        enable_automatic_punctuation=True
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech2text_config, 
        interim_results=False, 
        single_utterance=True,
        # enable_voice_activity_events=True,
        # voice_activity_timeout=voice_activity_timeout
    )

    # text-to-speech
    text2speech_client = texttospeech.TextToSpeechClient()

    text2speech_audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
    )
    voice = texttospeech.VoiceSelectionParams(
                                language_code="en-US",
                                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                            )
    return chat_client, speech2text_client, streaming_config, text2speech_client, text2speech_audio_config, voice

def get_therapy_config():
    """Get user's preferred therapy mode and style"""
    therapy_options = {
        TherapyStyle.GENERAL: systemprompt_v0,
        TherapyStyle.CBT: cbtprompt_v0
    }
    
    prompt = """Please select your therapy preferences:

Mode:
[T] Text-based therapy
[V] Voice-based therapy

Style:
[1] General Counseling
[2] Cognitive Behavioral Therapy (CBT)

Enter T1/T2 for text mode or V1/V2 for voice mode (or 'exit'): """

    while True:
        choice = input(prompt).lower()
        if choice == "exit":
            return None, None
            
        if choice.startswith('t'):
            style = choice[1:]
            if style in therapy_options:
                return TherapyMode.TEXT, therapy_options[style]()
                
        elif choice.startswith('v'):
            style = choice[1:]
            if style in therapy_options:
                return TherapyMode.VOICE, therapy_options[style]()
            
        print("Invalid choice. Please try again.")

def handle_voice_therapy(system_prompt, chat_client, speech2text_client, streaming_config, text2speech_client, audio_config, voice):
    """Handle voice-based therapy session using Google APIs.
    
    Sets up a voice conversation with real-time transcription and synthesis.
    The session continues until interrupted with Ctrl+C.
    
    Args:
        
    Returns:
        None
    """
    def on_press(key):
        if key == keyboard.Key.space:
            return False
    running = True
    def signal_handler(signum, frame):
        nonlocal running
        running = False
        raise KeyboardInterrupt

    # Signal handler for Ctrl+C
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    try:
        conversation = [{"role": "developer", "content": system_prompt + robust_v0()}]
        print("\nTalk2Me: What would you like to talk about?")
        print("(Press Ctrl+C to end the session)")
        while running:
            try:
                # Wait for spacebar press
                with keyboard.Listener(on_press=on_press) as listener:
                    print("Press SPACE to speak...")
                    listener.join()
                print("Recording... (Release SPACE to stop)")

                with MicrophoneStream(AUDIO_RATE, AUDIO_CHUNK) as stream:
                    audio_generator = stream.generator()
                    requests = (
                        speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator
                    )

                    responses = speech2text_client.streaming_recognize(streaming_config, requests)

                    # Get user input with automatic silence detection
                    user_input = get_final_transcription(responses)
                    if not user_input.strip():
                        continue
                        
                    print(f"You: {user_input}")
                    conversation.append({"role": "user", "content": user_input})

                    try:
                        response = chat_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=conversation,
                            timeout=30.0
                        )
                        bot_reply = response.choices[0].message.content
                        print(f"Talk2Me: {bot_reply}")
                        conversation.append({"role": "assistant", "content": bot_reply})
                        synthesis_input = texttospeech.SynthesisInput(text=bot_reply)
                        response = text2speech_client.synthesize_speech(
                            input=synthesis_input, voice=voice, audio_config=audio_config
                        )

                        audio = np.frombuffer(response.audio_content, dtype=np.int16)
                        sd.play(audio, 48000)
                        sd.wait()

                    except Exception as e:
                        print(f"Error: {e}")
                        print("Please try speaking again.")
                        continue
            except KeyboardInterrupt:
                break

            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Restarting audio stream...")
                continue

    finally:
        signal.signal(signal.SIGINT, original_handler)
        print("\nThank you for using Talk2Me. Take care!")

def handle_text_therapy(system_prompt, chat_client):
    """Handle text-based therapy session using OpenAI.
    
    Maintains a conversation with the user through text input/output.
    The session continues until the user types 'exit'.
    
    Args:
        system_prompt (str): Initial system prompt defining therapy style
        chat_client (OpenAI): Initialized OpenAI client
        
    Returns:
        None
    """
    conversation = [{"role": "developer", "content": system_prompt + robust_v0()}]
    print("\nTalk2Me: What would you like to talk about?")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
            
        conversation.append({"role": "user", "content": user_input})

        try:
            response = chat_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                timeout=30.0
            )
            bot_reply = response.choices[0].message.content
            print(f"Talk2Me: {bot_reply}")
            conversation.append({"role": "assistant", "content": bot_reply})

        except openai.error.OpenAIError as e:
            print(f"OPENAI API error: {e}")

def main():
    chat_client, speech2text_client, streaming_config, text2speech_client, audio_config, voice = setup_clients()

    print("Welcome to Talk2Me, your 24/7 AI therapist!")
    print("Please take a deep breath and ensure you're in a comfortable, private space.")
    
    mode, system_prompt = get_therapy_config()
    if not mode:
        print("Goodbye!")
        return
        
    if mode == TherapyMode.VOICE:
        handle_voice_therapy(system_prompt, chat_client, speech2text_client, streaming_config, text2speech_client, audio_config, voice)
    else:
        handle_text_therapy(system_prompt, chat_client)

if __name__ == "__main__":
    main()
    