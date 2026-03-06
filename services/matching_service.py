import numpy as np

# Example structure of a student:
# {
#     "id": "student_123",
#     "name": "Ali",
#     "class_id": "class_1",
#     "embedding": [0.12, 0.45, ..., 0.87]  # 512-dim float list
# }

# -----------------------------
# Config
# -----------------------------
MATCH_THRESHOLD = 0.6

# -----------------------------
# Load students (in-memory)
# -----------------------------
# These should be replaced with actual DB queries or file loading
_all_students_cache = None
_class_students_cache = {}

def load_all_students():
    global _all_students_cache
    if _all_students_cache is None:
        # Replace this with your DB call or JSON loading
        _all_students_cache = []  # Example: get_all_students_from_db()
    return _all_students_cache

def load_students_for_class(class_id):
    global _class_students_cache
    if class_id not in _class_students_cache:
        # Replace this with DB call or JSON filtering
        all_students = load_all_students()
        _class_students_cache[class_id] = [s for s in all_students if s["class_id"] == class_id]
    return _class_students_cache[class_id]

# -----------------------------
# Cosine similarity
# -----------------------------
def cosine_similarity_matrix(embeddings, new_embedding):
    """
    embeddings: np.array shape (N, D)
    new_embedding: np.array shape (D,)
    returns: np.array shape (N,) of cosine similarities
    """
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    new_embedding_norm = new_embedding / np.linalg.norm(new_embedding)
    return embeddings_norm @ new_embedding_norm

# -----------------------------
# Best match functions
# -----------------------------
def best_match(new_embedding, students=None, threshold=MATCH_THRESHOLD):
    """
    Search all students for best match
    """
    if students is None:
        students = load_all_students()

    if not students:
        return None

    embeddings = np.array([s["embedding"] for s in students])
    new_vec = np.array(new_embedding)

    similarities = cosine_similarity_matrix(embeddings, new_vec)
    idx = np.argmax(similarities)

    if similarities[idx] > threshold:
        return students[idx]
    return None

def best_match_in_class(new_embedding, students=None, class_id=None, threshold=MATCH_THRESHOLD):
    """
    Search students in a class for best match
    """
    if students is None:
        raise ValueError("students list must be provided for class search")

    if not students:
        return None

    if not class_id:
        raise ValueError("class_id must be provided for class search")

    embeddings = np.array([s["embedding"] for s in students if s["class_id"] == class_id])
    new_vec = np.array(new_embedding)

    similarities = cosine_similarity_matrix(embeddings, new_vec)
    idx = np.argmax(similarities)

    if similarities[idx] > threshold:
        return students[idx]
    return None

# -----------------------------
# Helper functions for app.py
# -----------------------------
def get_all_students_data():
    return load_all_students()

def get_students_for_class(class_id):
    return load_students_for_class(class_id)