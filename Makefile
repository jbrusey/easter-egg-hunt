# Easter egg hunt 2024
#
# Modifications
#
# 1. revert to 2019 approach based on latex

# Procedure
#
# 1. write the questions into iyra_questions.md etc
# 2. select the locations in locations.csv
# 3. select red herring locations in redherringlocations.csv
# 4. run make


OUTPUT_DIR := output

$(OUTPUT_DIR)/questions.pdf: $(OUTPUT_DIR)/questions.md
	pandoc $(OUTPUT_DIR)/questions.md -s -o $(OUTPUT_DIR)/questions.pdf \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"
#	    -V classoption=landscape \

$(OUTPUT_DIR)/questions.tex: $(OUTPUT_DIR)/questions.md
	pandoc $(OUTPUT_DIR)/questions.md -s -o $@ \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"

$(OUTPUT_DIR)/questions.md: src/parse_markdown.py data/questions/iyra_questions.md data/questions/ezra_questions.md data/questions/sascha_questions.md data/locations/locations.csv data/locations/redherringlocations.csv
	python3 src/parse_markdown.py >$@


out-2019.tex: questions-iyra.tex questions-ezra.tex questions-sascha.tex locations.csv
	python parse_latex.py >$@

test:
	python -m pytest
