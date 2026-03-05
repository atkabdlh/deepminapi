from deepface import DeepFace
import base64
import numpy as np
import cv2
import json

# preload model once
model = DeepFace.build_model("OpenFace")

def save_temp_image(job_id, name, image_base64):
    job_file = f"temp_jobs/{job_id}.txt"
    data = {"name": name, "image": image_base64, "status": "pending"}
    with open(job_file, "w") as f:
        json.dump(data, f)

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
    
def generate_multiple_embeddings(base64_strings: list):
    embeddings = []

    for img in base64_strings:
        embedding = generate_embedding(img)
        embeddings.append(embedding)

    return embeddings