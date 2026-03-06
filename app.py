from flask import Flask, request, jsonify, send_file
import os
import json
from uuid import uuid4
import logging
from services.embedding_service import generate_embedding, generate_multiple_embeddings, save_temp_image
from services.matching_service import best_match, best_match_in_class, get_students_for_class, get_all_students_data
from services.student_service import load_students, save_students

app = Flask(__name__)

# -----------------------------
# Global constants
# -----------------------------
MATCH_THRESHOLD = 0.6
TEMP_JOB_DIR = "temp_jobs"
os.makedirs(TEMP_JOB_DIR, exist_ok=True)

# -----------------------------
# Logging setup
# -----------------------------
LOG_FILE = "server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# Health check
# -----------------------------
@app.route("/health", methods=["GET"])
def health_check():
    logger.info("Health check requested")
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
            logger.warning("get_all_students: no image provided")
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)
        students = get_all_students_data()
        student = best_match(embedding, students, threshold=MATCH_THRESHOLD)

        logger.info(f"get_all_students: matched={bool(student)}")
        return jsonify({"matched": bool(student), "student": student} if student else {"matched": False})

    except Exception as e:
        logger.exception("get_all_students: error processing request")
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
            logger.warning("get_students_in_class: no class_id provided")
            return jsonify({"error": "No class_id provided"}), 400
        if not image_base64:
            logger.warning("get_students_in_class: no image provided")
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)
        students = get_students_for_class(class_id)
        student = best_match_in_class(embedding, students, threshold=MATCH_THRESHOLD)

        logger.info(f"get_students_in_class: class_id={class_id} matched={bool(student)}")
        return jsonify({"matched": bool(student), "student": student} if student else {"matched": False})

    except Exception as e:
        logger.exception("get_students_in_class: error processing request")
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
            logger.warning("generate_multiple_embeddings: no images or invalid format")
            return jsonify({"error": "No images provided or invalid format"}), 400

        embeddings = generate_multiple_embeddings(images_base64)
        logger.info(f"generate_multiple_embeddings: processed {len(embeddings)} embeddings")
        return jsonify({"embeddings": embeddings})

    except Exception as e:
        logger.exception("generate_multiple_embeddings: error processing request")
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
            logger.warning("generate_single_embedding: no image provided")
            return jsonify({"error": "No image provided"}), 400

        embedding = generate_embedding(image_base64)
        logger.info("generate_single_embedding: embedding created")
        return jsonify({"embedding": embedding})

    except Exception as e:
        logger.exception("generate_single_embedding: error processing request")
        return jsonify({"error": str(e)}), 400

# -----------------------------
# Start registration 
# -----------------------------
@app.route("/register-student", methods=["POST"])
def start_register_student():
    try:
        data = request.json
        name = data.get("name")
        image_base64 = data.get("image")

        if not name or not image_base64:
            logger.warning("register-student: missing name or image")
            return jsonify({"error": "Missing name or image"}), 400

        job_id = uuid4().hex
        save_temp_image(job_id, name, image_base64)

        job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.txt")
        with open(job_file, "w") as f:
            json.dump({"name": name, "image": image_base64, "status": "pending"}, f)

        logger.info(f"[job] Created job {job_id} for student {name}")
        return jsonify({"job_id": job_id, "status": "pending"})

    except Exception as e:
        logger.exception("[job] ERROR in start_register_student")
        return jsonify({"error": str(e)}), 500

# -----------------------------
# List jobs 
# -----------------------------
@app.route("/list-jobs", methods=["GET"])
def list_jobs():
    jobs = []
    for filename in os.listdir(TEMP_JOB_DIR):
        if filename.endswith(".txt"):
            try:
                with open(os.path.join(TEMP_JOB_DIR, filename), "r") as f:
                    data = json.load(f)
                jobs.append({
                    "job_id": filename.replace(".txt", ""),
                    "name": data.get("name"),
                    "status": data.get("status")
                })
            except Exception as e:
                jobs.append({
                    "job_id": filename.replace(".txt", ""),
                    "error": str(e)
                })
    logger.info(f"list_jobs: found {len(jobs)} jobs")
    return jsonify(jobs)

# -----------------------------
# View all students
# -----------------------------
@app.route("/view-students", methods=["GET"])
def view_students():
    students = load_students()
    logger.info(f"view_students: {len(students)} students returned")
    return jsonify(students)

# -----------------------------
# Export all students
# -----------------------------
@app.route("/export-students", methods=["GET"])
def export_students():
    file_path = "students.json"
    if not os.path.exists(file_path):
        logger.warning("export_students: no data found")
        return {"error": "No data found"}, 404

    logger.info("export_students: exporting students.json")
    return send_file(file_path, as_attachment=True)

# -----------------------------
# Import all students
# -----------------------------
@app.route("/import-students", methods=["POST"])
def import_students():
    data = request.json
    if not isinstance(data, list):
        logger.warning("import_students: invalid format")
        return {"error": "Invalid format"}, 400

    save_students(data)
    logger.info(f"import_students: imported {len(data)} students")
    return {"success": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)