from app.labels import position_to_label


def serialize_evaluation(submission, test):
    payload = submission.to_summary()
    payload["test_name"] = test.title
    payload["questions"] = []
    answers = sorted(
        submission.answers,
        key=lambda item: item.question.question_number if item.question else 0,
    )
    for answer in answers:
        q_num = answer.question.question_number if answer.question else None
        payload["questions"].append(
            {
                "question_number": q_num,
                "detected_position": answer.detected_position,
                "detected_label": position_to_label(
                    answer.detected_position, test.answer_style, test.choice_count
                ),
                "correct_position": answer.correct_position,
                "correct_label": position_to_label(
                    answer.correct_position, test.answer_style, test.choice_count
                ),
                "status": answer.status,
                "confidence": answer.confidence,
                "fill_scores": answer.fill_scores,
            }
        )
    return payload
