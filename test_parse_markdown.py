import pytest
from parse_markdown import parse_markdown


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
