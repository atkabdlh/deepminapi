from flask import Flask, request, jsonify, send_file
import os
import json
from uuid import uuid4
import logging
from services.embedding_service import save_temp_image
from services.student_service import save_students

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
        "status": "success",
        "message": "Server is running"
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
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        job_id = uuid4().hex
        save_temp_image(job_id, image_base64)

        job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(job_file, "w") as f:
            json.dump({ "image": image_base64, "job_status": "pending", "job_type": "matching" }, f)

        logger.info(f"[job] Created job {job_id} for matching")
        return jsonify({"status": "success", "message": f"Job {job_id} created for matching", "job_id": job_id, "job_status": "pending"})

    except Exception as e:
        logger.exception("[job] ERROR in get_all_students_endpoint")
        return jsonify({"status": "error", "message": str(e) if str(e) else f"Error matching student"}), 400

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
            return jsonify({"status": "error", "message": "No class_id provided"}), 400
        if not image_base64:
            logger.warning("get_students_in_class: no image provided")
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        job_id = uuid4().hex
        save_temp_image(job_id, image_base64)

        job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(job_file, "w") as f:
            json.dump({ "class_id": class_id, "image": image_base64, "job_status": "pending", "job_type": "match_in_class" }, f)

        logger.info(f"[job] Created job {job_id} for match_in_class")
        return jsonify({"status": "success", "message": f"Job {job_id} created for match_in_class, {class_id}", "job_id": job_id, "job_status": "pending"})

    except Exception as e:
        logger.exception("[job] ERROR in get_students_in_class_endpoint")
        return jsonify({"status": "error", "message": str(e) if str(e) else f"Error searching for student in {class_id}"}), 400

# -----------------------------
# Embed multiple students (benchmark testing)
# -----------------------------
@app.route("/generate-multiple-embeddings", methods=["POST"])
def generate_multiple_embeddings_endpoint():
    try:
        data = request.json
        students = data.get("students")

        if not students or not isinstance(students, list):
            logger.warning("generate_multiple_embeddings: no students or invalid format")
            return jsonify({"status": "error", "message": "No students provided or invalid format"}), 400

        job_id = uuid4().hex
        students_data = []
        for student in students:
            name = student.get("name")
            image_base64 = student.get("image")
            if not name or not image_base64:
                logger.warning(f"generate_multiple_embeddings: missing name or image for student {student}")
                return jsonify({"status": "error", "message": f"Missing name or image for student {student}"}), 400
            students_data.append({"name": name, "image": image_base64})

        save_temp_image(job_id, students_data)

        job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(job_file, "w") as f:
            json.dump({"students": students_data, "job_status": "pending", "job_type": "bulk_register" }, f)
        
        logger.info(f"[job] Created job {job_id} for bulk register")
        return jsonify({"status": "success", "message": f"Job {job_id} created for bulk register, {len(students)} students", "job_id": job_id, "job_status": "pending"})

    except Exception as e:
        logger.exception("[job] ERROR in generate_multiple_embeddings_endpoint")
        return jsonify({"status": "error", "message": str(e) if str(e) else "Error generating multiple embeddings"}), 500

# -----------------------------
# Start registration 
# -----------------------------
@app.route("/register-student", methods=["POST"])
def register_student():
    try:
        data = request.json
        name = data.get("name")
        image_base64 = data.get("image")

        if not name or not image_base64:
            logger.warning("register-student: missing name or image")
            return jsonify({"status": "error", "message": "Missing name or image"}), 400

        job_id = uuid4().hex
        save_temp_image(job_id, name, image_base64)

        job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(job_file, "w") as f:
            json.dump({"name": name, "image": image_base64, "job_status": "pending", "job_type": "register" }, f)

        logger.info(f"[job] Created job {job_id} for student {name}")
        return jsonify({"status": "success", "message": f"Job {job_id} created for {name}", "job_id": job_id, "job_status": "pending"})

    except Exception as e:
        logger.exception("[job] ERROR in register_student")
        return jsonify({"status": "error", "message": str(e) if str(e) else f"Error registering student {name}"}), 500

# -----------------------------
# List jobs (monitoring)
# -----------------------------
@app.route("/list-jobs", methods=["GET"])
def list_jobs():
    jobs = []
    for filename in os.listdir(TEMP_JOB_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(TEMP_JOB_DIR, filename), "r") as f:
                    data = json.load(f)
                jobs.append({
                    "job_id": filename.replace(".json", ""),
                    "name": data.get("name"),
                    "job_status": data.get("job_status"),
                    "job_type": data.get("job_type")
                })
            except Exception as e:
                jobs.append({
                    "job_id": filename.replace(".json", ""),
                    "error": str(e)
                })
    logger.info(f"list_jobs: found {len(jobs)} jobs")
    return jsonify({"status": "success", "message": f"Found {len(jobs)} jobs", "jobs": jobs})



# -----------------------------
# Export all students
# -----------------------------
@app.route("/export-students", methods=["GET"])
def export_students():
    file_path = "students.json"
    if not os.path.exists(file_path):
        logger.warning("export_students: no data found")
        return {"status": "error", "message": "No data found"}, 404

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
        return {"status": "error", "message": "Invalid format"}, 400

    save_students(data)
    logger.info(f"import_students: imported {len(data)} students")
    return {"status": "success", "message": f"Imported {len(data)} students"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)