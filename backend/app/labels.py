LABELS = "ABCDE"


def position_to_label(position, answer_style, choice_count=5):
    if position is None:
        return None
    if answer_style == "NUMERIC":
        return str(position)
    if 1 <= position <= min(choice_count, len(LABELS)):
        return LABELS[position - 1]
    return str(position)


def normalize_answer(value, choice_count):
    if value is None:
        raise ValueError("Empty answer value")
    raw = str(value).strip().upper()
    if not raw:
        raise ValueError("Empty answer value")
    if raw.isdigit():
        position = int(raw)
    elif len(raw) == 1 and raw in LABELS:
        position = LABELS.index(raw) + 1
    else:
        raise ValueError(f"Invalid answer '{value}'")
    if position < 1 or position > choice_count:
        raise ValueError(f"Answer '{value}' is outside 1–{choice_count}")
    return position


def normalize_answers(values, choice_count):
    return [normalize_answer(v, choice_count) for v in values]
