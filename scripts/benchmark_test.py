import os
import base64
import json
import requests

IMAGE_DIR = "./test_images"
API_URL = "http://localhost:5001/generate-multiple-embeddings"

students = []

for filename in os.listdir(IMAGE_DIR):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    filepath = os.path.join(IMAGE_DIR, filename)
    name = os.path.splitext(filename)[0]

    with open(filepath, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    students.append({
        "name": name,
        "image": img_b64
    })

data = {"students": students}

# Optional: save JSON to file
with open("students.json", "w") as f:
    json.dump(data, f, indent=2)

# Send to API
response = requests.post(API_URL, json=data)
print(f"Status code: {response.status_code}")
print(response.text)