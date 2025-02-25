import os
import logging

import openai
from openai import OpenAI
from dotenv import load_dotenv

import prompts
import util
from logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    chat_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    init_message = "\nTalk2Me: Hi! I'm Jennifer, Talk2Me's 24/7 AI therapist. What would you like to talk about?"
    convo_history = [{"role": "assistant", "content": init_message}]
    print(init_message)
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
            
        convo_history.append({"role": "user", "content": user_input})
        bot_reply = util.generate_response(chat_client, convo_history)
        print(f"Talk2Me: {bot_reply}")
        convo_history.append({"role": "assistant", "content": bot_reply})

if __name__ == "__main__":
    main()
    