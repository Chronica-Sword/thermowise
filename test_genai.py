import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")
DOC_ID = os.getenv("GEMINI_DOCUMENT_ID")

client = genai.Client(api_key=API_KEY)

f = client.files.get(name=DOC_ID)

try:
    print("Testing generate_content with new SDK and file...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[f, "What is this file?"]
    )
    print(response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
