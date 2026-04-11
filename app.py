from groq import Groq
import base64
from pathlib import Path
from gtts import gTTS
import os
import tempfile
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Debug (remove later)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Check your .env file")

client = Groq(api_key=api_key)


def speak(text: str, language: str):
    try:
        lang_code = {
            "english": "en",
            "tamil": "ta",
            "hindi": "hi"
        }.get(language, "en")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name

        # ✅ Clean text properly
        clean_text = text.replace("*", "").replace("#", "").replace("_", "")

        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(temp_path)

        # Play audio (Mac/Linux)
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

    prompt = f"""
You are Farmer Comrade, an expert agricultural AI assistant.
{lang_instruction}.

Analyze this crop image and provide:
1. CROP TYPE
2. DISEASE/PROBLEM
3. TREATMENT (cheap and easy)
4. WEATHER WARNING
5. SOIL TIP
6. URGENCY (Low / Medium / High)

Keep it simple and under 200 words.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content


def main():
    print("=" * 50)
    print("🌱 FARMER COMRADE — AI Crop Doctor")
    print("விவசாயி தோழன் | किसान साथी")
    print("=" * 50)

    image_path = input("\n📸 Drag your crop image here and press Enter: ").strip()
    image_path = image_path.replace("'", "").replace('"', "").replace("\\ ", " ").strip()

    if not Path(image_path).exists():
        print("❌ Image not found!")
        return

    print("\n🌍 Choose language:")
    print("1. English")
    print("2. Tamil")
    print("3. Hindi")

    choice = input("\nEnter 1, 2 or 3: ").strip()
    language = {"1": "english", "2": "tamil", "3": "hindi"}.get(choice, "english")

    print("\n⏳ Analyzing your crop...\n")

    try:
        result = analyze_crop(image_path, language)
    except Exception as e:
        print(f"❌ API Error: {e}")
        return

    print("=" * 50)
    print("📋 FARMER COMRADE REPORT")
    print("=" * 50)
    print(result)
    print("=" * 50)

    voice_choice = input("\n🔊 Hear this in voice? (yes/no): ").strip().lower()

    if voice_choice == "yes":
        print("\n🎙️ Speaking...\n")
        speak(result, language)

    print("\n💚 Thank you for using Farmer Comrade!")


if __name__ == "__main__":
    main()
