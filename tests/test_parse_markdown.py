# test_parse_markdown.py
import pytest
import pandas as pd
from io import StringIO
import numpy as np

from src.parse_markdown import (
    NQS,
    NAS,
    load_locations,
    get_hunter_questions,
    process_all,
    format_question,
    parse_markdown,
    normalize_asset_paths,
)


def _build_question_block(question_number: int, answer_numbers=(1, 2, 3)) -> str:
    answer_lines = "\n".join(
        [f"    {answer_no}. Option {question_number}-{answer_no}" for answer_no in answer_numbers]
    )
    return f"{question_number}. Question {question_number}?\n\n{answer_lines}\n"


@pytest.fixture
def sample_file_path(tmp_path):
    question_blocks = [_build_question_block(i) for i in range(1, NQS + 1)]
    content = "Header Title\nMore header info\n\n" + "\n".join(question_blocks)
    file_path = tmp_path / "sample.md"
    file_path.write_text(content)
    return file_path


def test_parse_markdown(sample_file_path):
    questions = parse_markdown(str(sample_file_path))
    assert len(questions) == NQS

    assert questions[0]["question"] == "Question 1?"
    assert questions[0]["options"] == ["Option 1-1", "Option 1-2", "Option 1-3"]

    assert questions[-1]["question"] == f"Question {NQS}?"
    assert questions[-1]["options"] == [
        f"Option {NQS}-1",
        f"Option {NQS}-2",
        f"Option {NQS}-3",
    ]


def test_format_question_latex(monkeypatch):
    hunter = "Alice"
    question = "What is 2+2?"
    answers = ["4", "3", "5"]
    thisloc = ("A1", "Start")
    therelocs = [("B1", "North"), ("C1", "East"), ("D1", "South")]

    # Force a predictable shuffle
    monkeypatch.setattr("src.parse_markdown.shuffle", lambda x: None)

    # Example LaTeX output you expect from format_question
    expected = "\n".join(
        [
            r"Start (A1): (Alice) What is 2+2?",
            r"\begin{enumerate}",
            r"\item 4 $\Rightarrow$ North (B1)",
            r"\item 3 $\Rightarrow$ East (C1)",
            r"\item 5 $\Rightarrow$ South (D1)",
            r"\end{enumerate}\\",
            r"\hline",
        ]
    )

    result = format_question(hunter, question, answers, thisloc, therelocs)
    assert result == expected


def test_normalize_asset_paths():
    legacy = r"\includegraphics{./Pictures/example.png}"
    nested = r"\includegraphics{../../assets/images/example.png}"
    expected = r"\includegraphics{assets/images/example.png}"
    assert normalize_asset_paths(legacy) == expected
    assert normalize_asset_paths(nested) == expected


def test_parse_markdown_fails_on_out_of_order_question_numbers(tmp_path):
    numbers = list(range(1, NQS + 1))
    numbers[4], numbers[5] = numbers[5], numbers[4]
    content = "\n".join(_build_question_block(i) for i in numbers)
    file_path = tmp_path / "out_of_order.md"
    file_path.write_text(content)

    with pytest.raises(ValueError, match=r"out_of_order\.md: question index 5 has number 6"):
        parse_markdown(str(file_path))


def test_parse_markdown_fails_on_duplicate_question_numbers(tmp_path):
    numbers = list(range(1, NQS + 1))
    numbers[6] = 6
    content = "\n".join(_build_question_block(i) for i in numbers)
    file_path = tmp_path / "duplicate.md"
    file_path.write_text(content)

    with pytest.raises(ValueError, match=r"duplicate\.md: question index 7 has number 6"):
        parse_markdown(str(file_path))


def test_parse_markdown_fails_on_malformed_answer_numbering(tmp_path):
    blocks = [_build_question_block(i) for i in range(1, NQS + 1)]
    blocks[2] = _build_question_block(3, answer_numbers=(1, 3, 4))
    content = "\n".join(blocks)
    file_path = tmp_path / "bad_answers.md"
    file_path.write_text(content)

    with pytest.raises(
        ValueError,
        match=r"bad_answers\.md: question index 3 has malformed answer numbering",
    ):
        parse_markdown(str(file_path))


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
    monkeypatch.setattr("src.parse_markdown.parse_markdown", dummy_parse_markdown)
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
    monkeypatch.setattr("src.parse_markdown.shuffle", lambda x: None)

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

    # Check that the line that contains the word "Congratulations" also contains the word "Alice"

    # start by splitting the output into lines
    lines = output.split("\n")

    # find the line that contains "Congratulations"
    congrats_line = [line for line in lines if "Congratulations" in line]
    assert len(congrats_line) == 1

    # check that the line contains "Alice"
    assert "Alice" in congrats_line[0]
