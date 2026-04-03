# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for generating Easter egg hunts. It reads markdown files containing trivia questions and CSV files containing location data, then produces LaTeX/PDF output with shuffled questions and answers mapped to specific hiding locations.

## Quick Start Commands

```bash
# Setup (install dependencies)
uv venv
source .venv/bin/activate
uv pip install pandas pytest

# Build the question set
make questions.md    # Generate normalized markdown questions file
make questions.pdf   # Generate final printable PDF
make questions.tex   # Generate LaTeX output

# Run tests
python -m pytest
# Or with uv:
uv run pytest

# Run a single test
uv run pytest tests/test_parse_markdown.py::test_parse_markdown -v
```

## Architecture Overview

### Directory Structure

```
easter-egg-hunt/
├── data/
│   ├── questions/
│   │   ├── iyra_questions.md
│   │   ├── ezra_questions.md
│   │   └── sascha_questions.md
│   └── locations/
│       ├── locations.csv
│       └── redherringlocations.csv
├── src/
│   └── parse_markdown.py
├── tests/
│   └── test_parse_markdown.py
├── archive/          # Archived/supplemental question files
├── output/           # Generated PDFs and exports
├── questions.md      # Normalized output (do NOT edit)
└── questions.pdf     # Final printable PDF (do NOT edit)
```

### Source Files (Source of Truth)

1. **Question banks** - Three hunters, located in `data/questions/`:
   - `iyra_questions.md` - Math/science questions
   - `ezra_questions.md` - General knowledge questions
   - `sascha_questions.md` - Mixed questions (math, science, geography, history)

2. **Location CSV files** - Located in `data/locations/`:
   - `locations.csv` - Real hiding locations (~89 rows)
   - `redherringlocations.csv` - Fake locations to mislead hunters

### Build Pipeline

The build process flows as follows:

```
[Source files]
    │
    ├── [data/questions/iyra_questions.md]
    ├── [data/questions/ezra_questions.md]
    ├── [data/questions/sascha_questions.md]
    │
    ├── [data/locations/locations.csv]
    └── [data/locations/redherringlocations.csv]
    │
    └──> src/parse_markdown.py
        │
        ├── process questions
        ├── shuffle answers
        └── map to locations
            │
            ├──> questions.md (normalized markdown)
            │   │
            ├──> questions.tex
            └───> questions.pdf
```

### Key Python Modules

**`src/parse_markdown.py`** - Main build script:
- Reads and parses markdown question files from `data/questions/`
- Reads location data from `data/locations/`
- Each question must have exactly 3 answers
- Shuffles answer-to-location mappings for variety
- Generates LaTeX output with longtable format

**`tests/test_parse_markdown.py`** - Test suite for the parser.

**`Makefile`** - Defines build targets:
- `questions.md` - Generates questions from source markdown
- `questions.tex` - LaTeX source for PDF generation
- `questions.pdf` - Final printable PDF (uses pandoc with xelatex)
- `test` - Runs pytest

### Question Markdown Format

Each hunter's question file must follow this format (located in `data/questions/`):

```markdown
Header Title

More header info

1. What is the capital of France?
   
   1. Paris
   
   2. Lyon
   
   3. Marseille

2. What is 2+2?
   
   1. 3
   
   2. 4
   
   3. 5
```

**Rules:**
- Question lines: top-level numbered items (e.g., `1. Question text`)
- Answer lines: indented and numbered (e.g., `    1. Answer text`)
- Each question must have exactly 3 answers
- Header text before first question is optional

### CSV Schema

Both location files must use this exact header (located in `data/locations/`):

```csv
Room,Place
Attic,On floor
Kitchen,In fridge on top shelf
```

**Rules:**
- Two columns only: `Room` and `Place`
- No partial-null rows (a room with empty place is invalid)
- UTF-8 plain CSV
- Rows are shuffled randomly per build

### Generated Output

The build produces these artifacts in the root directory (do NOT hand-edit):

- `questions.md` - Generated normalized markdown
- `questions.tex` - LaTeX source
- `questions.pdf` - Final printable PDF

Edit only the source files (`data/questions/*_questions.md`, `data/locations/*.csv`).

## Common Issues and Fixes

### Parse/build fails due to wrong indentation

**Symptoms:** Parser complains about malformed answers, questions detected but answers missing.

**Fix:** Ensure each answer is indented with 4 spaces under its question. Keep numbered format for all three answers. Use spaces consistently (avoid mixed tab/space indentation).

### Parse/build fails due to wrong number of questions

**Symptoms:** Validation or tests fail with question count mismatch.

**Fix:** Confirm the source question file has the expected number of top-level question entries (12 per hunter). Ensure each question starts with a numbered item marker and is not accidentally nested.

### Parse/build fails due to CSV partial null rows

**Symptoms:** CSV processing errors, missing location values during build.

**Fix:** Remove rows where `Room` or `Place` is blank. Ensure both columns are present on every non-header row. Re-save as standard CSV and re-run.

### Question count mismatch

**Details:** Each hunter requires exactly 12 questions (`NQS = 12`). If you add/remove questions, you must update the corresponding markdown file.

## Dependencies

- Python 3.10+
- `uv` package manager
- `pandas` for CSV handling
- `pytest` for testing
- `pandoc` for LaTeX conversion
- A TeX distribution with the XeLaTeX engine (`xelatex`)
