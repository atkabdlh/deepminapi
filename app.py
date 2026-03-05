from flask import Flask, request, jsonify, send_file
import os
import sys
from services.embedding_service import generate_embedding, generate_multiple_embeddings, base64_to_image
from services.matching_service import best_match, best_match_in_class, get_students_for_class, get_all_students_data
from services.student_service import load_students, save_students
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
    return jsonify({
        "status": "ok",
        "service": "face-attendance-api"
    }), 200

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

# -----------------------------
# Register a student
# -----------------------------
@app.route("/register-student", methods=["POST"])
def register_student():
    try:
        data = request.json
        name = data.get("name")
        image_base64 = data.get("image")

        if not name or not image_base64:
            print("[register] Missing name or image")
            sys.stdout.flush()
            return jsonify({"error": "Missing name or image"}), 400

        print(f"[register] Received request to register student: {name}")
        sys.stdout.flush()

        # Generate embedding directly from base64
        print("[register] Generating embedding...")
        sys.stdout.flush()
        embedding = generate_embedding(image_base64)
        print(f"[register] Embedding generated, length: {len(embedding)}")
        sys.stdout.flush()

        # Load current students
        students = load_students()

        # Append new student
        students.append({
            "name": name,
            "embedding": embedding
        })

        # Save to file
        save_students(students)
        print(f"[register] Student '{name}' saved successfully. Total students: {len(students)}")
        sys.stdout.flush()

        return jsonify({"success": True, "student": name})

    except Exception as e:
        print(f"[register] ERROR: {e}")
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 400

# -----------------------------
# View all students
# -----------------------------
@app.route("/view-students", methods=["GET"])
def view_students():
    students = load_students()
    return jsonify(students)

# -----------------------------
# Export all students
# -----------------------------
# Open in browser: https://your-render-url/export-students
# Download: students.json
@app.route("/export-students", methods=["GET"])
def export_students():
    file_path = "students.json"

    if not os.path.exists(file_path):
        return {"error": "No data found"}, 404

    return send_file(file_path, as_attachment=True)

# -----------------------------
# Import all students
# -----------------------------
@app.route("/import-students", methods=["POST"])
def import_students():
    data = request.json

    if not isinstance(data, list):
        return {"error": "Invalid format"}, 400

    save_students(data)

    return {"success": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)