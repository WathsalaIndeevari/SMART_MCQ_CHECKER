def classify_question(fill_scores, correct_position, mark_threshold=0.35, review_margin=0.08):
    """Return detected_position, status, confidence for one question."""
    if not fill_scores:
        return None, "UNANSWERED", 0.0

    passing = [(index, score) for index, score in enumerate(fill_scores) if score >= mark_threshold]
    confidence = max(fill_scores)

    if not passing:
        return None, "UNANSWERED", confidence

    if len(passing) > 1:
        return None, "MULTIPLE", confidence

    index, score = passing[0]
    detected = index + 1
    if score < mark_threshold + review_margin:
        return detected, "REVIEW_REQUIRED", score

    status = "CORRECT" if detected == correct_position else "INCORRECT"
    return detected, status, score


def summarize_results(question_results, total_questions):
    correct = sum(1 for item in question_results if item["status"] == "CORRECT")
    unanswered = sum(1 for item in question_results if item["status"] == "UNANSWERED")
    multiple = sum(1 for item in question_results if item["status"] == "MULTIPLE")
    review = any(item["status"] == "REVIEW_REQUIRED" for item in question_results)
    incorrect = sum(1 for item in question_results if item["status"] == "INCORRECT")
    percentage = (correct / total_questions) * 100 if total_questions else 0.0
    status = "REVIEW_REQUIRED" if review else "COMPLETED"
    return {
        "correct_count": correct,
        "incorrect_count": incorrect,
        "unanswered_count": unanswered,
        "multiple_count": multiple,
        "total_questions": total_questions,
        "percentage": percentage,
        "status": status,
        "score": correct,
    }
