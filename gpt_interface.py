from flask import json
from openai import OpenAI
import os
import dotenv
import uuid
import os
from summary import get_summary_by_title
import base64
import re

dotenv.load_dotenv()
oa_client = OpenAI(api_key=os.getenv("OPENAI_API"))

def extract_themes(query: str) -> str:
    system_prompt = (
        "You are an AI that extracts key literary themes or topics from a user question. "
        "Return only a comma-separated list of 2–3 keywords. Respond in English regardless of the input language."
    )
    completion = oa_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    return completion.choices[0].message.content.strip()


def generate_speech(text: str, model="tts-1", voice="nova") -> str:
    speech_response = oa_client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )

    filename = f"{uuid.uuid4().hex}.mp3"
    path = os.path.join("static", "audio", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(speech_response.content)

    return path
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Returns the full summary of a book based on its exact title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Exact title of the book (e.g., '1984')"
                    }
                },
                "required": ["title"]
            }
        }
    }
]


def recommend_and_call_tool(user_query: str, summaries: list[str], metadatas: list[dict]) -> str:
    system_prompt = (
        "You are a helpful assistant that recommends books based only on the provided summaries.\n"
        "Each summary includes the title of the book.\n\n"

        "📚 Recommendation Rules:\n"
        "- Only recommend books that appear in the provided summaries.\n"
        "- Do not invent or mention any book that is not included.\n"
        "- If no suitable match is found, respond politely that no recommendation can be made.\n"
        "- If multiple books match, list them all.\n"
        "- If multiple books match the user's interests, you must list all of them.\n"
        "- Format your response as a bullet list.\n"
        "- Each bullet must begin with the book title in **double asterisks**, followed by a short reason for the match.\n"
        "- Do not omit any relevant title from the summaries.\n\n"

        "🛠️ Tool Usage:\n"
        "- If the user requests to **summarize**, **describe**, or **explain** a specific book, call the `get_summary_by_title` tool.\n"
        "- This includes questions like:\n"
        "  • 'Can you describe The Hobbit?'\n"
        "  • 'What is 1984 about?'\n"
        "  • 'Tell me more about Brave New World'\n"
        "- You must wrap the book title in double asterisks in your response (e.g., **The Great Gatsby**).\n"
        "- Use the exact title provided in the summaries.\n"
        "- Only call the tool if **one specific book** is clearly mentioned.\n\n"

        "⚠️ Content Safety:\n"
        "- If the user message includes offensive or inappropriate language, do not generate a recommendation.\n"
        "- Politely respond with a warning and stop the conversation.\n"
)

    # Combine summaries with their corresponding titles
    summaries_text = "\n\n".join(
        [f"Title: {meta['title']}\nSummary: {summary}" for meta, summary in zip(metadatas, summaries)]
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": "Here are some book summaries:\n\n" + summaries_text}
    ]

    response = oa_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    # If GPT decides to call the tool
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "get_summary_by_title":
            summary = get_summary_by_title(args["title"])

            # Respond with full tool result
            followup = oa_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    *messages,
                    msg,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": summary
                    }
                ]
            )
            final_result = followup.choices[0].message.content
            titles = extract_titles_from_response(final_result)

            return {
                "result": final_result,
                "recommended_titles": titles
}

    # Fallback if no tool is called
    result_text = msg.content
    titles = extract_titles_from_response(result_text)

    return {
        "result": result_text,
        "recommended_titles": titles
}


def generate_image(prompt: str) -> str:
    image_response = oa_client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="low"  # sau "high" pentru calitate mai bună,
    )

    image_base64 = image_response.data[0].b64_json

    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join("static", "images", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return path

def speech_to_text(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        transcript=oa_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
    return transcript.text.strip()


def extract_titles_from_response(response: str) -> list[str]:
    return re.findall(r"\*\*(.*?)\*\*", response)