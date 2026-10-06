#!/usr/bin/env bash
# Build main.pdf into build/. Usage: ./build.sh [clean]
set -euo pipefail
cd "$(dirname "$0")"

# MiKTeX installs per user and may not be on PATH in Git Bash.
if ! command -v latexmk >/dev/null 2>&1; then
	for d in "${LOCALAPPDATA:-}/Programs/MiKTeX/miktex/bin/x64" "/c/Program Files/MiKTeX/miktex/bin/x64"; do
		[ -x "$d/latexmk" ] || [ -x "$d/latexmk.exe" ] && PATH="$d:$PATH" && break
	done
fi

if [ "${1:-}" = clean ]; then
	rm -rf build
	exit 0
fi

# bibtex runs inside build/, so point it back at reference.bib.
if command -v cygpath >/dev/null 2>&1; then
	export BIBINPUTS="$(cygpath -w "$PWD");${BIBINPUTS:-}"
else
	export BIBINPUTS="$PWD:${BIBINPUTS:-}"
fi
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
grep -E '^LaTeX Warning: (Citation|Reference).*undefined|Float too large' build/main.log || true
echo "PDF: build/main.pdf"
