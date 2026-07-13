import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")
DOC_ID = os.getenv("GEMINI_DOCUMENT_ID")
genai.configure(api_key=API_KEY)

f = genai.get_file(DOC_ID)
print(f"File State: {f.state}")
print(f"File Name: {f.name}")
