from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("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"))


response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello to Farmer Comrade project!"}]
)

print(response.choices[0].message.content)
input("Press Enter to exit...")