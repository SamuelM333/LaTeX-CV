"""Check the compiled CV; run from the repository root with `make test`."""

import json
from pathlib import Path
import re
import sys
import unicodedata

import pymupdf


OUTPUT = Path("build/quality")
OUTPUT.mkdir(parents=True, exist_ok=True)
PDF = Path("build/cv.pdf")
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def normalized(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def lines(page):
    return [normalized(line) for line in page.get_text().splitlines() if line.strip()]


report = {}
try:
    with pymupdf.open(PDF) as doc:
        check(not doc.is_repaired, "PDF required structural repair")
        check(doc.page_count == 2, f"expected 2 pages, got {doc.page_count}")
        text = normalized(" ".join(page.get_text() for page in doc))
        font_names = set()
        for page in doc:
            label = f"page {page.number + 1}"
            check(all(abs(a - b) < 1 for a, b in
                      zip((page.rect.width, page.rect.height), (612, 792))),
                  f"{label}: expected US Letter, got {page.rect}")
            check(bool(page.get_text().strip()), f"{label}: empty text layer")
            check("\ufffd" not in page.get_text(),
                  f"{label}: replacement character in text layer")
            for font in page.get_fonts(full=True):
                xref, _, kind, base_name = font[:4]
                font_names.add(base_name)
                check(kind != "Type3", f"{label}: Type 3 font {base_name}")
                check(xref > 0 and bool(doc.extract_font(xref)[3]),
                      f"{label}: font is not embedded: {base_name}")
            # Opaque PNGs are review artifacts, not pixel-perfect snapshots.
            page.get_pixmap(dpi=100, alpha=False).save(
                OUTPUT / f"cv-{page.number + 1}.png")

        # Liberation Sans keeps Arial's metrics, so lines wrap like the original.
        for face in ("LiberationSans", "LiberationSans-Bold", "LiberationSans-Italic",
                     "NotoSansCJKjp-Bold"):
            check(any(name.split("+")[-1] == face for name in font_names),
                  f"font is missing: {face}")

        for phrase in ("Samuel Murillo - Computer Engineer", "ABILITIES AND KNOWLEDGES",
                       "EXPERIENCE", "EDUCATION",
                       "Computer Engineering - Universidad José Antonio Páez (Venezuela)"):
            check(phrase in text, f"text extraction lost {phrase!r}")
        check(text.count("✓") == 12, f"expected 12 checklist items, got {text.count('✓')}")

        links = {link.get("uri") for page in doc for link in page.get_links()}
        for uri in ("mailto:contact@samuelmurillo.xyz", "https://samuelmurillo.xyz/",
                    "http://github.com/samuelm333",
                    "https://www.linkedin.com/in/samuel-murillo"):
            check(uri in links, f"missing or changed link {uri}")

        # The page break follows the Google Docs original.
        check(lines(doc[0])[-1] == "and Heroku using Terraform, CircleCI and Datadog.",
              f"page 1 ends with {lines(doc[0])[-1]!r}")
        check(lines(doc[1])[0].startswith("Senior Software Developer"),
              f"page 2 starts with {lines(doc[1])[0]!r}")

        log = PDF.with_suffix(".log").read_text()
        for pattern in (r"Missing character:", r"LaTeX Font Warning:",
                        r"Package fontspec Warning:", r"Overfull \\[hv]box"):
            check(not re.search(pattern, log), f"{pattern} in compiler log")
        report = {"pages": doc.page_count, "fonts": sorted(font_names),
                  "box_warnings": re.findall(r"Underfull \\[hv]box[^\n]*", log)}
except (OSError, RuntimeError, ValueError, IndexError) as error:
    failures.append(str(error))

(OUTPUT / "report.json").write_text(
    json.dumps({"cv": report, "failures": failures}, indent=2) + "\n")
for failure in failures:
    print(f"FAIL: {failure}", file=sys.stderr)
print(f"Checked {PDF}; {len(failures)} failures. See {OUTPUT}.")
sys.exit(bool(failures))
