# ThermoWise - Kimya Mühendisliği Termodinamik Eğitmeni

ThermoWise, Smith & Van Ness'in (2018) *Introduction to Chemical Engineering Thermodynamics* kitabını referans alarak kimya mühendisliği termodinamiği sorularını ve konseptlerini adım adım anlatan etkileşimli bir web uygulamasıdır.

## 🚀 Özellikler
- **FastAPI Altyapısı**: Hızlı, modern ve asenkron web API katmanı.
- **Multimodal Gemini Entegrasyonu**: Görsel (PNG, JPEG) ve PDF yükleme desteği ile formül ve soruları doğrudan analiz edebilme yeteneği.
- **Dinamik Matematiksel Formüller**: KaTeX entegrasyonu ile LaTeX formatındaki formülleri tarayıcıda pürüzsüz görüntüleme.
- **Mermaid.js Şemaları**: Sistemlerin ve süreçlerin görsel şemalarını otomatik çizme.
- **Çift Katmanlı Mermaid Hata Yönetimi**: Hatalı çizimlerde ham veriyi gösteren robust tasarım.

## 🛠️ Kurulum ve Çalıştırma

1. Projeyi bilgisayarınıza klonlayın veya indirin.
2. Bir sanal ortam (venv) oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   # Windows için:
   .\venv\Scripts\activate
   # Linux/macOS için:
   source venv/bin/activate
   ```
3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install fastapi uvicorn google-genai python-multipart python-dotenv
   ```
4. Proje kök dizininde bir `.env` dosyası oluşturun ve Gemini API anahtarınızı ekleyin:
   ```env
   GEMINI_API_KEY=kendi_api_anahtariniz
   ```
5. Uygulamayı başlatın:
   ```bash
   uvicorn main:app --reload
   ```
6. Tarayıcınızdan `http://127.0.0.1:8000` adresine gidin.

## 📂 Dosya Yapısı
- `main.py`: FastAPI backend ve Gemini entegrasyonu.
- `static/`: HTML, CSS (Tailwind) ve istemci tarafı JavaScript (`script.js`) kodları.
- `.gitignore`: venv, .env ve geçici dosyaların GitHub'a gitmesini önleyen yapılandırma.
