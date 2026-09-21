import cv2
import numpy as np

from app.scoring import classify_question
from ml_pipeline.utils import get_perspective_transform, preprocess_for_bubbles


class EvaluationError(ValueError):
    pass


def fill_ratio(thresh, box):
    x, y, w, h = box
    x = max(0, x)
    y = max(0, y)
    roi = thresh[y : y + h, x : x + w]
    if roi.size == 0 or w <= 0 or h <= 0:
        return 0.0
    return float(cv2.countNonZero(roi)) / float(w * h)


def evaluate_sheet(
    image_path,
    layout,
    questions,
    template_width,
    template_height,
    mark_threshold=0.35,
    review_margin=0.08,
):
    image = cv2.imread(image_path)
    if image is None:
        raise EvaluationError("Could not read the uploaded answer sheet.")

    warped = get_perspective_transform(image)
    if template_width and template_height:
        warped = cv2.resize(warped, (int(template_width), int(template_height)))

    _gray, thresh = preprocess_for_bubbles(warped)
    results = []

    for question in questions:
        q_num = question.question_number
        bubbles = layout.get(str(q_num)) or layout.get(q_num)
        if not bubbles:
            raise EvaluationError(f"No bubble coordinates stored for question {q_num}.")

        fill_scores = [fill_ratio(thresh, box) for box in bubbles]
        detected, status, confidence = classify_question(
            fill_scores,
            question.correct_position,
            mark_threshold=mark_threshold,
            review_margin=review_margin,
        )
        results.append(
            {
                "question_id": question.id,
                "question_number": q_num,
                "detected_position": detected,
                "correct_position": question.correct_position,
                "fill_scores": [round(score, 4) for score in fill_scores],
                "confidence": round(float(confidence), 4),
                "status": status,
            }
        )

    if not results:
        raise EvaluationError("No questions were evaluated.")

    confidences = [item["confidence"] for item in results]
    if float(np.mean(confidences)) < 0.02:
        raise EvaluationError(
            "The sheet looks blank, blurry, or incomplete. Please upload a clearer photo of the full page."
        )

    return results
