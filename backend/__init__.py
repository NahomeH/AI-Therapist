import os
from flask import Flask
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import texttospeech
from supabase import create_client

from .logging_config import setup_logging
from .routes import api_blueprint

def create_app(test_config=None):
    setup_logging()
    load_dotenv()

    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    app.config.from_mapping(
        OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
        SUPABASE_URL=os.getenv('SUPABASE_URL'),
        SUPABASE_API_KEY=os.getenv('SUPABASE_API_KEY')
    )
    
    # Initialize clients
    app.openai_client = OpenAI(api_key=app.config['OPENAI_API_KEY'])
    app.tts_client = texttospeech.TextToSpeechClient()
    app.supabase_client = create_client(
        app.config['SUPABASE_URL'], 
        app.config['SUPABASE_API_KEY']
    )

    # Initialize state objects
    app.temp_db = {}
    app.user_info = {}
    app.custom_sys_prompt = None

    app.register_blueprint(api_blueprint)
    
    return app
