---
layout: converter-docs
title: "Converter documentation"
permalink: /converter/docs/
sitemap: false
noindex: true
---
{% raw %}

The converter translates molecular interaction maps between three formats: yEd GraphML drawn in the
SBGN palette, CellDesigner 4.x and SBGN-ML (Process Description, also Newt files). It keeps the
drawing of the input map, the biology it states (entities, reactions, annotation) and says in its
messages what it changed or left out. It runs in the browser on the
[Converter page](/converter/), and the files never leave the computer.

| Input | Outputs |
|---|---|
| yEd GraphML | CellDesigner in two layouts, SBGN-ML (plain and for Newt) |
| CellDesigner | GraphML in two layouts, SBGN-ML (plain and for Newt) |
| SBGN-ML, Newt | GraphML, CellDesigner in two layouts |

Two layouts: advanced, the drawing of the input map kept, is the recommended file. Straight line, every
arc straight from centre to centre, is a fallback for laying out by hand. SBGN-ML has one layout, the drawing of the
input map kept; the file for Newt is adjusted so that Newt keeps it as drawn.

## This documentation

- **Start**: [Convert a first map](/converter/docs/start/), a walk through the Converter page.
- **How-to guides**: [short recipes](/converter/docs/howto/) for one task each (a round trip through
  CellDesigner, opening a map in Newt, harmonising node sizes, a map the check marks red).
- **Reference**: what each input gives ([Inputs and outputs](/converter/description/)), what the
  [messages](/converter/docs/messages/) under a map mean, and the conventions of each format, as
  learnt from files saved by the programs themselves.
- **Explanation**: how the converter is built ([Architecture](/converter/architecture/)).

The pages under Reference say each convention as the programs' own saved files show it.

{% endraw %}
