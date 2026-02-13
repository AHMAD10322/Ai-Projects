import asyncio
import speech_recognition as sr
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from openai.helpers import LocalAudioPlayer

load_dotenv()
client = OpenAI()
async_client = AsyncOpenAI()


async def tts_speak(text: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="speak in cheerful and happy tone",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


async def main():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 2

        while True:
            print("🎤 Speak something:")
            audio = recognizer.listen(source)
            try:
                query = recognizer.recognize_google(audio)
                print("📝 You said:", query)

                # Send query to OpenAI
                resp = client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "user", "content": query}]
                )

                reply = resp.choices[0].message.content
                print("🤖 Assistant:", reply)

                
                await tts_speak(reply)

            except sr.UnknownValueError:
                print("⚠️ Could not understand audio")
            except Exception as e:
                print("⚠️ Error:", e)



asyncio.run(main())
