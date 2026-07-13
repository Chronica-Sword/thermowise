import os
import google.generativeai as genai
from dotenv import load_dotenv, set_key

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY == "Braya_kendi_anahtarini_yapisitir":
    print("API Key not found or invalid.")
    exit(1)

genai.configure(api_key=API_KEY)

pdf_path = r"d:\J.M. Smith, Hendrick Van Ness, Michael Abbott, Mark Swihart - Introduction to Chemical Engineering Thermodynamics-McGraw-Hill Education (2018).pdf"
display_name = "Smith_Van_Ness_Thermodynamics"

print(f"Uploading {pdf_path} to Gemini...")
try:
    # Check if we already uploaded it to save bandwidth
    existing_files = list(genai.list_files())
    uploaded_file = None
    for f in existing_files:
        if f.display_name == display_name:
            uploaded_file = f
            print(f"File already exists on Gemini servers: {f.name}")
            break
            
    if not uploaded_file:
        uploaded_file = genai.upload_file(pdf_path, display_name=display_name)
        print(f"Uploaded successfully. URI: {uploaded_file.uri}, Name: {uploaded_file.name}")
    
    # Save the file name to .env
    env_file = r"d:\thermowise\.env"
    set_key(env_file, "GEMINI_DOCUMENT_ID", uploaded_file.name)
    print("Updated .env with GEMINI_DOCUMENT_ID")
except Exception as e:
    print(f"Error uploading file: {e}")
