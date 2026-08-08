import pytest
from pydantic import ValidationError
from ctow_guard.io import load_yaml
from ctow_guard.models import ReviewReport


def test_demo_review_is_fully_independent():
    review = ReviewReport.model_validate(load_yaml("examples/REVIEW-DEMO.yaml"))
    assert review.author_agent != review.reviewer_agent
    assert review.author_session != review.reviewer_session
    assert review.author_dispatch != review.reviewer_dispatch


def test_same_identity_cannot_be_independent_reviewer():
    base = {
        "review_id": "R1", "task_id": "T1",
        "author_agent": "luna-a", "reviewer_agent": "luna-a",
        "author_session": "s1", "reviewer_session": "s2",
        "author_dispatch": "d1", "reviewer_dispatch": "d2",
        "verdict": "PASS", "findings": [],
    }
    with pytest.raises(ValidationError):
        ReviewReport.model_validate(base)
