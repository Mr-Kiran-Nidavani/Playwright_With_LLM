from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Ensure .env is loaded
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
)