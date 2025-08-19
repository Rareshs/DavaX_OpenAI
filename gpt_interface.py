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

def format_recommendations(titles: list[str]) -> str:
    """Return a clean, well-structured Markdown response with clear separation."""
    if not titles:
        return "No book recommendations could be generated."

    blocks = []
    for idx, title in enumerate(titles, start=1):
        summary = get_summary_by_title(title)
        blocks.append(
            f"### {idx}. **{title}**\n"
            f"{summary.strip()}\n"
        )
    return "## 📚 Recommended Books\n\n" + "\n".join(blocks)

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

def is_flagged_by_moderation(text: str) -> bool:
    moderation_resp = oa_client.moderations.create(input=text)
    return moderation_resp.results[0].flagged

def handle_user_query(user_query: str):
    if is_flagged_by_moderation(user_query):
        return {
            "result": "⚠️ Your message contains inappropriate language or violates our safety guidelines. I cannot continue this conversation.",
            "recommended_titles": []
        }

def recommend_and_call_tool(user_query: str, summaries: list[str], metadatas: list[dict]) -> dict:
    system_prompt = (
        "You are a helpful assistant that recommends books based only on the provifded summaries.\n"
        "Each summary includes the title of the book.\n\n"

        "📚 Recommendation Rules:\n"
        "- Only recommend books that appear in the provided summaries.\n"
        "- Do not invent or mention any book that is not included.\n"
        "- If no suitable match is found, respond politely that no recommendation can be made.\n"
        "- If the user asks for exactly one book (e.g., using phrases like 'only one', 'just one', or 'exactly one'), you must return only a single recommendation.\n"
        "- If the user does not specify a number, and multiple books match, you should list all relevant titles.\n"
        "- Never recommend more books than the user requested.\n"
        "- Format your response as a bullet list.\n"
        "- Each bullet must begin with the book title in **double asterisks**, followed by a short reason for the match.\n"


        "🛠️ Tool Usage:\n"
        "- When the user clearly asks to describe, explain, or summarize a specific book (e.g., 'What is The Great Gatsby about?', 'Describe 1984'), treat it as a direct summary request.\n"
        "- In such cases, do NOT present a list or use recommendation formatting. Instead, respond with a single paragraph that begins with the book title in **double asterisks**.\n"
        "- Example: '**The Hobbit** is a fantasy novel about a reluctant hobbit...'\n"
        "- When recommending books (e.g., based on themes), list them as bullets. Each bullet must begin with the title in **double asterisks**, followed by a reason.\n"
        "- Always use the exact book title from the summaries.\n"


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

    # ✅ If GPT made a tool call
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "get_summary_by_title":
            summary = get_summary_by_title(args["title"])

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

    # ❌ Fallback — if no tool call, format the summaries manually
    result_text = msg.content or ""
    titles = extract_titles_from_response(result_text)

    if titles:
        final_result = format_recommendations(titles)
    else:
        final_result = result_text

    return {
        "result": final_result,
        "recommended_titles": titles
    }


def generate_image(prompt: str) -> str:
    image_response = oa_client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="low"  # sau "high" pentru calitate mai bună
    )

    # Retunreaza direct imaginea ca base64, fără să o salvăm
    return image_response.data[0].b64_json


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