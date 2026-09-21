from app.labels import normalize_answers, position_to_label
from app.csv_key import CsvValidationError, parse_answer_key_csv
import pytest


def test_normalize_letter_answers():
    assert normalize_answers(["A", "C", "B"], 5) == [1, 3, 2]


def test_normalize_numeric_answers():
    assert normalize_answers(["1", "3", "2"], 5) == [1, 3, 2]


def test_position_to_label():
    assert position_to_label(1, "ALPHABETIC") == "A"
    assert position_to_label(3, "NUMERIC") == "3"


def test_csv_validation_and_parse():
    csv_text = "test_id,Q1,Q2,Q3\nTest001,A,C,B\n"
    assert parse_answer_key_csv(csv_text, 3, 5, expected_test_code="Test001") == [1, 3, 2]


def test_csv_rejects_wrong_question_count():
    csv_text = "test_id,Q1,Q2\nTest001,A,C\n"
    with pytest.raises(CsvValidationError):
        parse_answer_key_csv(csv_text, 3, 5)


def test_normalize_lowercase_and_whitespace():
    assert normalize_answers([" a ", " c ", " b "], 5) == [1, 3, 2]


def test_normalize_rejects_out_of_bounds():
    with pytest.raises(ValueError, match="outside 1–4"):
        normalize_answers(["E"], 4)
    with pytest.raises(ValueError, match="outside 1–4"):
        normalize_answers(["5"], 4)


def test_normalize_rejects_invalid_symbols_and_empty():
    with pytest.raises(ValueError, match="Invalid answer 'X'"):
        normalize_answers(["X"], 5)
    with pytest.raises(ValueError, match="Empty answer value"):
        normalize_answers([""], 5)
    with pytest.raises(ValueError, match="Empty answer value"):
        normalize_answers([None], 5)


def test_csv_rejects_empty_and_no_header():
    with pytest.raises(CsvValidationError, match="empty"):
        parse_answer_key_csv("", 3, 5)
    with pytest.raises(CsvValidationError, match="no answer row"):
        parse_answer_key_csv("test_id,Q1,Q2,Q3\n", 3, 5)


def test_csv_matching_expected_test_code():
    csv_text = "test_id,Q1,Q2\nTestA,A,B\nTestB,C,D\n"
    assert parse_answer_key_csv(csv_text, 2, 4, expected_test_code="TestB") == [3, 4]

