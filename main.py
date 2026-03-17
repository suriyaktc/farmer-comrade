from flask import Flask, request, jsonify, send_file
from groq import Groq
import base64
from pathlib import Path
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("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"))

LANGUAGES = {
    "english": {"code": "en", "name": "English", "instruction": "Respond in English"},
    "tamil": {"code": "ta", "name": "Tamil", "instruction": "Respond in Tamil language (தமிழில் பதில் கூறுக)"},
    "hindi": {"code": "hi", "name": "Hindi", "instruction": "Respond in Hindi language (हिंदी में जवाब दें)"},
    "telugu": {"code": "te", "name": "Telugu", "instruction": "Respond in Telugu language (తెలుగులో సమాధానం చెప్పండి)"},
    "kannada": {"code": "kn", "name": "Kannada", "instruction": "Respond in Kannada language (ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ)"},
    "malayalam": {"code": "ml", "name": "Malayalam", "instruction": "Respond in Malayalam language (മലയാളത്തിൽ മറുപടി പറയൂ)"},
    "marathi": {"code": "mr", "name": "Marathi", "instruction": "Respond in Marathi language (मराठीत उत्तर द्या)"},
    "bengali": {"code": "bn", "name": "Bengali", "instruction": "Respond in Bengali language (বাংলায় উত্তর দিন)"},
}

def analyze_crop(image_data: str, mime: str, language: str):
    lang = LANGUAGES.get(language, LANGUAGES["english"])
    prompt = f"""You are Farmer Comrade, an expert agricultural AI assistant.
{lang['instruction']}.
Analyze this crop image and provide a detailed report:
1. 🌱 CROP TYPE: What crop is this?
2. 🔍 DISEASE/PROBLEM: What disease or issue do you see? If healthy say so.
3. 💊 TREATMENT: Cheapest and easiest treatment available?
4. 🌦️ WEATHER WARNING: What weather conditions make this worse?
5. 🌾 SOIL TIP: One quick soil health tip for this crop
6. ⚡ URGENCY: Low / Medium / High
Be simple, clear and practical. Keep under 200 words."""
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}},
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files["image"]
        language = request.form.get("language", "english")
        ext = Path(file.filename).suffix.lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
        image_data = base64.b64encode(file.read()).decode("utf-8")
        result = analyze_crop(image_data, mime, language)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.json
        text = data.get("text", "")
        language = data.get("language", "english")
        lang_code = LANGUAGES.get(language, LANGUAGES["english"])["code"]
        clean_text = text.replace("*", "").replace("#", "").replace("_", "")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(temp_path)
        return send_file(temp_path, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)