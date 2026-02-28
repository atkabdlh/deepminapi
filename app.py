from flask import Flask, request, jsonify
from services.embedding_service import generate_embedding
from services.matching_service import find_best_match

app = Flask(__name__)

# -----------------------------
# Global constants
# -----------------------------
MATCH_THRESHOLD = 0.6


# -----------------------------
# Search through all students
# -----------------------------
@app.route("/get_all_students", methods=["POST"])
def get_all_students():
    try:
        data = request.json
        image_base64 = data["image"]

        embedding = generate_embedding(image_base64)
        student = best_match(embedding)

        if student:
            return jsonify({
                "matched": True,
                "student": student
            })
        else:
            return jsonify({"matched": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -----------------------------
# Search through students in a class
# -----------------------------
@app.route("/get-students-in-class", methods=["POST"])
def get_students_in_class():
    try:
        data = request.json
        class_id = data["class_id"]
        image_base64 = data["image"]

        embedding = generate_embedding(image_base64)
        student = best_match_in_class(class_id, embedding)

        if student:
            return jsonify({
                "matched": True,
                "student": student
            })
        else:
            return jsonify({"matched": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -----------------------------
# Embed multiple students
# -----------------------------
@app.route("/generate-multiple-embeddings", methods=["POST"])
def generate_multiple_embeddings():
    try:
        data = request.json
        images_base64 = data["images"]

        embeddings = generate_multiple_embeddings(images_base64)

        return jsonify({
            "embeddings": embeddings
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -----------------------------
# Embed one student
# -----------------------------
@app.route("/generate-single-embedding", methods=["POST"])
def generate_single_embedding():
    try:
        data = request.json
        image_base64 = data["image"]

        embedding = generate_embedding(image_base64)

        return jsonify({
            "embedding": embedding
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)