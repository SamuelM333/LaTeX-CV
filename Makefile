.PHONY: cv test clean distclean

LATEXMK = latexmk
PYTHON = python3

cv:
	$(LATEXMK)

test: cv
	$(PYTHON) tests/check_pdfs.py

clean:
	$(LATEXMK) -c

distclean:
	$(LATEXMK) -C
