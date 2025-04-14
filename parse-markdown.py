""" parse latex file into questions and answers

j. brusey, March 2018
"""

from random import shuffle
import csv
import re
import pandas as pd

HEAD = 1
QUES = 2
ANS = 3

import re


def read_lines(file_path):
    """Read the file and return a list of stripped lines."""
    with open(file_path, "r") as file:
        return [line.rstrip() for line in file]


def parse_header(lines):
    """Parse header lines until the first question is encountered.
    Returns the header string and the current index.
    """
    header_lines = []
    i = 0
    while i < len(lines) and not re.match(r"^\d+\.\s+", lines[i]):
        header_lines.append(lines[i])
        i += 1
    header = "\n".join(header_lines).strip()
    return header, i


def parse_question(lines, i):
    """Parse a single question with optional continuation lines.
    Returns a tuple (question_number, question_text) and the updated index.
    """
    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not re.match(r"^\d+\.\s+", lines[i]):
        raise ValueError("Expected a question at line index {}".format(i))
    # Capture the question and its continuation lines
    q_lines = [lines[i].strip()]
    i += 1
    while i < len(lines) and lines[i] and not lines[i].startswith("    "):
        q_lines.append(lines[i].strip())
        i += 1
    question_text = " ".join(q_lines)
    match = re.match(r"(\d+)\.\s+(.*)", question_text)
    if not match:
        raise ValueError(f"Invalid question format: '{question_text}'")
    return match.groups(), i


def parse_answer(lines, i):
    """Parse a single answer (which may span multiple indented lines).
    Returns the answer text and the updated index.
    """
    # Skip any blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not (
        lines[i].startswith("    ") and re.match(r" {4}\d+\.\s+", lines[i])
    ):
        raise ValueError(
            f"Invalid answer start format at line index {i}: '{lines[i] if i < len(lines) else 'EOF'}'"
        )
    ans_lines = [lines[i].lstrip()]
    i += 1
    # Append continuation lines (still indented and not a new answer start)
    while (
        i < len(lines)
        and lines[i].startswith("    ")
        and not re.match(r" {4}\d+\.\s+", lines[i])
    ):
        if lines[i].strip():
            ans_lines.append(lines[i].strip())
        i += 1
    ans_text = " ".join(ans_lines)
    match = re.match(r"(\d+)\.\s+(.*)", ans_text)
    if not match:
        raise ValueError(f"Invalid answer format: '{ans_text}'")
    return match.group(2), i


def parse_questions(lines, i):
    """Parse all questions and their associated answers starting at index i."""
    questions = []
    while i < len(lines):
        # Parse question
        (q_number, q_body), i = parse_question(lines, i)
        answers = []
        # Expect exactly 3 answers for each question.
        for _ in range(3):
            ans_body, i = parse_answer(lines, i)
            answers.append(ans_body)
        questions.append({"question": q_body, "options": answers})
    return questions


def parse_markdown(file_path):
    """Main function to parse the markdown file."""
    lines = read_lines(file_path)
    header, index = parse_header(lines)
    questions = parse_questions(lines, index)
    return questions


def formatquestion(hunter, question, answers, thisloc, therelocs):
    """format a question and the associated answers

    hunter - this is the name of the person
    question - question text
    answers - list of three answers
    thisloc - location where this egg should be placed
    therelocs - 3 locations where the next egg should be found with only the first being the real location
    """

    j = list(zip(answers, therelocs))

    shuffle(j)
    j = [f"    {i+1}. {al[0]} go to {al[1][1]}({al[1][0]})" for (i, al) in enumerate(j)]

    ans = "\n\n".join(j)
    return f"{thisloc[1]} ({thisloc[0]}): {hunter} {question}\n\n{ans}\n"


NQS = 12
NAS = 3


def main():
    """main code"""

    # locations = readlocations("locations.csv")
    locations = pd.read_csv("locations.csv")

    # randomly shuffle locations
    locations = locations.sample(frac=1).reset_index(drop=True)

    # add some red herring locations
    locations = pd.concat(
        [locations, pd.read_csv("redherringlocations.csv")], ignore_index=True
    )

    # convert dataframe into array of tuples
    locations = [tuple(row) for row in locations.itertuples(index=False)]

    # first person has locs 0-12, second has 13-25, etc.
    hunter = ["Iyra", "Ezra", "Sascha"]

    # parse the question file for each hunter and create a dict
    # relating hunter to the set of questions
    hunter_questions = {parse_markdown(h.lower() + "_questions.md") for h in hunter}

    # shuffle the questions for each hunter
    for h in hunter:
        shuffle(hunter_questions[h])

    beforetext = ""

    aftertext = ""

    # for each person, print the questions and answers
    for person in range(len(hunter)):
        h = hunter[person]
        # locs is taken from nth lot of 13 questions
        locs = [("Start clue", "")] + locations[person * NQS : (person + 1) * NQS]

        # otherlocs is all locations excluding the correct locations for this person
        otherlocs = list(locations[: person * NQS] + locations[(person + 1) * NQS :])
        shuffle(otherlocs)

        # questions is nth lot of 13 questions
        questions = hunter_questions[h]

        if person == 0:
            print(beforetext)
        #        print("% number of qs {}".format(len(questions)))
        assert len(questions) == NQS

        for i in range(NQS):

            s = f"{i+1}. " + formatquestion(
                hunter[person],
                questions[i]["question"],
                questions[i]["options"],
                locs[i],
                [locs[i + 1]] + otherlocs[i * (NAS - 1) : (i + 1) * (NAS - 1)],
            )
            print(s)

    print(aftertext)

    # for line in f:
    #     if state == HEAD:
    #         if "\\item" in line:
    #             state = QUES
    #             aquestion.append(line)
    #         else:
    #             head.append(line)
    #     elif state == QUES:
    #         if "\\begin{enumerate}" in line:
    #             print("ignoring "+repr(line))
    #         elif "\\item" in line:
    #             state = ANS
    #             answers.append(line)
    #         else:
    #             aquestion.append(line) # multiline question
    #     elif state == ANS:
    #         answers.append(line)


if __name__ == "__main__":
    main()
