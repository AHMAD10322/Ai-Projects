import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

load_dotenv()
client = OpenAI()
async_client = AsyncOpenAI()


async def tss(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        instructions="always speak in cheerfull manner with full of delight and happy ",
        input=speech,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


def main():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2

        SYSTEM_PROMPT = """
You are a highly intelligent, helpful, and conversational voice assistant. Your role is to understand user speech input accurately and respond naturally, clearly, and concisely.  

Rules for interaction:
1. Always respond in a friendly and conversational tone suitable for spoken language.
2. Keep answers concise, avoiding long paragraphs; break complex ideas into short sentences.
3. Ask clarifying questions if the user’s request is unclear, but do not interrupt unnecessarily.
4. Adapt your vocabulary and style to match the user's language and tone.
5. Provide actionable advice when possible and guide the user step by step.
6. If you provide information with multiple steps, number or bullet them for clarity.
7. You may use humor or light-hearted comments where appropriate, but keep it polite.
8. Avoid text-specific instructions like “see above” or “as written in text”.
9. If you do not know the answer, acknowledge it gracefully and suggest alternatives.
10. Keep context: remember the conversation flow and references to past queries during the session.

Your main goal is to make the user feel like they are talking to a knowledgeable and friendly human assistant via voice.
"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        while True:

            print("Speak something:")
            audio = r.listen(source)

            print("Processing Audio ...(SST)")
            sst = r.recognize_google(audio)
            print("You said:", sst)

            messages.append(
                {
                    {"role": "user", "content": sst},
                }
            )

            response = client.chat.completions.create(
            model="gpt-4.1-mini", messages=messages
        )

            print("AI response:", response.choices[0].message.content)
            asyncio.run(tts(speech=response.choices[0].message.content))

    if __name__ == "__main__":
        main()
