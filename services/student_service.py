import json
import os

STUDENTS_FILE = "students.json"

# -----------------------------
# Caches
# -----------------------------
_all_students_cache = None
_class_students_cache = {}

# -----------------------------
# Load all students
# -----------------------------
def load_students():
    global _all_students_cache
    if _all_students_cache is None:
        if not os.path.exists(STUDENTS_FILE):
            _all_students_cache = []
        else:
            with open(STUDENTS_FILE, "r") as f:
                _all_students_cache = json.load(f)
    return _all_students_cache

# -----------------------------
# Save students
# -----------------------------
def save_students(students):
    global _all_students_cache, _class_students_cache
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students, f, indent=2)

    # Reset caches
    _all_students_cache = students
    _class_students_cache = {}

# -----------------------------
# Load students for a class
# -----------------------------
def load_students_for_class(class_id):
    global _class_students_cache
    if class_id not in _class_students_cache:
        all_students = load_students()
        # Only filter students with class_id
        _class_students_cache[class_id] = [
            s for s in all_students if s["class_id"] == class_id
        ]
    return _class_students_cache[class_id]

# -----------------------------
# Helper functions
# -----------------------------
def get_all_students_data():
    return load_students()

def get_students_for_class(class_id):
    return load_students_for_class(class_id)