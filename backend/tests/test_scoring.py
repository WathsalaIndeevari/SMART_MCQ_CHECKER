import numpy as np

from app.scoring import classify_question, summarize_results
from ml_pipeline.evaluate_sheet import fill_ratio


def test_fill_ratio():
    thresh = np.zeros((20, 20), dtype=np.uint8)
    thresh[0:10, 0:10] = 255
    assert fill_ratio(thresh, [0, 0, 10, 10]) == 1.0
    assert fill_ratio(thresh, [10, 10, 10, 10]) == 0.0


def test_unanswered_when_no_bubble_passes():
    detected, status, _conf = classify_question([0.05, 0.04, 0.02], 1)
    assert detected is None
    assert status == "UNANSWERED"


def test_multiple_when_two_bubbles_pass():
    detected, status, _conf = classify_question([0.7, 0.65, 0.1], 1)
    assert detected is None
    assert status == "MULTIPLE"


def test_review_when_close_to_threshold():
    detected, status, _conf = classify_question([0.38, 0.1, 0.1], 1, mark_threshold=0.35, review_margin=0.08)
    assert detected == 1
    assert status == "REVIEW_REQUIRED"


def test_correct_and_incorrect():
    detected, status, _conf = classify_question([0.1, 0.8, 0.05], 2)
    assert detected == 2
    assert status == "CORRECT"
    _detected, status, _conf = classify_question([0.8, 0.1, 0.05], 2)
    assert status == "INCORRECT"


def test_percentage_uses_correct_over_total():
    results = [
        {"status": "CORRECT"},
        {"status": "INCORRECT"},
        {"status": "UNANSWERED"},
        {"status": "MULTIPLE"},
    ]
    summary = summarize_results(results, 4)
    assert summary["score"] == 1
    assert summary["percentage"] == 25
    assert summary["unanswered_count"] == 1
    assert summary["multiple_count"] == 1
    assert summary["status"] == "COMPLETED"


def test_summary_status_review_required_when_any_question_needs_review():
    results = [
        {"status": "CORRECT"},
        {"status": "REVIEW_REQUIRED"},
        {"status": "INCORRECT"},
    ]
    summary = summarize_results(results, 3)
    assert summary["score"] == 1
    assert summary["status"] == "REVIEW_REQUIRED"


def test_fill_ratio_edge_cases():
    thresh = np.zeros((10, 10), dtype=np.uint8)
    assert fill_ratio(thresh, [0, 0, 0, 0]) == 0.0
    assert fill_ratio(thresh, [-5, -5, 0, 0]) == 0.0

