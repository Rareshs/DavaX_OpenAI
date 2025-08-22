import uuid
from flask import Flask, request, render_template, jsonify, url_for
from gpt_interface import extract_themes, generate_speech, recommend_and_call_tool, generate_image, speech_to_text, handle_user_query
from rag_core import get_embedding, setup_chroma
import os

app = Flask(__name__)
collection = setup_chroma()  # Initialize ChromaDB collection for book recommendations

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main route for the web app.
    Handles user queries for book recommendations.
    - On POST: processes the query, checks moderation, extracts themes, gets embeddings,
      queries the vector DB, and generates recommendations.
    - On GET: renders the homepage.
    """
    result = None
    recommended_titles = []
    user_query = None

    if request.method == "POST":
        user_query = request.form.get("query", "")
        if user_query:
            try:
                # Check for inappropriate content
                moderation_response = handle_user_query(user_query)

                # If the input is flagged, stop immediately and show the warning
                if moderation_response is not None:
                    return render_template("index.html", result=moderation_response["result"], recommended_titles=[], last_query=user_query)


                # Extract themes and get embedding for query
                themes = extract_themes(user_query)
                embedding = get_embedding(themes)
                # Query the vector DB for similar books
                results = collection.query(query_embeddings=[embedding], n_results=3)

                # Get summaries and metadata for recommended books
                summaries = results["documents"][0] if results and "documents" in results else []
                metadatas = results["metadatas"][0] if results and "metadatas" in results else []

                # Generate final recommendation and result
                response = recommend_and_call_tool(user_query, summaries, metadatas)
                result = response.get("result", "No result")
                recommended_titles = response.get("recommended_titles", [])
            except Exception as e:
                # Handle any errors during processing
                result = f"Error processing your request: {e}"
                recommended_titles = []

    # Render the homepage with results (if any)
    return render_template("index.html", result=result, recommended_titles=recommended_titles, last_query=user_query)

@app.route('/speak', methods=['POST'])
def speak():
    """
    API endpoint for text-to-speech.
    Expects JSON with 'summary', 'model', and 'voice'.
    Returns a URL to the generated audio file.
    """
    data = request.json
    summary = data.get('summary', '')
    model = data.get('model', 'tts-1')
    voice = data.get('voice', 'nova')

    if not summary:
        return jsonify({'error': 'No summary provided'}), 400

    try:
        filepath = generate_speech(summary, model=model, voice=voice)
        # Normalize path for URL (Windows compatibility)
        relative_path = os.path.relpath(filepath, start="static").replace("\\", "/")
        return jsonify({
            'audio_url': url_for('static', filename=relative_path, _external=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/generate_image", methods=["POST"])
def generate_image_route():
    """
    API endpoint to generate an image from a prompt using AI.
    Expects JSON with 'prompt'.
    Returns base64-encoded image.
    """
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        image_base64 = generate_image(prompt)
        return jsonify({"image_base64": image_base64})  # No file saving
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voice_transcribe", methods=["POST"])
def voice_transcribe():
    """
    API endpoint for speech-to-text transcription.
    Expects an audio file in the 'audio' field of the request.
    Returns the transcribed text.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join("static", "audio_input", f"{uuid.uuid4().hex}.webm")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    audio_file.save(file_path)

    try:
        text = speech_to_text(file_path)
        os.remove(file_path)  # Clean up after transcription
        return jsonify({"transcription": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app in debug mode
