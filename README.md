# Smart Scribe – AI Book Recommender

Smart Scribe is a book recommendation web application powered by an LLM (OpenAI). It allows users to request book suggestions, view summaries retrieved from a local vector store, and interact via a simple HTML/CSS UI with optional text-to-speech and image generation.

---

## Features

- Book suggestions using OpenAI LLM + tool calls
- Embedded `get_summary_by_title()` tool
- 10+ book summaries embedded and searchable with ChromaDB
- Image generation (optional) for book covers
- Text-to-speech summaries (OpenAI TTS)
- Animated UI with floating books
- Streamlined Flask backend
- Markdown-based answer formatting

---

## Project Structure
```
├── app.py # Flask app entrypoint
├── gpt_interface.py # LLM communication, moderation, tool usage
├── summary.py # get_summary_by_title() tool
├── rag_core.py # Embedding + vector DB setup
├── process_books.py # Embeds summaries into ChromaDB
├── data/
│ └── book_summ.txt # Contains 10+ book summaries
├── static/
│ ├── main.js # JS: voice, animation, TTS
│ ├── style.css # CSS styles and animations
│ └── img/book-icon.png # Book icon used for floating effect
├── templates/
│ ├── layout.html # Base HTML layout
│ ├── index.html # Main interface
│ └── component/ # HTML components (form, result)
├──tests
│ ├── test_app.py
│ ├── test_gpt_interface.py
│ ├── test_rag_core.py
│ └── test_summary.py
├── .env # Contains your OpenAI API key
└── README.md
```

## After Cloning the Repo

1. **Create a virtual environment**

<details>
<summary>Linux / macOS</summary>

```bash
python -m venv .venv
source .venv/bin/activate
```

</details>

<details>
<summary>Windows</summary>

```bash
python -m venv .venv
.venv\Scripts\activate
```

</details>

---

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

3. **Add your OpenAI API key to a `.env` file**

```env
OPENAI_API=your-api-key-here
```

---

4. **Initialize vector store (ChromaDB)**

```bash
python process_books.py
```

---

5. **Start the Flask app**

```bash
python app.py
```

---

6. **Visit the app in your browser**

[http://localhost:5000](http://localhost:5000)
