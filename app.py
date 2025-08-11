from flask import Flask, request, render_template,jsonify,url_for
from gpt_interface import extract_themes,generate_speech,recommend_and_call_tool,generate_image
from rag_core import get_embedding, setup_chroma
import os


app = Flask(__name__)
collection = setup_chroma()

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        user_query = request.form.get("query", "")
        if user_query:
            # 1. Extrage temele
            themes = extract_themes(user_query)

            # 2. Facem căutarea semantică în ChromaDB
            embedding = get_embedding(themes)
            results = collection.query(query_embeddings=[embedding], n_results=3)
            summaries = results["documents"][0]
            metadatas = results["metadatas"][0]

            # 3. GPT face recomandarea și decide dacă apelează tool-ul
            result = recommend_and_call_tool(user_query, summaries,metadatas)

    # Trimiți doar result (rezumatul complet e deja inclus în textul GPT)
    return render_template("index.html", result=result)


@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    summary = data.get('summary', '')
    model = data.get('model', 'tts-1')
    voice = data.get('voice', 'nova')

    if not summary:
        return jsonify({'error': 'No summary provided'}), 400

    try:
        filepath = generate_speech(summary, model=model, voice=voice)

        # Normalizează pentru URL (elimină "static/" și înlocuiește \ cu /)
        relative_path = os.path.relpath(filepath, start="static").replace("\\", "/")

        return jsonify({
            'audio_url': url_for('static', filename=relative_path, _external=True)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route("/generate_image", methods=["POST"])
def generate_image_route():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Generează imaginea și salvează fișierul
        image_path = generate_image(prompt)

        # Creează URL-ul public pentru imagine
        relative_path = os.path.relpath(image_path, start="static").replace("\\", "/")
        image_url = url_for("static", filename=relative_path, _external=True)

        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
