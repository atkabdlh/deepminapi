import time
import os
import json
import logging
import numpy as np
from services.matching_service import best_match, best_match_in_class
from services.memlog_service import log_memory_usage
from services.embedding_service import generate_embedding, remove_temp_image
from services.student_service import load_students, save_students

TEMP_JOB_DIR = "temp_jobs"
COMPLETED_JOB_DIR = "completed_jobs"
os.makedirs(TEMP_JOB_DIR, exist_ok=True)
os.makedirs(COMPLETED_JOB_DIR, exist_ok=True)

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

def process_register(job_data, job_id):
    try:
        name = job_data["name"]
        image_path = job_data["image_path"]

        log_memory_usage(context=f"before processing {name}")
        logger.info(f"[worker] Processing job {job_id} for {name}...")
        embedding = generate_embedding(image_path)
        log_memory_usage(context=f"after embedding {name}")

        # Save student
        students = load_students()
        students = [s for s in students if s["name"] != name]
        students.append({"name": name, "embedding": embedding})
        save_students(students)
        log_memory_usage(context=f"after saving {name}")

        # Mark job done
        job_data["job_status"] = "done"
        filepath = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(filepath, "w") as f:
            json.dump(job_data, f)

        log_memory_usage(context=f"after processing {name}")
        logger.info(f"[worker] Completed job {job_id} for {name}")
    except Exception as e:
        logger.error(f"[worker] Failed job {job_id}: {e}") 

def process_match(job_data, job_id):
    try:
        image_path = job_data["image_path"]

        log_memory_usage(context=f"before processing {image_path}")
        logger.info(f"[worker-matching] Processing job {job_id} for {image_path}...")

        try:
            embedding = generate_embedding(image_path)
        except Exception as e:
            if "Face could not be detected" in str(e):
                logger.warning(f"[worker-matching] No face detected for {job_id}")

                job_data["job_status"] = "failed"

                filepath = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
                with open(filepath, "w") as f:
                    json.dump(job_data, f)

                completed_filepath = os.path.join(COMPLETED_JOB_DIR, f"{job_id}.json")
                with open(completed_filepath, "w") as f:
                    json.dump(job_data, f)

                return
            else:
                raise e

        log_memory_usage(context=f"after embedding {image_path}")

        students = load_students()

        log_memory_usage(context=f"before matching {image_path}")
        matches = best_match(embedding, students, threshold=0.8)
        log_memory_usage(context=f"after matching {image_path}")

        job_data["job_status"] = "done"
        job_data["matches"] = matches

        filepath = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(filepath, "w") as f:
            json.dump(job_data, f)

        completed_filepath = os.path.join(COMPLETED_JOB_DIR, f"{job_id}.json")
        with open(completed_filepath, "w") as f:
            json.dump(job_data, f)

        logger.info(f"[worker-matching] Completed job {job_id}")

    except Exception as e:
        logger.error(f"[worker-matching] Failed job {job_id}: {e}")

def process_match_class(job_data, job_id):
    try:
        image_path = job_data["image_path"]
        
        log_memory_usage(context=f"before processing {image_path}")
        logger.info(f"[worker-matching-class] Processing job {job_id} for {image_path}...")
        embedding = generate_embedding(image_path)
        log_memory_usage(context=f"after embedding {image_path}")

        # Load students
        students = load_students()
        log_memory_usage(context=f"after loading students {image_path}")

        # Find matches
        log_memory_usage(context=f"before matching {image_path}")
        matches = best_match_in_class(embedding, students, class_id=job_data["class_id"], threshold=0.8)
        log_memory_usage(context=f"after matching {image_path}")

        # Mark job done
        job_data["job_status"] = "done"
        filepath = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")
        with open(filepath, "w") as f:
            json.dump(job_data, f)

        log_memory_usage(context=f"after processing {image_path}")
        logger.info(f"[worker-matching-class] Completed job {job_id} for {image_path} with {matches}")
        
    except Exception as e:
        logger.error(f"[worker-matching-class] Failed job {job_id}: {e}")

def background_worker():
    logger.info("[background_worker] Starting background worker...")
    while True:
        for filename in os.listdir(TEMP_JOB_DIR):
            if not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(TEMP_JOB_DIR, filename)

            with open(filepath, "r") as f:
                job_data = json.load(f)

            job_id = filename.replace(".json", "")

            if job_data["job_status"] == "done" or job_data["job_status"] == "failed":
                remove_temp_image(job_id)
                continue

            if job_data["job_status"] != "pending":
                continue
            job_type = job_data["job_type"]
            if job_type == "register":
                process_register(job_data, job_id)
            elif job_type == "match_student":
                process_match(job_data, job_id)
            elif job_type == "match_in_class":
                process_match_class(job_data, job_id)
        time.sleep(2)  # check every 2 seconds
        # log_memory_usage("worker idle")


if __name__ == "__main__":
    background_worker()