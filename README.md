# Samuel Murillo - CV

[![Compile PDFs](https://github.com/SamuelM333/LaTeX-CV/actions/workflows/main.yml/badge.svg)](https://github.com/SamuelM333/LaTeX-CV/actions/workflows/main.yml)

My CV in LaTeX, replicating the layout of the Google Docs version: US Letter,
Arial metrics, a grey header bar, a framed photo and a two-column skills
checklist.

| File | Purpose |
| --- | --- |
| `cv.tex` | The CV: layout macros and content |
| `profile.jpg` | Photo shown in the header |
| `tests/check_pdfs.py` | Checks run on the compiled PDF |
| `Dockerfile` | Pinned build environment used by CI |


## Build

The CV uses **LuaLaTeX** driven by **latexmk**. From the repository root:

```bash
make            # or: latexmk
latexmk -pvc    # rebuild on every change
```

The PDF is written to `build/cv.pdf`. `make clean` removes auxiliary files and
`make distclean` also removes the PDF.

A native build needs a full [TeX Live](https://tug.org/texlive/) and two font
families visible to LuaLaTeX:

- **Liberation Sans**, which shares Arial's metrics so lines wrap exactly like
  the Google Docs original.
- **Noto Sans CJK JP Bold**, used for the ✓ checklist marks.

Run `luaotfload-tool --update` if a newly installed font is not found.

### Docker

The `Dockerfile` provides TeX Live and the fonts. CI uses it, so it is the
reference environment:

```bash
docker build --tag cv .
docker run --rm --user "$(id -u):$(id -g)" --volume "$PWD:/doc" cv
```

The base image is pinned to a multi-platform digest and Debian packages come
from a dated snapshot, so rebuilding uses the same TeX and font versions. To
update them, replace the digest with the one from
`docker buildx imagetools inspect texlive/texlive:latest`, pick a matching
[Debian snapshot](https://snapshot.debian.org/) date, then rebuild with
`--pull --no-cache` and compare the PDFs. Dependabot proposes digest and action
updates; the snapshot date is updated by hand.

### VS Code

Install the recommended **LaTeX Workshop** extension and open the repository
root. The workspace settings build with latexmk and read the PDF from `build/`.


## Checks

```bash
make test
```

This builds the CV and runs `tests/check_pdfs.py` (requires Python 3 and
[PyMuPDF](https://pymupdf.readthedocs.io/en/latest/installation.html); both are
in the Docker image). It checks:

- 2 US Letter pages with a text layer and only embedded, non-Type 3 fonts.
- Liberation Sans and Noto Sans CJK JP Bold are used, so lines wrap as intended.
- Key text, all 12 checklist items and the four header links.
- Page 1 ends and page 2 starts where the Google Docs original breaks.
- No missing characters, font warnings or overfull boxes in the compiler log.

`build/quality/` contains a PNG of every page and a JSON report for visual
review.


## CI

Every push and pull request runs **Compile PDFs** (`.github/workflows/main.yml`):
it builds the Docker image, runs `make test` inside it and uploads the PDF, the
compiler log and `build/quality/` as the `cv` artifact. Separate workflows lint
YAML files and GitHub Actions workflows through the shared
[`tedilabs/github-actions`](https://github.com/tedilabs/github-actions)
workflows.


## Credit

The build tooling (Docker image, latexmk setup and CI) comes from
[Awesome CV](https://github.com/posquit0/Awesome-CV), which this repository was
forked from.
