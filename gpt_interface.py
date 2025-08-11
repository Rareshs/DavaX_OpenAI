from flask import json
from openai import OpenAI
import os
import dotenv
import uuid
import os
from summary import get_summary_by_title
import base64


dotenv.load_dotenv()
oa_client = OpenAI(api_key=os.getenv("OPENAI_API"))

def extract_themes(query: str) -> str:
    system_prompt = (
        "You are an AI that extracts key literary themes or topics from a user question. "
        "Return only a comma-separated list of 2–3 keywords. Respond in English regardless of the input language."
    )
    completion = oa_client.chat.completions.create(
        model="gpt-4",
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
        "You are a helpful assistant that recommends books based only on the provided summaries. "
        "Each summary includes the title of the book. "
        "Do not invent or mention any book that is not included in the summaries. "
        "If none of the books are suitable, respond politely that no recommendation can be made. "
        "If multiple books match the user's interests, you must list all of them. "
        "Format your response as a bullet list. "
        "Each list item must start with the book title in bold, followed by a short reason why it matches the user's request. "
        "Do not omit any relevant book from the summaries. "
        "Only if you are recommending exactly one book, you may use a tool to return its full summary. "
        "You should not respond to offensive language or inappropriate content. "
        "You must respond politely with a warning and do NOT continue the conversation or generate a recommendation."
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
        model="gpt-4-0613",
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
                model="gpt-4-0613",
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
            return followup.choices[0].message.content

    # Fallback if no tool is called
    return msg.content


def generate_image(prompt: str) -> str:
    image_response = oa_client.images.generate(
        model="gpt-image-1",  # sau gpt-4o, gpt-4.1 (care suportă tool image)
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