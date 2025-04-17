""" parse_markdown.py

Parse markdown file into questions and answers

J. Brusey, March, 2018 -- April, 2025
"""

import pandas as pd
from random import shuffle
import csv
import re
import pandas as pd
from typing import List, Tuple, Dict, Any

# Constants
NQS: int = 12
NAS: int = 3


def read_lines(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.rstrip() for line in file]


def parse_header(lines: List[str]) -> Tuple[str, int]:
    header_lines: List[str] = []
    i: int = 0
    while i < len(lines) and not re.match(r"^\d+\.\s+", lines[i]):
        header_lines.append(lines[i])
        i += 1
    header: str = "\n".join(header_lines).strip()
    return header, i


def parse_question(lines: List[str], i: int) -> Tuple[Tuple[str, str], int]:
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not re.match(r"^\d+\.\s+", lines[i]):
        raise ValueError(f"Expected a question at line index {i}")
    q_lines: List[str] = [lines[i].strip()]
    i += 1
    while i < len(lines) and lines[i] and not lines[i].startswith("    "):
        q_lines.append(lines[i].strip())
        i += 1
    question_text: str = " ".join(q_lines)
    match = re.match(r"(\d+)\.\s+(.*)", question_text)
    if not match:
        raise ValueError(f"Invalid question format: '{question_text}'")
    return match.groups(), i


def parse_answer(lines: List[str], i: int) -> Tuple[str, int]:
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not (
        lines[i].startswith("    ") and re.match(r" {4}\d+\.\s+", lines[i])
    ):
        raise ValueError(
            f"Invalid answer start format at line index {i}: "
            f"'{lines[i] if i < len(lines) else 'EOF'}'"
        )
    ans_lines: List[str] = [lines[i].lstrip()]
    i += 1
    while (
        i < len(lines)
        and lines[i].startswith("    ")
        and not re.match(r" {4}\d+\.\s+", lines[i])
    ):
        if lines[i].strip():
            ans_lines.append(lines[i].strip())
        i += 1
    ans_text: str = " ".join(ans_lines)
    match = re.match(r"(\d+)\.\s+(.*)", ans_text)
    if not match:
        raise ValueError(f"Invalid answer format: '{ans_text}'")
    return match.group(2), i


def parse_questions(lines: List[str], i: int) -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []
    while i < len(lines):
        (q_number, q_body), i = parse_question(lines, i)
        answers: List[str] = []
        for _ in range(3):
            ans_body, i = parse_answer(lines, i)
            answers.append(ans_body)
        questions.append({"question": q_body, "options": answers})
    return questions


def parse_markdown(file_path: str) -> List[Dict[str, Any]]:
    lines: List[str] = read_lines(file_path)
    _header, index = parse_header(lines)
    return parse_questions(lines, index)


def format_question(
    hunter: str,
    question: str,
    answers: List[str],
    thisloc: Tuple[str, str],
    therelocs: List[Tuple[str, str]],
) -> str:
    paired = list(zip(answers, therelocs))
    shuffle(paired)
    # Build lines for the 3 numbered answers
    numbered_answers = [
        rf"\item {ans} $\Rightarrow$ {loc[1]} ({loc[0]})"
        for i, (ans, loc) in enumerate(paired)
    ]
    # Return LaTeX, one row in the table, with newlines
    return "\n".join(
        [
            rf"{thisloc[1]} ({thisloc[0]}): ({hunter}) {question}",
            r"\begin{enumerate}",
            *numbered_answers,
            r"\end{enumerate}\\",
            r"\hline",
        ]
    )


def load_locations(locations_file: str, red_herring_file: str) -> List[Tuple[str, str]]:
    """
    Load locations from two CSV files, shuffle, and return as a list of tuples.

    Rows that are entirely null are dropped.
    If any row contains partial nulls, a ValueError is raised.
    """
    df_locations = pd.read_csv(locations_file)
    df_locations = df_locations.sample(frac=1).reset_index(drop=True)
    df_red = pd.read_csv(red_herring_file)
    combined = pd.concat([df_locations, df_red], ignore_index=True)

    # Drop rows where all columns are null.
    combined = combined.dropna(how="all")

    # Check for rows with partial nulls: Some fields are missing but not all.
    partial_null = combined.isnull().any(axis=1) & ~combined.isnull().all(axis=1)
    if partial_null.any():
        raise ValueError("Encountered row with partial nulls")

    return [tuple(row) for row in combined.itertuples(index=False)]


def get_hunter_questions(hunters: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """For each hunter, parse their markdown file of questions and return a dict mapping."""
    return {h: parse_markdown(f"{h.lower()}_questions.md") for h in hunters}


def process_all(
    hunters: List[str],
    locations: List[Tuple[str, str]],
    hunter_questions: Dict[str, List[Dict[str, Any]]],
    nqs: int = NQS,
    nas: int = NAS,
    beforetext: str = "",
    aftertext: str = "",
) -> str:
    """
    Format all questions for all hunters and return the combined output.

    For each hunter the function:
      - Determines a list of locations (the first is a static start clue)
      - Selects the remaining locations from their allocated chunk
      - Prepares 'other locations' from the rest of the locations for red herrings
      - Formats each question by calling format_question.
    """
    output_lines = [beforetext] if beforetext else []
    for person, h in enumerate(hunters):
        # Select this hunter's dedicated locations and create a starting location
        start_idx = person * nqs
        end_idx = (person + 1) * nqs
        locs: List[Tuple[str, str]] = [("Start clue", "")] + locations[
            start_idx:end_idx
        ]
        # For red herrings, all locations not assigned to this hunter
        otherlocs: List[Tuple[str, str]] = locations[:start_idx] + locations[end_idx:]
        shuffle(otherlocs)
        questions = hunter_questions[h]
        if len(questions) != nqs:
            raise ValueError(f"Expected {nqs} questions for {h}, got {len(questions)}")
        for i in range(nqs):
            formatted = f"{i+1}. " + format_question(
                hunter=h,
                question=questions[i]["question"],
                answers=questions[i]["options"],
                thisloc=locs[i],
                therelocs=[locs[i + 1]]
                + otherlocs[i * (nas - 1) : (i + 1) * (nas - 1)],
            )
            output_lines.append(formatted)

        # print final location
        output_lines.append(
            rf"{nqs+1}. {locs[-1][1]} ({locs[-1][0]}): ({h}) \textbf{{Congratulations! You found them all}} \\[3ex]\hline"
        )

    if aftertext:
        output_lines.append(aftertext)
    return "\n".join(output_lines)


def main() -> None:
    """Main function to run the whole process."""
    locations = load_locations("locations.csv", "redherringlocations.csv")
    hunters = ["Iyra", "Ezra", "Sascha"]
    hunter_questions = get_hunter_questions(hunters)
    output = process_all(
        hunters,
        locations,
        hunter_questions,
        nqs=NQS,
        nas=NAS,
        beforetext=r"\renewcommand{\arraystretch}{1.3}\setlength{\extrarowheight}{1ex}\begin{longtable}{p{\textwidth}}",
        aftertext=r"\end{longtable}",
    )
    print(output)


if __name__ == "__main__":
    main()
