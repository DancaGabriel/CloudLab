from flask import Flask, request, jsonify, send_from_directory
import requests
import xml.etree.ElementTree as ET
import random
from google import genai

client = genai.Client(api_key="pwp")

app = Flask(__name__, static_folder='frontend', static_url_path='')

@app.route("/api/song", methods=["GET"])
def get_song():
    try:
        response = requests.get("http://localhost:9999/resource")
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            resources = root.findall("resource")
            if resources:
                random_resource = random.choice(resources)
                song = {child.tag: child.text for child in random_resource}
                return jsonify(song)
            return jsonify({"error": "No songs found"}), 404
        return jsonify({"error": f"Error retrieving data: {response.status_code}"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/adapt", methods=["POST"])
def adapt():
    song = request.get_json()
    if not song:
        return jsonify({"error": "No song data provided"}), 400

    prompt = (
        f"Adaptează următoarea melodie pentru un public modern. "
        f"Răspunde în limba română, frumos aranjat, fără text extra, doar răspunsul cu cerință. Scrie o noua melodie in raspuns, frumos aranjată. Ca o piesă modernă.\n"
        f"Titlu: {song.get('title', '')}\n"
        f"Album: {song.get('album', '')}\n"
        f"An: {song.get('year', '')}\n"
        f"Descriere: {song.get('description', '')}\n"
        f"Featuring: {song.get('featuring', '')}\n"
        f"Vizualizări: {song.get('views', '')}\n"
        f"Like-uri: {song.get('likes', '')}\n"
    )


    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/backstory", methods=["POST"])
def backstory():
    song = request.get_json()
    if not song:
        return jsonify({"error": "No song data provided"}), 400

    prompt = (
        f"Explică fundalul cultural și istoric al următoarei melodii. "
        f"Răspunde în limba română, frumos aranjat, fără text extra, doar răspunsul cu cerință. Fă un scris informal.\n"
        f"Titlu: {song.get('title', '')}\n"
        f"Album: {song.get('album', '')}\n"
        f"An: {song.get('year', '')}\n"
        f"Descriere: {song.get('description', '')}\n"
        f"Featuring: {song.get('featuring', '')}\n"
    )


    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True)
