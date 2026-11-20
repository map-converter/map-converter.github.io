---
layout: converter-docs
title: "SBML with Layout"
permalink: /converter/docs/sbml/
sitemap: false
noindex: true
---
{% raw %}

`mapconv/sbml.read` reads an SBML file that has a layout (the Layout package of Level 3, or the same elements in a
Level 2 annotation) into the map model, drawn where the file places it. Nothing is moved or laid out on the way.

- Compartment glyphs: compartments, named by their text glyph or the compartment's name.
- Species glyphs: the glyph from the species' SBO term (`SPECIES` in the reader): protein and Reactome's sets
  macromolecule, complex, simple chemical, nucleic acid feature (mRNA and gene with their unit of information), empty
  set, phenotype; no term, an unspecified entity. A species drawn more than once keeps one node per glyph.
- A species glyph lying inside a complex glyph's box is its member; inside a compartment glyph, the smallest one
  holding its centre is its compartment.
- Reaction glyphs: a process at the middle of the reaction's curve, else at its box's centre; omitted and uncertain
  process, association and dissociation from the reaction's SBO term.
- Species reference glyphs: arcs. The role from the glyph, else from its species reference, else from the reaction's
  reference to the species its glyph draws (a species in two roles of one reaction: its glyphs take the references in
  their order). A modifier's head from its SBO term (catalysis 13, inhibition 20, stimulation 459, necessary
  stimulation 461, modulation 594), the generic modifier term 19 giving way to the glyph's role (activator,
  inhibitor). The specification asks (a "should", Layout §3.10.1) that modifier curves start at the species and other curves at the process, and files do not always follow it: each is read from the end nearer its species glyph,
  and its inner points are the arc's bend points. Bezier control points are not kept.
- A species glyph may name its species by id or by metaid; one naming no species of the model is drawn as an
  unspecified entity and said.
- Labels: the text glyph's text, else the name of the element it shows. MIRIAM identifiers (is, hasVersion) as node
  properties.
- Sources and sinks: a species glyph that names no species and has no text (COPASI writes such a glyph, 1 by 1, with
  the text "unset", for a reaction's source or sink) is a source or sink, drawn as a circle round its centre, 20 px at
  least. "unset" is never taken as a label.
- A species given as a point (a position with no dimensions, as MonaLisa writes Petri net places) is drawn 60 by 30
  round it. A reaction glyph with no place (a box of 0 by 0 at 0, 0, no curve) is drawn amid the glyphs it joins, and
  said. A reaction glyph with no species reference glyphs gets its reaction's reactants, products and modifiers as
  straight lines to the first glyph of each species.
- SBML-qual: a qualitative species' box (a general glyph naming it, as CaSQ and bioLQM write them, or a species glyph,
  as Path2Models writes them) is an Activity Flow activity, drawn as sbgnml.read draws one (a macromolecule with the
  SBGN class biological activity). Each transition gives an influence from each input to each output, straight: a
  positive input a stimulation, a negative one an inhibition, otherwise a modulation; an input without a sign takes it
  from the function terms (compared with 0, or below 1, negative; with 1 or more, positive), and a transition that
  lists no inputs takes them from its function terms. A qualitative species without a box is left out and said.
- Left out and said: layouts after the first, general glyphs other than SBML-qual boxes (MINERVA's modifications), reactions
  without a glyph, glyphs without a box. A file without a layout, or without species glyphs, is refused.
- Render: each glyph's style by its id, else by its glyph type (typeList), the layout's own styles over the global
  ones: a species' or compartment's fill, a compartment's outline colour and width, a line's colour, a label's font
  size from its text glyph's style. Black outlines and lines are the default and not kept. Gradients and the shapes
  Render draws (polygons, curves) are not read: the glyph is drawn by its kind.

## Writing

`mapconv/sbml.write` writes a map read from GraphML, CellDesigner or SBGN-ML as SBML Level 3 Version 1 with the
Layout and Render packages (the button SBML on the Converter page, or `python3 -m mapconv <map> <out.sbml>`). The drawing
is the map's SBGN-ML drawing, glyph for glyph (boxes, process ports, line ends and bends), so the SBML and the SBGN-ML
of one map look the same. The meaning is the map's biology, as the other formats take it.

- Compartments: one per compartment name. Entities outside any compartment are in a compartment `default`, which has
  no glyph.
- Species: one per entity (glyphs that draw one entity are glyphs of one species). Each source or sink is a species of its
  own, as SBGN never clones the empty set. The SBO term gives the glyph kind, the same terms the reader takes back:
  macromolecule 245, complex 253, simple chemical 247, nucleic acid feature 354 (a gene 243, an mRNA 278), unspecified
  entity 285, phenotype 358, source and sink 291 (boundary condition true). MIRIAM identifiers as RDF, `bqbiol:is`, or
  `bqbiol:hasVersion` for a family's members, with identifiers.org links.
- What SBML core has no place for goes into the species' notes, one line each, and is said: state variables, units of
  information other than gene and mRNA, the multimer count, a hypothetical entity. Two forms of one protein that differ
  only by a state are two species of the same name, told apart by their notes.
- Reactions: one per process glyph, its SBO term by the process (process 375, omitted 397, uncertain 396, association
  177, dissociation 180). Consumed entities are reactants, produced ones products. A process with no consumption is
  reversible: the products at its first port are written as reactants. Modifiers by their SBO term: catalysis 13,
  inhibition 20, stimulation 459, necessary stimulation 461, modulation 594.
- A logic gate on a process: each input of the gate is a modifier of the process, with the SBO term of the gate's arc
  (SBML core has no gate). Gates feeding gates are followed down to their entities. An input of a NOT gate takes the
  opposite sign: NOT A stimulating a process writes A as its inhibitor. The gate is drawn (a general glyph with its box
  and name) and each input's line runs on through the gate, or gates, to the process. Said under the map.
- Arcs into an entity (no process between, with or without a gate) are drawn as general glyphs, each naming its source
  species and drawing a line to its target, and have no meaning in SBML core. Said. Equivalence arcs and operators are
  left out and said.
- A process with no reactant or product is left out and said.
- Layout: a compartment glyph per compartment glyph, a species glyph per entity glyph, a reaction glyph per process
  (a line between its two ports), a species reference glyph per arc, its curve the arc's points, from the process to
  the species for reactants and products and from the species to the process for modifiers (Layout 3.10.1). A text
  glyph per name, a compartment's name in a strip along its top.
- Render: every glyph that draws a box has a style (its fill, outline colour and width, a shape by its kind: rounded
  rectangle, rectangle or ellipse), every line a style with its colour and its SBGN head as a line ending (production,
  stimulation, catalysis, inhibition, necessary stimulation, modulation), every name a style with its font size. Render
  fixes no defaults, so every attribute is written.
- Checked: every reference map writes SBML that libSBML reads without an error, Layout and Render included;
  SBMLNetwork draws them. Read back, each CellDesigner reference map keeps its entities and reactions within the limits
  above (tests/test_sbml_write.py).

{% endraw %}
