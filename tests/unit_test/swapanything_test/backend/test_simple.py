import pandas as pd
from swapanything.backend import simple as backend


def test_simple_backend():
    availabilities = pd.DataFrame(
        [
            {"sub": "sub1", "avail": "a1"},
            {"sub": "sub1", "avail": "a2"},
            {"sub": "sub2", "avail": "a1"},
        ]
    )
    be = backend.SimpleBackend(
        availabilities=availabilities,
        availabilities_column="avail",
        availability_subject_column="sub",
    )

    expected_subjects = pd.DataFrame([{"sub": "sub1"}, {"sub": "sub2"}], index=[0, 2])

    subjects = be.get_subjects()
    assert subjects.equals(expected_subjects)

    assert be.get_availabilities().equals(availabilities)

    assert not be.get_exclusions()


def test_simple_backend_subjects():
    availabilities = pd.DataFrame(
        [
            {"sub": "sub1", "avail": "a1"},
            {"sub": "sub1", "avail": "a2"},
            {"sub": "sub2", "avail": "a1"},
        ]
    )

    orig_subjects = pd.DataFrame(
        [
            {"sub": "sub1", "feat": 1},
            {"sub": "sub2", "feat": 2},
        ]
    )

    be = backend.SimpleBackend(
        availabilities=availabilities,
        availabilities_column="avail",
        availability_subject_column="sub",
        subjects=orig_subjects,
        subject_features=["feat"],
    )

    subjects = be.get_subjects()
    assert subjects.equals(orig_subjects)

    assert be.get_availabilities().equals(availabilities)

    assert not be.get_exclusions()
