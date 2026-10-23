"""Builds main.tex (ACM acmart, TELO) from ../manuscript.md with pandoc.

Usage: python research/paper_integrity_audit/tex/build_tex.py
Compile on Overleaf (or with a TeX distribution): main.tex + references.bib + ../fig_integrity_matrix.pdf.
"""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "manuscript.md")

# author-year text -> natbib command; whitespace inside the patterns matches line breaks of the Markdown source
CITATIONS = [
    (r"\(Hansen et al\.\s+2021\)", r"\\citep{Hansen_2020}"),
    (r"\(de Nobel et\s+al\.\s+2024\)", r"\\citep{de_Nobel_2024}"),
    (r"\(Hansen et al\.\s+2011\)", r"\\citep{Hansen_2011}"),
    (r"\(Gyori et al\.\s+2016\)", r"\\citep{Gyori_2016}"),
    (r"Gruber et al\.\s+\(2021\)", r"\\citet{Gruber_2021}"),
    (r"Kudela\s+\(2022\)", r"\\citet{Kudela_2022}"),
    (r"\(Vermetten et al\.\s+2022\)", r"\\citep{Vermetten_2022}"),
    (r"Ravber et al\.\s+\(2025\)", r"\\citet{Ravber_2025}"),
    (r"\(Ravber et al\.\s+2025\)", r"\\citep{Ravber_2025}"),
    (r"\(Rounds and Kanewala\s+2018\)", r"\\citep{Rounds2018}"),
    (r"\(Duque-Torres et al\.\s+2025a,\s+2025b\)", r"\\citep{Duque_Torres_2025a,Duque_Torres_2025b}"),
]

PREAMBLE = r"""\documentclass[acmsmall,screen,review,anonymous=false]{acmart}
\citestyle{acmauthoryear}
\acmJournal{TELO}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{calc}
\usepackage{array}
\usepackage{newunicodechar}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\pandocbounded}[1]{#1}
%(unicode)s
\begin{document}
\title{%(title)s}
\author{Danijel Jovanovi\'{c}}
\affiliation{\institution{University of Novi Sad, Faculty of Technical Sciences}\city{Novi Sad}\country{Serbia}}
\email{danijel.jovanovic@uns.ac.rs}
\begin{abstract}
%(abstract)s
\end{abstract}
\maketitle
"""

POSTAMBLE = r"""
\bibliographystyle{ACM-Reference-Format}
\bibliography{references}
\end{document}
"""


def pandoc(markdown):
    return subprocess.run(["pandoc", "-f", "markdown+raw_tex", "-t", "latex", "--wrap=preserve"],
                          input=markdown, capture_output=True, text=True, check=True).stdout


# non-ASCII characters of the manuscript, for pdfLaTeX
UNICODE = {"−": r"\ensuremath{-}", "≤": r"\ensuremath{\le}", "≥": r"\ensuremath{\ge}", "×": r"\ensuremath{\times}",
           "∈": r"\ensuremath{\in}", "Σ": r"\ensuremath{\Sigma}", "⌊": r"\ensuremath{\lfloor}", "⌋": r"\ensuremath{\rfloor}",
           "→": r"\ensuremath{\to}", "′": r"\ensuremath{'}", "…": r"\ldots{}", "–": "--", "—": "---", "≠": r"\ensuremath{\neq}",
           "≈": r"\ensuremath{\approx}", "·": r"\ensuremath{\cdot}", "⁻": r"\ensuremath{^{-}}", "¹": r"\ensuremath{^{1}}",
           "²": r"\ensuremath{^{2}}", "μ": r"\ensuremath{\mu}", "λ": r"\ensuremath{\lambda}", "ε": r"\ensuremath{\varepsilon}"}


def blank_line_before_lists(text):
    """Pandoc Markdown needs a blank line before a list that follows a paragraph line."""
    out, previous = [], ""
    for line in text.splitlines():
        if re.match(r"^\s*(- |\d+\. )", line) and previous.strip() and not re.match(r"^\s*(- |\d+\. )", previous) \
                and not previous.startswith("  ") and not previous.startswith("|"):
            out.append("")
        out.append(line)
        previous = line
    return "\n".join(out) + "\n"


def main():
    text = open(SOURCE, encoding="utf-8").read()
    text = blank_line_before_lists(text)
    # one figure float with its caption (pandoc implicit_figures)
    text = re.sub(r"!\[Figure 1\]\(fig_integrity_matrix\.png\)\n\n\*\*Figure 1\.\*\* ((?:.+\n)+?)\n",
                  lambda m: "![" + " ".join(m.group(1).split()) + "](fig_integrity_matrix.png)\n\n", text)
    unknown = sorted({ch for ch in text if ord(ch) > 127} - set(UNICODE) - set("ćčšžđĆČŠŽĐéöüäŭß"))
    assert not unknown, f"unmapped characters: {unknown}"
    for pattern, replacement in CITATIONS:
        text, n = re.subn(pattern, replacement, text)
        assert n, f"citation not found: {pattern}"
    title = text.splitlines()[0].lstrip("# ").strip()
    abstract = text[text.index("## Abstract") + len("## Abstract"):text.index("## 1. Introduction")].strip()
    body = text[text.index("## 1. Introduction"):text.index("## References")]
    appendix = text[text.index("## Appendix A"):text.index("## References")] if "## Appendix A" in text else ""
    if appendix:
        body = body.replace(appendix, "")
    body = body.replace("](fig_integrity_matrix.png)", "](../fig_integrity_matrix.pdf)")
    # section numbers come from LaTeX, not from the Markdown headings
    body = re.sub(r"^(#+) \d+(\.\d+)*\.? ", r"\1 ", body, flags=re.M)
    unicode = "\n".join(f"\\newunicodechar{{{ch}}}{{{cmd}}}" for ch, cmd in UNICODE.items())
    tex = PREAMBLE % dict(title=pandoc(title).strip(), abstract=pandoc(abstract).strip(), unicode=unicode)
    tex += pandoc(("\n" + body).replace("\n## ", "\n# ").replace("\n### ", "\n## "))
    if appendix:
        appendix = re.sub(r"^## Appendix A\. ", "# ", appendix, flags=re.M)
        tex += "\n\\appendix\n" + pandoc(appendix)
    tex += POSTAMBLE
    open(os.path.join(HERE, "main.tex"), "w", encoding="utf-8").write(tex)
    print(f"main.tex: {len(tex)} characters")


if __name__ == "__main__":
    main()
