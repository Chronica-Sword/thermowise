import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

try:
    print("Testing generate_content with gemini-2.0-flash...")
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="Hello, how are you?"
    )
    print("Success!")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
