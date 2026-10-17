"""Relabel Figures 1 and 3 in place.

The diagrams.net source of Figure 3 in the old paper repository predates the
published figure, so these labels are changed in the PDFs themselves. Only
the old text is removed; drawings stay untouched. The new text uses Arial
glyphs embedded in the figures, at the old baseline and size, keeping each
label's center (or left edge, for the Figure 3 code header that lines up
with the one above it).

Usage: python figures/scripts/relabel_diagrams.py
"""
from pathlib import Path

import fitz

FIG = Path(__file__).resolve().parent.parent
PIPELINE = FIG / 'sec-2-ebpf-pipeline-fig.pdf'
JIT_DUMP = FIG / 'sec-3-jit-dump-fig.pdf'
# (figure, old label, new label, keep 'center' or 'left')
EDITS = [
    (PIPELINE, 'User Space', 'Userspace', 'center'),
    (PIPELINE, 'clang', 'Clang', 'center'),
    (JIT_DUMP, 'x86-64 (Under Optimized)', 'x86-64 (Underoptimized)', 'left'),
    (JIT_DUMP, 'clang', 'Clang', 'center'),
]


def embedded_fonts(doc):
    fonts = {}
    for xref, _, _, base, *_ in doc[0].get_fonts(full=True):
        fonts[base.split('+')[-1]] = fitz.Font(fontbuffer=doc.extract_font(xref)[3])
    return fonts


def main():
    # Figure 3 embeds no regular capital C, so glyphs come from the same
    # Arial subset of Figure 1 when a figure's own subset lacks one.
    shared = embedded_fonts(fitz.open(PIPELINE))
    for path in (PIPELINE, JIT_DUMP):
        doc = fitz.open(path)
        page = doc[0]
        own = embedded_fonts(doc)
        spans = [s for b in page.get_text('dict')['blocks'] for line in b.get('lines', [])
                 for s in line['spans']]
        writes = []
        for fig, old, new, keep in EDITS:
            if fig != path:
                continue
            span = next((s for s in spans if s['text'] == old), None)
            if span is None:
                print(f'{path.name}: "{old}" not found, skipped')
                continue
            name = span['font']
            font = own[name] if all(own[name].has_glyph(ord(c)) for c in new) else shared[name]
            size, (x, y) = span['size'], span['origin']
            if keep == 'center':
                x += (font.text_length(old, size) - font.text_length(new, size)) / 2
            page.add_redact_annot(fitz.Rect(span['bbox']), fill=False)
            writes.append(((x, y), new, font, size))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_REMOVE)
        for point, text, font, size in writes:
            writer = fitz.TextWriter(page.rect)
            writer.append(point, text, font=font, fontsize=size)
            writer.write_text(page, color=(0, 0, 0))
            print(f'{path.name}: wrote "{text}" at ({point[0]:.2f}, {point[1]:.2f}), {size:.2f} pt')
        if writes:
            tmp = path.with_suffix('.tmp.pdf')
            doc.save(tmp, garbage=3, deflate=True)
            doc.close()
            tmp.replace(path)


if __name__ == '__main__':
    main()
