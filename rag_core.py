# rag_core.py
import os
import hashlib
import re
import dotenv
from openai import OpenAI
from chromadb import PersistentClient

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API")
EMBEDDING_MODEL = "text-embedding-3-small"
oa_client = OpenAI(api_key=OPENAI_API_KEY)

def setup_chroma():
    client = PersistentClient(path="./chroma_book_db")
    return client.get_or_create_collection(name="book_recom")

def generate_id(title: str) -> str:
    return hashlib.md5(title.encode("utf-8")).hexdigest()

def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    response = oa_client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def parse_books(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    entries = re.findall(r"## Title: (.*?)\n(.*?)(?=\n## Title:|\Z)", text, re.DOTALL)
    return [{"title": title.strip(), "summary": summary.strip()} for title, summary in entries]
