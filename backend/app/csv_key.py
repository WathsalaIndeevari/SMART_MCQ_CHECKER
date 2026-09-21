import csv
import io

from app.labels import normalize_answer


class CsvValidationError(ValueError):
    pass


def parse_answer_key_csv(file_storage_or_text, question_count, choice_count, expected_test_code=None):
    if hasattr(file_storage_or_text, "read"):
        raw = file_storage_or_text.read()
        if hasattr(file_storage_or_text, "seek"):
            file_storage_or_text.seek(0)
        text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    else:
        text = file_storage_or_text

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise CsvValidationError("CSV is empty or missing a header row.")

    headers = [h.strip() for h in reader.fieldnames if h]
    question_cols = []
    for header in headers:
        upper = header.upper()
        if upper.startswith("Q") and any(ch.isdigit() for ch in upper):
            number = int("".join(ch for ch in upper if ch.isdigit()))
            question_cols.append((number, header))
    question_cols.sort(key=lambda item: item[0])

    if len(question_cols) != question_count:
        raise CsvValidationError(
            f"CSV has {len(question_cols)} question columns but the test has {question_count} questions."
        )

    rows = list(reader)
    if not rows:
        raise CsvValidationError("CSV has a header but no answer row.")

    selected = rows[0]
    test_id_key = next((h for h in headers if h.lower() in {"test_id", "testid", "test_code"}), None)
    if expected_test_code and test_id_key:
        match = next(
            (row for row in rows if str(row.get(test_id_key, "")).strip() == expected_test_code),
            None,
        )
        if match is not None:
            selected = match

    positions = []
    for number, header in question_cols:
        try:
            positions.append(normalize_answer(selected.get(header), choice_count))
        except ValueError as exc:
            raise CsvValidationError(f"Q{number}: {exc}") from exc

    if len(positions) != question_count:
        raise CsvValidationError("The number of answers in the CSV must equal the number of questions.")

    return positions
