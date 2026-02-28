import numpy as np
from models.student_store import get_students_for_class

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def best_match_in_class(class_id, new_embedding):
    students = get_students_for_class(class_id)

    best_score = -1
    best_student = None

    for student in students:
        score = cosine_similarity(new_embedding, student["embedding"])

        if score > best_score:
            best_score = score
            best_student = student

    if best_score > 0.6:  # tune later
        return best_student

    return None

def best_match( new_embedding):
    students = get_all_students()

    best_score = -1
    best_student = None

    for student in students:
        score = cosine_similarity(new_embedding, student["embedding"])

        if score > best_score:
            best_score = score
            best_student = student

    if best_score > 0.6:  # tune later
        return best_student

    return None