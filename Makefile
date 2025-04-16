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


questions.pdf: questions.md
	pandoc questions.md -s -o questions.pdf \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"
#	    -V classoption=landscape \

questions.tex: questions.md
	pandoc questions.md -s -o $@ \
	    --pdf-engine=xelatex \
	    -V documentclass=scrartcl \
	    -V title="" \
	    -V classoption=DIV=14 \
	    -V pagestyle=empty \
	    -V header-includes="\\usepackage{libertine,longtable,graphicx,array}"


questions.md: parse_markdown.py iyra_questions.md ezra_questions.md sascha_questions.md locations.csv redherringlocations.csv
	python3 parse_markdown.py >$@


out-2019.tex: questions-iyra.tex questions-ezra.tex questions-sascha.tex locations.csv
	python parse_latex.py >$@

test:
	python -m pytest
