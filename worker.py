import time
import os
import json
from services.embedding_service import generate_embedding, load_students, save_students

TEMP_JOB_DIR = "temp_jobs"
os.makedirs(TEMP_JOB_DIR, exist_ok=True)

def background_worker():
    print("[worker] Starting background worker...")
    while True:
        for filename in os.listdir(TEMP_JOB_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(TEMP_JOB_DIR, filename)
                with open(filepath, "r") as f:
                    job_data = json.load(f)

                if job_data.get("status") == "pending":
                    try:
                        name = job_data["name"]
                        image_base64 = job_data["image"]

                        print(f"[worker] Processing job {filename} for {name}...")
                        embedding = generate_embedding(image_base64)

                        # Save student
                        students = load_students()
                        students.append({"name": name, "embedding": embedding})
                        save_students(students)

                        # Mark job done
                        job_data["status"] = "done"
                        with open(filepath, "w") as f:
                            json.dump(job_data, f)

                        print(f"[worker] Completed job {filename} for {name}")
                    except Exception as e:
                        print(f"[worker] Failed job {filename}: {e}")
        time.sleep(2)  # check every 2 seconds


if __name__ == "__main__":
    background_worker()