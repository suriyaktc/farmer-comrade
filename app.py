from groq import Groq
import base64
from pathlib import Path
from gtts import gTTS
import os
import tempfile

import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("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"))

def speak(text: str, language: str):
    try:
        lang_code = {"english": "en", "tamil": "ta", "hindi": "hi"}.get(language, "en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name
        clean_text = text.replace("*", "").replace("#", "").replace("_", "")
        clean_text = text.replace("*", "").replace("#", "").replace("_", "")
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(temp_path)
        os.system(f"mpg123 -q {temp_path}")
        os.unlink(temp_path)
    except Exception as e:
        print(f"⚠️ Voice error: {e}")

def analyze_crop(image_path: str, language: str = "english"):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    ext = Path(image_path).suffix.lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    lang_instruction = {
        "english": "Respond in English",
        "tamil": "Respond in Tamil language (தமிழில் பதில் கூறுக)",
        "hindi": "Respond in Hindi language (हिंदी में जवाब दें)"
    }.get(language, "Respond in English")
    prompt = f"""You are Farmer Comrade, an expert agricultural AI assistant.
{lang_instruction}.
Analyze this crop image and provide:
1. CROP TYPE: What crop is this?
2. DISEASE/PROBLEM: What disease or issue do you see?
3. TREATMENT: Cheapest and easiest treatment?
4. WEATHER WARNING: What weather makes this worse?
5. SOIL TIP: One quick soil health tip
6. URGENCY: Low / Medium / High
Be simple and practical. Keep under 200 words."""
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

def main():
    print("=" * 50)
    print("🌱  FARMER COMRADE — AI Crop Doctor")
    print("    விவசாயி தோழன் | किसान साथी")
    print("=" * 50)
    image_path = input("\n📸 Drag your crop image here and press Enter: ").strip()
    image_path = image_path.replace("'", "").replace('"', "").replace("\\ ", " ").strip()
    if not Path(image_path).exists():
        print("❌ Image not found!")
        input("Press Enter to exit...")
        return
    print("\n🌍 Choose language:")
    print("   1. English")
    print("   2. Tamil (தமிழ்)")
    print("   3. Hindi (हिंदी)")
    choice = input("\nEnter 1, 2 or 3: ").strip()
    lang_map = {"1": "english", "2": "tamil", "3": "hindi"}
    language = lang_map.get(choice, "english")
    print("\n⏳ Analyzing your crop... please wait...\n")
    result = analyze_crop(image_path, language)
    print("=" * 50)
    print("📋  FARMER COMRADE REPORT")
    print("=" * 50)
    print(result)
    print("=" * 50)
    voice_choice = input("\n🔊 Hear this in voice? (yes/no): ").strip().lower()
    if voice_choice == "yes":
        print("\n🎙️ Speaking now...\n")
        speak(result, language)
        print("✅ Done!")
    print("\n💚 Thank you for using Farmer Comrade!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()