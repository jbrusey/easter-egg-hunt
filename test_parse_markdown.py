import pytest
import pandas as pd
from io import StringIO
import numpy as np

from parse_markdown import (
    NQS,
    NAS,
    load_locations,
    get_hunter_questions,
    process_all,
    format_question,
    parse_markdown,
)


@pytest.fixture
def sample_file_path(tmp_path):
    content = (
        "Header Title\n"
        "More header info\n"
        "\n"
        "1. What is the capital of France?\n"
        "Additional question info.\n"
        "\n"
        "    1. Paris\n"
        "    extra details\n"
        "\n"
        "    2. Lyon\n"
        "\n"
        "    3. Marseille\n"
        "\n"
        "2. What is 2+2?\n"
        "Simple math question.\n"
        "\n"
        "    1. 3\n"
        "    continued explanation.\n"
        "\n"
        "    2. 4\n"
        "\n"
        "    3. 5\n"
    )
    file_path = tmp_path / "sample.md"
    file_path.write_text(content)
    return file_path


def test_parse_markdown(sample_file_path):
    questions = parse_markdown(str(sample_file_path))
    assert len(questions) == 2

    # Verify the first question and its answers.
    assert (
        questions[0]["question"]
        == "What is the capital of France? Additional question info."
    )
    assert questions[0]["options"][0] == "Paris extra details"
    assert questions[0]["options"][1] == "Lyon"
    assert questions[0]["options"][2] == "Marseille"

    # Verify the second question and its answers.
    assert questions[1]["question"] == "What is 2+2? Simple math question."
    assert questions[1]["options"][0] == "3 continued explanation."
    assert questions[1]["options"][1] == "4"
    assert questions[1]["options"][2] == "5"


def test_format_question(monkeypatch):
    hunter = "Alice"
    question = "What is 2+2?"
    answers = ["4", "3", "5"]
    thisloc = ("A1", "Start")
    therelocs = [("B1", "North"), ("C1", "East"), ("D1", "South")]

    # Patch random.shuffle to preserve the original order for predictable output.
    monkeypatch.setattr("parse_markdown.shuffle", lambda x: None)

    expected = (
        "Start (A1): Alice What is 2+2?\n\n"
        "    1. 4 go to North(B1)\n\n"
        "    2. 3 go to East(C1)\n\n"
        "    3. 5 go to South(D1)\n"
    )
    result = format_question(hunter, question, answers, thisloc, therelocs)
    assert result == expected


# --- Test for load_locations ---
def test_load_locations(monkeypatch):
    from io import StringIO

    # Dummy CSV data for locations and red herrings
    locations_csv = "col1,col2\nA,B\nC,D"
    red_csv = "col1,col2\nE,F"
    df_locations = pd.read_csv(StringIO(locations_csv))
    df_red = pd.read_csv(StringIO(red_csv))

    def fake_read_csv(filename):
        if filename == "locations.csv":
            return df_locations
        elif filename == "redherringlocations.csv":
            return df_red
        raise ValueError("Unexpected file")

    monkeypatch.setattr("pandas.read_csv", fake_read_csv)
    # For determinism, override sample() to return the DataFrame as is.
    monkeypatch.setattr(df_locations, "sample", lambda **kwargs: df_locations)

    locations = load_locations("locations.csv", "redherringlocations.csv")
    expected = {("A", "B"), ("C", "D"), ("E", "F")}
    assert set(locations) == expected


def test_load_locations_failure_on_partial_nulls(monkeypatch):
    # CSV with a row having partial nulls (only one column provided in second row)
    locations_csv = "col1,col2\nA,B\nC,"
    red_csv = "col1,col2\nE,F"
    df_locations = pd.read_csv(StringIO(locations_csv))
    df_red = pd.read_csv(StringIO(red_csv))

    def fake_read_csv(filename: str):
        if filename == "locations.csv":
            return df_locations
        elif filename == "redherringlocations.csv":
            return df_red
        raise ValueError("Unexpected file requested")

    monkeypatch.setattr("pandas.read_csv", fake_read_csv)
    # Override sample to return the DataFrame as-is
    monkeypatch.setattr(df_locations, "sample", lambda **kwargs: df_locations)

    with pytest.raises(ValueError, match="Encountered row with partial nulls"):
        load_locations("locations.csv", "redherringlocations.csv")


def test_load_locations_filters_all_null(monkeypatch):
    # CSV where the second row is completely null and should be filtered out.
    locations_csv = "col1,col2\nA,B\n,\nC,D"
    red_csv = "col1,col2\nE,F"
    df_locations = pd.read_csv(StringIO(locations_csv))
    df_red = pd.read_csv(StringIO(red_csv))

    def fake_read_csv(filename: str):
        if filename == "locations.csv":
            return df_locations
        elif filename == "redherringlocations.csv":
            return df_red
        raise ValueError("Unexpected file requested")

    monkeypatch.setattr("pandas.read_csv", fake_read_csv)
    monkeypatch.setattr(df_locations, "sample", lambda **kwargs: df_locations)

    result = load_locations("locations.csv", "redherringlocations.csv")
    # Expected: first file yields two valid rows after filtering out the completely null row.
    expected = {("A", "B"), ("C", "D"), ("E", "F")}
    assert set(result) == expected


# --- Test for get_hunter_questions ---
def test_get_hunter_questions(monkeypatch):
    # Create a dummy parse_markdown function that returns a fixed list of questions.
    def dummy_parse_markdown(filename: str):
        return [
            {
                "question": f"Question for {filename}",
                "options": ["Opt1", "Opt2", "Opt3"],
            }
            for _ in range(NQS)
        ]

    # Patch the module-level parse_markdown with our dummy.
    monkeypatch.setattr("parse_markdown.parse_markdown", dummy_parse_markdown)
    hunters = ["Alice", "Bob"]
    questions_dict = get_hunter_questions(hunters)
    assert set(questions_dict.keys()) == set(hunters)
    for qs in questions_dict.values():
        assert len(qs) == NQS


# --- Test for process_all ---
def test_process_all(monkeypatch):
    # Set up dummy hunters, locations, and questions.
    hunters = ["Alice"]
    # Create NQS dummy locations – here we use a predictable list
    dummy_locations = [(f"LID{i}", f"Loc{i}") for i in range(NQS)]
    # Create dummy questions for one hunter
    dummy_questions = [
        {
            "question": f"Test question {i}",
            "options": [f"Opt{i}A", f"Opt{i}B", f"Opt{i}C"],
        }
        for i in range(NQS)
    ]
    hunter_questions = {"Alice": dummy_questions}

    # To test determinism, override shuffle in both format_question and process_all.
    monkeypatch.setattr("parse_markdown.shuffle", lambda x: None)

    # Override format_question to a simpler version, if desired.
    # (Here, we use the original implementation so we know what to expect.)
    output = process_all(
        hunters,
        dummy_locations,
        hunter_questions,
        nqs=NQS,
        nas=NAS,
        beforetext="BEFORE",
        aftertext="AFTER",
    )
    # Check that beforetext and aftertext are in the output
    assert "BEFORE" in output
    assert "AFTER" in output
    # Check that at least one dummy question text appears in the output
    assert "Test question 0" in output
