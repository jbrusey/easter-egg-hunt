# Easter egg hunt build pipeline (2026)
#
# Current process:
# 1. Update question source files in data/questions/.
# 2. Update location data in data/locations/.
# 3. Run one of the canonical targets:
#    - make questions.pdf
#    - make test


OUTPUT_DIR := output
HUNTERS := Iyra Ezra Sascha
QUESTIONS_DIR := data/questions
LOCATIONS_FILE := data/locations/locations.csv
RED_HERRING_FILE := data/locations/redherringlocations.csv
NQS := 12
NAS := 3

questions.pdf: $(OUTPUT_DIR)/questions.pdf

$(OUTPUT_DIR)/questions.pdf: $(OUTPUT_DIR)/questions.md
	pandoc $(OUTPUT_DIR)/questions.md -s -o $(OUTPUT_DIR)/questions.pdf \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"
#	    -V classoption=landscape \

questions.tex: $(OUTPUT_DIR)/questions.tex

$(OUTPUT_DIR)/questions.tex: $(OUTPUT_DIR)/questions.md
	pandoc $(OUTPUT_DIR)/questions.md -s -o $@ \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"

questions.md: $(OUTPUT_DIR)/questions.md

$(OUTPUT_DIR)/questions.md: src/parse_markdown.py data/questions/iyra_questions.md data/questions/ezra_questions.md data/questions/sascha_questions.md data/locations/locations.csv data/locations/redherringlocations.csv
	python3 src/parse_markdown.py \
	    --hunters $(HUNTERS) \
	    --questions-dir $(QUESTIONS_DIR) \
	    --locations-file $(LOCATIONS_FILE) \
	    --red-herring-file $(RED_HERRING_FILE) \
	    --nqs $(NQS) \
	    --nas $(NAS) >$@

test:
	python -m pytest

print: questions.pdf
	@echo "Printing output/questions.pdf single-sided..."
	lp -o sides=one-sided $(OUTPUT_DIR)/questions.pdf

help:
	@echo "Canonical commands:"
	@echo "  make questions.pdf   # Generate output/questions.pdf"
	@echo "  make print           # Print output/questions.pdf (single-sided)"
	@echo "  make test            # Run test suite"
	@echo ""
	@echo "Intermediary targets (usually not called directly):"
	@echo "  make questions.md    # Generate output/questions.md"
	@echo "  make questions.tex   # Generate output/questions.tex"

.PHONY: questions.md questions.tex questions.pdf test print help
