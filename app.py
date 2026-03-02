from flask import Flask, request, jsonify
from services.embedding_service import generate_embedding, generate_multiple_embeddings
from services.matching_service import best_match, best_match_in_class, get_students_for_class, get_all_students_data

app = Flask(__name__)

# -----------------------------
# Global constants
# -----------------------------
MATCH_THRESHOLD = 0.6

# -----------------------------
# Health check
# -----------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return {
        "status": "ok",
        "service": "face-attendance-api"
    }, 200

# -----------------------------
# Search through all students
# -----------------------------
@app.route("/get_all_students", methods=["POST"])
def get_all_students_endpoint():
    try:
        data = request.json
        image_base64 = data.get("image")
        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)
        students = get_all_students_data()
        student = best_match(embedding, students, threshold=MATCH_THRESHOLD)

        if student:
            return jsonify({"matched": True, "student": student})
        else:
            return jsonify({"matched": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Search through students in a class
# -----------------------------
@app.route("/get-students-in-class", methods=["POST"])
def get_students_in_class_endpoint():
    try:
        data = request.json
        class_id = data.get("class_id")
        image_base64 = data.get("image")

        if not class_id:
            return jsonify({"error": "No class_id provided"}), 400
        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)
        students = get_students_for_class(class_id)
        student = best_match_in_class(embedding, students, threshold=MATCH_THRESHOLD)

        if student:
            return jsonify({"matched": True, "student": student})
        else:
            return jsonify({"matched": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Embed multiple students
# -----------------------------
@app.route("/generate-multiple-embeddings", methods=["POST"])
def generate_multiple_embeddings_endpoint():
    try:
        data = request.json
        images_base64 = data.get("images")

        if not images_base64 or not isinstance(images_base64, list):
            return jsonify({"error": "No images provided or invalid format"}), 400

        embeddings = generate_multiple_embeddings(images_base64)

        return jsonify({"embeddings": embeddings})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Embed one student
# -----------------------------
@app.route("/generate-single-embedding", methods=["POST"])
def generate_single_embedding_endpoint():
    try:
        data = request.json
        image_base64 = data.get("image")

        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)

        return jsonify({"embedding": embedding})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)