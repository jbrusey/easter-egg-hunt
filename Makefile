# Easter egg hunt build pipeline (2026)
#
# Current process:
# 1. Update question source files in data/questions/.
# 2. Update location data in data/locations/.
# 3. Run one of the canonical targets:
#    - make questions.pdf
#    - make test


OUTPUT_DIR := output

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
	python3 src/parse_markdown.py >$@

test:
	python -m pytest

help:
	@echo "Canonical commands:"
	@echo "  make questions.pdf   # Generate output/questions.pdf"
	@echo "  make test            # Run test suite"
	@echo ""
	@echo "Intermediary targets (usually not called directly):"
	@echo "  make questions.md    # Generate output/questions.md"
	@echo "  make questions.tex   # Generate output/questions.tex"

.PHONY: questions.md questions.tex questions.pdf test help
