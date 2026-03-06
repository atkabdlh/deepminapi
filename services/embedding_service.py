from deepface import DeepFace
import base64
import numpy as np
import cv2
import json
import os
import logging

# preload model once
model = DeepFace.build_model("OpenFace")

TEMP_JOB_DIR = os.path.join(os.path.dirname(__file__), "../temp_jobs")

def remove_temp_image(job_id):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    for filename in os.listdir(TEMP_JOB_DIR):
        if job_id in filename:
            file_path = os.path.join(TEMP_JOB_DIR, filename)
            logger.info(f"{job_id} is done, deleting file: {file_path}")
            if os.path.isfile(file_path):
                os.remove(file_path)
    image_path = os.path.join(TEMP_JOB_DIR, f"{job_id}.jpg")
    if os.path.exists(image_path):
        logger.info(f"{job_id} is done, deleting file: {image_path}")
        os.remove(image_path)
    logger.info(f"Deleted file(s) for {job_id}")
        

def save_image_helper(job_id, image_base64):
    image_bytes = base64.b64decode(image_base64)
    image_path = os.path.join(TEMP_JOB_DIR, f"{job_id}.jpg")
    with open(image_path, "wb") as img:
        img.write(image_bytes)
    return image_path

def save_temp_image(job_id, name=None, image_base64=None, students=None):
    job_file = os.path.join(TEMP_JOB_DIR, f"{job_id}.json")

    if name and image_base64:
        image_path = save_image_helper(job_id, image_base64)
        data = {
            "name": name,
            "image_path": image_path,
            "job_status": "pending"
        }
    elif image_base64 :
        image_path = save_image_helper(job_id, image_base64)
        data = {
            "image_path": image_path,
            "job_status": "pending"
        }
    elif students:
        students_data = []
        for i, student in enumerate(students):
            name = student["name"]
            image_base64 = student["image"]

            if not name or not image_base64:
                raise ValueError(f"Invalid student data: {student}")

            image_path = save_image_helper(job_id + f"_{i}", image_base64)
            students_data.append({
                "name": name,
                "image_path": image_path
            })
        data = {
            "students": students_data,
            "job_status": "pending"
        }
    else:
        raise ValueError("Invalid input")

    with open(job_file, "w") as f:
        json.dump(data, f)
    
    return job_file

def base64_to_image(base64_string):
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def generate_embedding(base64_string):
    img = base64_to_image(base64_string)

    result = DeepFace.represent(
        img_path=img,
        model_name="OpenFace",
        enforce_detection=True
    )

    return result[0]["embedding"]