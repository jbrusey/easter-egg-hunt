# Easter egg hunt 2024
#
# Modifications
#
# 1. revert to 2019 approach based on latex

# Procedure
#
# 1. write the questions into qs.py
# 2. select the locations in locations.csv


# Notes:
#
# 1. I didn't do the locations update this year and it caused some
# problems - e.g., missing location. I recommend that you find out how
# parse_latex.py works and ensure that it randomises the locations
# properly.

# 2. There is nothing printed for the last egg.

# 3. It's easy to get confused about which one to stick on where.

# 4. It would be better to output a long table to avoid questions and
# their answers splitting over a page.

questions.pdf: questions.md
	pandoc -s questions.md -o questions.pdf

questions.md: parse-markdown.py iyra_questions.md ezra_questions.md sascha_questions.md locations.csv redherringlocations.csv
	python3 parse-markdown.py >$@


out-2019.tex: questions-iyra.tex questions-ezra.tex questions-sascha.tex locations.csv
	python parse_latex.py >$@

