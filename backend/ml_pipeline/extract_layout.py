import cv2

from ml_pipeline.utils import get_perspective_transform, preprocess_for_bubbles, sort_contours


class LayoutError(ValueError):
    pass


def _detect_bubbles(thresh, image_shape):
    height, width = image_shape[:2]
    min_side = min(width, height)
    min_size = max(8, int(min_side * 0.012))
    max_size = max(40, int(min_side * 0.09))

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect = w / float(h) if h else 0
        if min_size <= w <= max_size and min_size <= h <= max_size and 0.7 <= aspect <= 1.3:
            bubbles.append(contour)
    return bubbles


def _split_columns(bubbles):
    if not bubbles:
        return []
    ordered = sort_contours(bubbles, method="left-to-right")
    columns = []
    current = [ordered[0]]
    for index in range(1, len(ordered)):
        _x_prev, _y_prev, w_prev, _h_prev = cv2.boundingRect(ordered[index - 1])
        x_curr, _y_curr, _w_curr, _h_curr = cv2.boundingRect(ordered[index])
        x_prev, _, _, _ = cv2.boundingRect(ordered[index - 1])
        gap = abs(x_curr - x_prev)
        if gap > max(50, w_prev * 1.6):
            columns.append(current)
            current = []
        current.append(ordered[index])
    columns.append(current)
    return columns


def extract_layout(image_path, question_count, choice_count):
    image = cv2.imread(image_path)
    if image is None:
        raise LayoutError("Could not read the blank OMR template image.")

    warped = get_perspective_transform(image)
    _gray, thresh = preprocess_for_bubbles(warped)
    bubbles = _detect_bubbles(thresh, warped.shape)
    expected = question_count * choice_count
    if len(bubbles) < expected:
        raise LayoutError(
            f"Detected {len(bubbles)} bubbles but expected {expected} "
            f"({question_count} questions × {choice_count} choices)."
        )

    columns = _split_columns(bubbles)
    layout = {}
    question_number = 1

    for column in columns:
        col_sorted = sort_contours(column, method="top-to-bottom")
        current_q = []
        last_y = None
        for bubble in col_sorted:
            x, y, w, h = cv2.boundingRect(bubble)
            if last_y is not None and abs(y - last_y) > h / 2 and current_q:
                if len(current_q) != choice_count:
                    raise LayoutError(
                        f"Question {question_number} has {len(current_q)} choices; expected {choice_count}."
                    )
                layout[str(question_number)] = sorted(current_q, key=lambda box: box[0])
                question_number += 1
                current_q = []
            current_q.append([int(x), int(y), int(w), int(h)])
            last_y = y
        if current_q:
            if len(current_q) != choice_count:
                raise LayoutError(
                    f"Question {question_number} has {len(current_q)} choices; expected {choice_count}."
                )
            layout[str(question_number)] = sorted(current_q, key=lambda box: box[0])
            question_number += 1

    if len(layout) != question_count:
        raise LayoutError(
            f"Detected {len(layout)} questions but the test is configured for {question_count}."
        )

    height, width = warped.shape[:2]
    return {
        "layout": layout,
        "width": int(width),
        "height": int(height),
        "questions_detected": len(layout),
        "choices_per_question": choice_count,
    }
