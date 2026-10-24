#!/bin/zsh
# Builds main.pdf from main.tex in a temporary directory (pdflatex + bibtex), copies it here and reports warnings.
# TeX: TinyTeX in ~/Library/TinyTeX (packages: acmart and its dependencies, newunicodechar, booktabs, upquote, caption).
set -e
export PATH=~/Library/TinyTeX/bin/universal-darwin:$PATH
HERE=${0:A:h}
BUILD=$(mktemp -d)
mkdir -p $BUILD/tex
cp $HERE/main.tex $HERE/references.bib $BUILD/tex/
cp $HERE/../fig_integrity_matrix.pdf $BUILD/
cd $BUILD/tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null || { grep -A3 "^!" main.log; exit 1; }
bibtex main | grep -i "warning" || true
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
grep -i "undefined\|Missing character" main.log || true
echo "overfull boxes: $(grep -c Overfull main.log || true)"
grep "Output written" main.log
cp main.pdf $HERE/main.pdf
rm -rf $BUILD
