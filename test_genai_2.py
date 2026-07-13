import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# upload file
print("Uploading file...")
with open("test.txt", "w") as f:
    f.write("This is a test file.")
    
gemini_file = client.files.upload(file="test.txt")
print("File uploaded:", gemini_file.name)

# Wait for process (mostly for pdf/video, but good measure)
while True:
    file_info = client.files.get(name=gemini_file.name)
    print("File state:", file_info.state)
    if file_info.state.name == "FAILED":
        raise ValueError("File processing failed")
    if file_info.state.name == "ACTIVE":
        break
    time.sleep(2)

print("Testing generate_content...")
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=[gemini_file, "Ne anladın?"],
    config=genai.types.GenerateContentConfig(
        system_instruction="Sen bir asistansın."
    )
)
print(response.text)
