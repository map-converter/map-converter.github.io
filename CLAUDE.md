# Map Converter website

This repository is public and builds https://map-converter.github.io: the Converter (yEd GraphML, CellDesigner and
SBGN-ML, both ways), its description, architecture and documentation pages, and a copy of Newt. Moved here from the
Metabolism Regulation website on 2026-11-08 (user); The addresses keep their
`/converter/...` paths, so links and the documentation's own links work unchanged; `/` leads to `/converter/`.

Names: this repository is public and names no private repository, in files, pages, code comments or commit messages.
"The converter's repository" is the converter's private source.

- `converter/mapconv/` is a copy of the converter's code, with its commit in `VERSION`, written by the converter
  repository's `tools/to_website.sh`, and so are `pages/converter-docs/` and `_data/converter_docs.yml`. Change them
  there, never here.
- `converter/cdrender.py` is a copy of the CellDesigner renderer of the Metabolism Regulation website (its CD viewer
  uses it too); a change there is copied here.
- `newt/` is a copy of Newt (iVis-at-Bilkent/newt, LGPL-3.0) with one script of ours, `newt/open.js`, opened by the
  Converter's Newt buttons (`_includes/newt-open.js`).
- Logo beside the name: `images/logo-converter/logo.svg`, the tab icon reversed for the white page, in the grey of the
  Converter's tick boxes, #626262 (arrows and edge on white; 2026-11-08, in place of the slate one: the page is grey); the tab icon stays in `images/favicon-converter/`.
- Hidden: the pages carry `noindex` and are linked from nowhere public. Layout, styles and `meta.html` are copies from
  the Metabolism Regulation website (2026-11-08).
- A change counts only when it is live, checked on the site itself.
