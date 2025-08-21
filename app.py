import uuid
from flask import Flask, request, render_template,jsonify,url_for
from gpt_interface import extract_themes,generate_speech,recommend_and_call_tool,generate_image,speech_to_text, handle_user_query
from rag_core import get_embedding, setup_chroma
import os


app = Flask(__name__)
collection = setup_chroma()

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    recommended_titles = []
    user_query=None

    if request.method == "POST":
        user_query = request.form.get("query", "")
        if user_query:
            try:
                moderation_result = handle_user_query(user_query)
                if moderation_result:
                    result = moderation_result["result"]
                    recommended_titles = moderation_result["recommended_titles"]
                    return render_template("index.html", result=result, recommended_titles=recommended_titles)

                themes = extract_themes(user_query)
                embedding = get_embedding(themes)
                results = collection.query(query_embeddings=[embedding], n_results=3)

                summaries = results["documents"][0] if results and "documents" in results else []
                metadatas = results["metadatas"][0] if results and "metadatas" in results else []

                response = recommend_and_call_tool(user_query, summaries, metadatas)
                result = response.get("result", "No result")
                recommended_titles = response.get("recommended_titles", [])
            except Exception as e:
                result = f"Error processing your request: {e}"
                recommended_titles = []

    return render_template("index.html", result=result, recommended_titles=recommended_titles,last_query=user_query)


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
        # Problema pe windows este că calea are \ în loc de /
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
        image_base64 = generate_image(prompt)
        return jsonify({"image_base64": image_base64})  #fara salvare
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route("/voice_transcribe", methods=["POST"])
def voice_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join("static", "audio_input", f"{uuid.uuid4().hex}.webm")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    audio_file.save(file_path)

    try:
        text = speech_to_text(file_path)
        os.remove(file_path)
        return jsonify({"transcription": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

if __name__ == "__main__":
    app.run(debug=True)
