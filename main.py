from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google import genai
import os
import shutil
from dotenv import load_dotenv

# Load env variables
load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """Sen 'ThermoWise' adında uzman bir Kimya Mühendisliği Termodinamik profesörüsün.
Görevin, kullanıcının sorduğu soruları veya konseptleri ona adım adım, en anlaşılır ve mantıksal sırayla **kendi açıklayarak öğretmektir**.

Sıkı Kurallar:
1. Eğer sana bir bölüm slaytı (PDF vb.) gönderildiyse, SADECE o belgeyi referans alarak cevap ver!
2. Sanki "açık kaynak olan bir vize sınavına" girmiş gibi, hangi tablonun, hangi formülün sayfa kaçta (veya nerede) olduğunu özellikle belirterek adım adım anlat.
3. Dışarıdan veya internetten belirsiz veriler KULLANMA. 
4. Yanıtlarında formülleri ve matematiksel terimleri LaTeX formatında yaz. (Tek satır için $, blok için $$)
5. Mümkün olan yerlerde sistemi somutlaştırmak için Mermaid.js diyagramları kullan (```mermaid tagleri arasında).
   Mermaid Yazım Kuralları:
   - Düğüm (node) adlarında asla Türkçe karakter, boşluk veya özel karakter kullanma (Örn: `A1`, `B` veya `sistem_1` kullan).
   - Düğüm etiketlerinde (labels) parantez, Türkçe karakter, virgül veya özel simge varsa etiket metnini MUTLAKA çift tırnak içine al (Örn: `A["Sıcaklık (T)"]` veya `B["Giriş Akımı (P = 1 bar)"]`).
   - Düğüm adları ile etiketlerin arasında boşluk bırakma (Örn: `A["Etiket"]` doğru, `A ["Etiket"]` yanlış).
   - Mermaid kodu içinde asla tek veya çift tırnakları kapatmayı unutma.

Öğretici Çözüm Akışı (Mentorluk Modeli):
Problemi yanıtlarken öğrenciye soru sorup cevabını bekleme. Bunun yerine süreci kendin yönet ve mantığını açıklayarak çöz:
Adım 1: "Önce sistemi ve süreci tanımlayalım: (Açıklama...)"
Adım 2: "Yapmamız gereken varsayımlar şunlardır: (Neden bu varsayımları yaptığını açıkla)"
Adım 3: "Sisteme/Slayta göre kullanacağımız referans veya tablo: (Sayfa/Tablo belirterek değeri çek)"
Adım 4: "Enerji/Kütle dengesini kuralım: (Denklem...)"
Her adımı net bir şekilde yazarak öğrencinin zihninde konuyu tamamen somutlaştır. Asla öğrencinin cevap vermesini gerektirecek açık uçlu sorular sorma, soruları kendin sor ve kendin cevapla.
"""

client = None
if API_KEY and API_KEY != "Braya_kendi_anahtarini_yapisitir":
    client = genai.Client(api_key=API_KEY)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

chat_history = []
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat(message: str = Form(...), file: UploadFile = File(None)):
    if not client:
        return {"reply": "⚠️ **Sistem Uyarısı:** Gemini Modeli başlatılamadı."}
    
    # 1. Store the uploaded file locally if exists
    gemini_file = None
    if file and file.filename:
        import uuid
        import re
        # Get extension and sanitize it to ASCII
        _, ext = os.path.splitext(file.filename)
        ext = re.sub(r'[^a-zA-Z0-9.]', '', ext)
        # Create a secure random name
        secure_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(TEMP_DIR, secure_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Upload to Gemini
        try:
            gemini_file = client.files.upload(file=file_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"reply": f"⚠️ Dosya yüklenirken hata oluştu: {str(e)}"}
            
    try:
        # Build prompt natively
        prompt_parts = []
        if gemini_file:
             prompt_parts.append(gemini_file)
        
        if chat_history:
            history_text = "Önceki konuşmalar:\n" + "\n".join(chat_history) + "\n\nŞu anki soru: " + message
            prompt_parts.append(history_text)
        else:
            prompt_parts.append(message)

        import time
        models_to_try = [
            'gemini-3.5-flash',
            'gemini-2.5-flash',
            'gemini-flash-latest',
            'gemini-2.0-flash',
            'gemini-2.5-pro',
            'gemini-2.0-flash-lite'
        ]
        reply_text = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"Deneme yapılıyor: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_parts,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                reply_text = response.text
                break
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "429" in err_str:
                    print(f"API meşgul ({model_name}), başka modele geçiliyor...")
                    time.sleep(1)
                else:
                    print(f"Beklenmeyen hata ({model_name}): {err_str}, başka modele geçiliyor...")
                    time.sleep(1)
                    
        if not reply_text and last_error:
            raise last_error
        
        chat_history.append(f"Kullanıcı: {message} {'(Belge Eklendi)' if gemini_file else ''}")
        chat_history.append(f"Sistem: {reply_text}")
        
        return {"reply": reply_text}
        
    except Exception as api_err:
        import traceback
        traceback.print_exc()
        return {"reply": f"Hata: API isteği başarısız oldu. {str(api_err)}"}
