---
layout: converter-docs
title: "Changes"
permalink: /converter/docs/changes/
sitemap: false
noindex: true
---
{% raw %}

What changed for people who use the converter, newest first, by the date it went to the Converter page.
Changes inside the code that leave every file the same are listed only when they change how the converter works.


## 2026-11-21

- Activity Flow maps keep their submaps and terminals: a file saying `language="activity flow"` drew a submap as a
  phenotype and dropped its terminals; now it is read as Process Description maps are, the equivalence arcs to the
  terminals kept, also when converting to SBGN-ML Process Description.
- CellDesigner files keep submaps and perturbing agents: CellDesigner draws both as a phenotype, and the species now
  carries the line `SBGN class: submap` (or `perturbing agent`) in its notes, so converting back to SBGN-ML gives the
  submap or perturbing agent again with all its arcs. A phenotype without that line stays a phenotype, arcs in and out
  kept.
- GraphML: a submap is drawn as yEd's Submap and read back as a submap, with or without terminals, its arcs kept
  (before: a Submap without terminals became a phenotype). Changed to the Phenotype in yEd, it is a phenotype again.
  SREBP's "Transcription of target genes" and "Cholesterol biosynthesis" are submaps in SBGN-ML now.

- CellDesigner files keep the sites: every site of a species (its state variables' P@S1177 and the property PTM)
  goes into the species' notes as one line, `PTM: P@S1177 Pa@C26`, which CellDesigner keeps on saving and does not draw;
  read back into the property PTM (GraphML) and onto the state variables' sites (SBGN-ML). The residues still carry no
  name, as CellDesigner would draw it over the species' name.

- CellDesigner to GraphML and SBGN-ML: a reversible reaction's reactant line, drawn out of the process, now keeps its bend
  points in order from the process; they were reversed, so the line doubled back and crossed the map (ReconMap 2: 287 of
  its 1,948 reversible reactions have two or more bends there, GULN3D among them).
A CellDesigner reaction with only a metaid (no id, which SBML requires) is read by its metaid: VMH's ReconMap 2
failed whole on one such reaction (re227) and now converts to GraphML (22,707 nodes).

- SBGN-ML keeps a map's sites and references: a site from the property PTM on its state variable (`variable`),
  the sites no circle shows in the glyph's note `PTM:`, a process's references as `bqmodel:isDescribedBy`; both read back.

- A cardinality's place along its line is kept: SBGN-ML's cardinality bbox is read as a place on the line and written
  there again; a yEd label keeps it as ratio and side. Converter-written SBGN-ML boxes now sit on the line as written
  (iNOS, eNOS, phosphoinositides, TAG, estrogen: the cardinality boxes moved by a few px).
- Cardinality (the number on a consumption or production line) is kept in every format: a number label on a yEd
  line, SBGN-ML's cardinality glyph and CellDesigner's stoichiometry, each read and written; only where one is set. SBML core's stoichiometry takes the number too.
- SBGN-ML read: colours in the render extension's earlier namespace (libSBGN's 0.2 examples) are read, and a gradient
  fill is read as the colour halfway between its first and last stops (it was drawn white).
- SBML-qual: an Activity Flow map (SBGN-ML, Newt, GraphML) also gives SBML-qual, its Boolean model with its drawing
  (lines, bends and gates in Layout), button SBML-qual; `--qual` on the command line (docs/SBML.md, SBML-qual).

- Units of information keep the place their file gives them (SBGN-ML, GraphML), in place of being spread along the top; a
  unit with no place, or at its default slot, is spread along the top as before. CellDesigner keeps its one unit at the
  top (its angle for another side is not known yet), said in the messages when the file had it elsewhere.
- SBGN-ML read: a new id for a glyph whose id another glyph has is never one of the map's port or arc ids.
- SBGN-ML read: two glyphs with the same id are both kept, the later under <id>_2, and each arc naming the id goes
  to the glyph its end meets (the PD 2.1 specification's muscle example draws its myosin and ATP association again).
- SBGN-ML read: a file with an XML comment among a glyph's children (libSBGN's adh, clone-marker, edgerouting,
  reversible-verticalpn test files) is read; it stopped with an error before.
- SBGN-ML read: an arc keeps its width from the render extension (the stroke-width of a style naming the arc), drawn in
  GraphML and written back to SBGN-ML, so GraphML made from Newt's files has its 1.25 px lines
 .

## 2026-11-20

- CellDesigner read: every species shows every residue of its protein, empty where it sets no state, as CellDesigner
  draws them; protein entries of one name and type (files of other tools) count as one protein. SBGN-ML and GraphML
  made from CellDesigner files gain the state variables they lacked
 .
- SBML: every input (GraphML, CellDesigner, SBGN-ML, Newt) also gives SBML Level 3 with Layout and Render, drawn as
  its SBGN-ML file, button SBML, tick box → SBML on the page; `python3 -m mapconv <map> <out.sbml>`. State variables,
  multimer counts and other details SBML core cannot hold go into the species' notes; logic gates are drawn, their
  inputs written as modifiers (docs/SBML.md, Writing).

- CellDesigner: a line's end off a species' centre goes to the nearest of its 16 places; no edit point is added just
  outside a node to hold the input's port any more (as drawn: a level line into a larger node; modifiers leaving off the
  centre at the process glyph's height). A bend next to that end moves into line with the place. The messages list
  places shared by several lines and line ends moved more than 5 px. In the advanced file a node moved so a level
  line into a larger node stays level is moved in line with the place that line meets, not that node's centre.

## 2026-11-18

- SBGN-ML: one file drawn as the input map, "SBGN-ML" (`<map>.sbgn`, the blue button), and one for Newt (`<map>-newt.sbgn`,
  newt-adjusted); the straight SBGN-ML files are gone (four buttons were two). Logic gate arcs keep their bends; a bend at or
  behind a process's or gate's antenna tip joins the antenna; an arc leaving a phenotype is kept with a warning; arcs
  meeting a process from the side are listed in one message.

- CellDesigner written as CellDesigner 4.4.2 saves it in three more places, so a file opened and saved there comes back
  unchanged: the identifiers in a complex member's notes one element per line (they were on one line after the
  family's name), a species' notes text ending with a line break, and a species' catalysed reactions in the order the
  reactions are written. What the files hold is the same (108 reference and test files changed by line breaks and that
  order only).

## 2026-11-16

- SBGN-ML read: an arc keeps its colour from the render extension (a style naming the arc), drawn in GraphML and
  written back to SBGN-ML, so GraphML made from Newt's files has their grey lines
 .
- GraphML written: a compartment's name low in its compartment is placed at the bottom (left, middle or right) and no
  longer centred because of its distance from the top; its height unchanged.

## 2026-11-15

- SBGN-ML read (Activity Flow): a biological activity's GraphML node keeps its class and its unit of information's entity
  as the node properties "SBGN class" and "SBGN unit", so the viewer's editor saves an Activity Flow map as Activity
  Flow; the drawing is unchanged.
- SBGN-ML read (Activity Flow): a perturbation is drawn, as yEd's perturbing agent, and keeps its class back to SBGN-ML;
  it was left out before.

## 2026-11-14

- GraphML: an unspecified entity's name at 14 as every other glyph's (its template had 12, in a box sized for 14).
- A unit of information is at least as wide as N:2 (25 by 16 in GraphML, 21 wide in SBGN-ML), so an empty one is a box
  to type into, not a sliver; units of three characters or more as before.
- SBGN-ML read: every glyph keeps its outline colour and width from the file, not only compartments, so GraphML made
  from Newt's files has their grey outlines.
- SBGN-ML (advanced) keeps every bend of the map, not only the key ones; the files for Newt and the straight ones as
  before. Compartments keep their outline width.
- SBGN-ML read: an arc starts and ends where the file says (a point on a glyph's side stays there), compartments keep
  their outline width, and a compartment's name stays at the left, middle or right of its top as in the file. So a
  GraphML or CellDesigner file made from SBGN-ML draws the file's own arc ends.
- SBGN-ML: association, dissociation and perturbing agent keep their class through GraphML (the node property "SBGN
  class"; a perturbing agent as yEd's own glyph) and back to SBGN-ML, so they can be drawn as themselves.
- SBGN-ML read (Process Description): an equivalence arc between two glyphs that are drawn (an entity and a submap)
  is a plain line, as in Activity Flow; one to a tag or a submap terminal is still left out with them.
- SBGN-ML read: glyphs drawn inside a glyph that holds no members in SBGN (a submap used as a frame, as in the spec's
  layout example) are read beside it; before, the file could not be converted.

## 2026-11-10

- CellDesigner files: a line leaving a metabolite keeps its first bend level with where it leaves the circle (no
  small jog); the two bend points that hold a process glyph where yEd has it never fall inside the reaction's own
  species (a line no longer runs through a complex); a modifier arc with bends ends on the side of the process
  glyph it arrives from, so its arrowhead shows (a protein catalysing its own step).
- CellDesigner files: in the notes of a protein inside a complex, every line (a family's name, a member's sites)
  now ends with a line break, so CellDesigner keeps it when the file is saved. Before, it dropped the last line,
  the one written right against the identifiers ("Family: PKA regulatory subunits"). The identifiers were never lost.

## 2026-10-29

- A node property "Unit of information" (one per line) for units the drawing does not show: two forms of one
  protein with one identifier (cleavage fragments) stay two species, and the units go into CellDesigner's notes on
  one line, read back from there.
  No reference file changed.

## 2026-10-28

- Compartment colours as CellDesigner draws them:
  from CellDesigner the outline takes the compartment's colour and the fill the light band CellDesigner shows (a
  quarter of the colour over white), where before the whole box had the colour, the dark one of its lines; to
  CellDesigner the colour is chosen so that its band shows the yEd fill. Newt and SBGN-ML compartments keep their
  outline colour. Reference files: every file with a compartment.
- Font sizes kept on every conversion: names,
  state variables and units at the input map's sizes (CellDesigner, yEd, SBGN-ML and Newt), where before the map
  got one size (CellDesigner files 12, GraphML 14 or the glyph's template). The tick box is now **standard node
  and font sizes**: its GraphML has names 14, state variables and units 10. Reference files: every CellDesigner
  file from GraphML (14), GraphML from CellDesigner and Newt, SBGN-ML (font sizes in the render styles).
- CellDesigner to GraphML: an unknown species has no outline, as CellDesigner draws it, and a transparent colour
  (six digits, or alpha 00) gives no fill; before, a black outline and an invalid colour (`#FFFF`), so name tags
  drawn as bare text in CellDesigner came out as boxes. No reference file changed.
- CellDesigner to GraphML and SBGN-ML: bends within 3 px of one line are aligned on it (lanes of arcs, segments
  meant level), and GraphML made from CellDesigner or Newt has sharp bends, as those programs draw them
 . Lines at a
  phenotype attach to its hexagon, where CellDesigner draws them, not to its box corners (both ways). Reference
  files: every GraphML from CellDesigner, SBGN-ML or Newt (sharp bends), and bends under 3 px in the GraphML and
  SBGN-ML from the Atlas CellDesigner files, PD02 eicosanoids and the PD map's autophagy and histamine submaps.
- CellDesigner to GraphML: an arc between two entities (reduced notation, influences) keeps its CellDesigner
  drawing: its ends at the connection points, its bends where CellDesigner shows them. Before, the bends were
  read from the node centres and came out shifted, so lines drawn level in CellDesigner came out slanted.
  Reference files: the PD map's autophagy and histamine submaps (GraphML and SBGN-ML).
- CellDesigner to GraphML: identifiers the GraphML has no property for (MINERVA's Ensembl, NCBI Gene, RefSeq, InChI,
  STITCH; GO, PubChem) are named in the messages, per database with the number of species; before, they went
  without a word. Empty layers (CellDesigner's default two) are no longer reported as left out.
- GraphML: a compartment or complex folded in yEd shows its own name; before, the template's (CYTOSOL, LABEL).
  Reference files: every GraphML with a compartment or complex (the folded name only), and the messages of
  PD02 eicosanoids and the PD map's autophagy and histamine submaps.

## 2026-10-27

- References on reactions (PubMed, DOI, PMC, Reactome): CellDesigner to GraphML puts them on the process glyph as
  the node property References (`pubmed:27260166 doi:10.1016/...`), GraphML to CellDesigner writes that property
  as `bqmodel:isDescribedBy`, one bag per reference, as MINERVA maps hold them. Before, they were left out. A
  reaction drawn as an arc keeps none, said in the messages. Reference files: the GraphML of the PD map's
  autophagy and histamine submaps and their messages.

## 2026-10-26

- Logic gates with more than two inputs: a CellDesigner test file (an OR of five), read and written on every route;
  no file changed. In CellDesigner every gate, NOT included, is drawn from two inputs, more added with the
  add-reactant tool (checked in CellDesigner). A NOT with one input, as SBGN draws it, goes to CellDesigner as written:
  CellDesigner opens and saves it (a second test file, saved by CellDesigner); no file changed.

## 2026-10-25

- Every GraphML file (from CellDesigner, SBGN-ML and Newt, corrected, standard sizes): a complex's name at the bottom
  inside it, as in CellDesigner; before, at the top. Reference files: every GraphML with a named complex (75 files).
  Where the name touches the lowest member (from SBGN-ML and Newt) the complex is left as drawn; the layout skill's
  complex packing gives it room.
- CellDesigner's unknown logic gate (the question mark) is a logic operator labelled ? in the GraphML (was UNKNOWN)
  and goes back to CellDesigner as the same gate; before, it was left out there. GraphML and SBGN-ML to CellDesigner:
  an equivalence operator becomes the unknown gate, its line to the generic entity a dashed stimulation; before, it
  was left out. Reference files: the test map of an equivalence operator (its CellDesigner files gain the gate).
- CellDesigner to GraphML and SBGN-ML: a logic gate (AND, OR, NOT) on a reaction's modifiers, as CellDesigner saves
  it with bends, sits where CellDesigner draws it; before, it was placed at the map's top left corner, its lines
  drawn across the whole map. The line from the gate to the process and the lines from its inputs keep their bends
  and connection points. Official files: histamine signalling (PD map), its AND gate (the map no longer reaches
  out to that corner, so every coordinate of its SBGN-ML moves by the same amount).
- CellDesigner to GraphML and SBGN-ML: a species annotated in another order than the Atlas files (MINERVA lists
  RefSeq or Entrez first) keeps its HGNC ID, HGNC symbol and UniProt; before, only the identifiers before the
  first HGNC symbol were read. Official files: PD02 Eicosanoids (AsthmaMap) gains 64 HGNC symbols and 17 HGNC IDs,
  histamine signalling (PD map) one HGNC symbol; nothing else changed.
- Converter page: the three routes are tick boxes, all ticked at first. Only the files of the ticked routes are
  made (a large CellDesigner map gives its GraphML files without waiting for SBGN-ML). A file no ticked route
  takes says in red which box to tick. The tick boxes are together on the right, the note on the buttons under
  the drop area.
- Converter page: ticking a box makes only the files the maps on the page do not have yet; unticking one hides
  its buttons. The browser keeps the tick boxes as last left.
- Converter page: "straight line" on the buttons and the tick box reads "straight". Files and their names unchanged.
- Converter page: an ⓘ after "Additional CellDesigner layouts" and "Options" opens what each box gives, on a phone too.
  "Standard node sizes" reads "standard node sizes", like the other boxes.
- SBGN-ML written about three times faster on large maps (the test for nodes a straightened line would cross).
  Every file the same.

## 2026-10-24

- Converter page: the SBGN-ML button made for Newt reads "newt-adjusted" under SBGN-ML (was "Newt"), so it is not
  taken for the Open in Newt button. Files and their names unchanged.
- Converter page: ticking or unticking a CellDesigner layout or Standard node sizes converts the maps
  already on the page again, so their buttons follow the boxes without dropping the maps again.
- Converter page: the three CellDesigner fallbacks (straight line, straight & bends, as drawn) are made only
  when ticked under "Additional CellDesigner layouts". CellDesigner (advanced) and the SBGN-ML files are always made.
- Four CellDesigner files:
  CellDesigner (advanced, the small moves that straighten lines, as before this day), straight line,
  straight & bends (the input's key bends, no node moved) and as drawn (process glyphs and ports held by
  edit points, for round trips between editors). Only advanced moves nodes.
- CellDesigner to GraphML and SBGN-ML: a line attached to a multimer ends on its front shape, as
  CellDesigner draws it (5 official maps changed: glycolysis cardiac, mevalonate, glycogen liver and muscle, BCAA);
  a bend at most 3.5 px outside a node reads as the line's port.
- CellDesigner: the added edit points stay 3 px outside the nodes, so no line runs to a node's centre.
- Multimers: the count as the unit N:3 with CellDesigner's prefix N (no "free input").
- No node is moved in conversion:
  the small moves that straightened lines for CellDesigner are gone, and with them the button CellDesigner
  (positions kept). CellDesigner (advanced) holds the process glyph where yEd has the process, and lets a
  line reach a large node beside its centre, by edit points CellDesigner draws over or along.
- Multimers beyond 2 in CellDesigner: drawn as dimers at the yEd size, the count as the unit of
  information N:x.
- Design: the tidy moves are an add-on of their own (`cd_tidy.py`) after the CellDesigner adapter, which
  moves no node but for the room of a complex's name. Every file the same.
- Documentation: these pages.

## 2026-10-23

- Standard sizes: metabolites are 40 x 40 circles (were 36 x 36 circles and stadiums sized to the name),
  also in the straight GraphML from CellDesigner and in CellDesigner files.

## 2026-10-22

- GraphML (standard sizes) for a GraphML map too, when the tick box Standard node sizes is ticked.
- Dashed (unknown) arcs kept in the biology and the check, and in SBGN-ML as an arc note.
- A family's name and its members' sites go into the notes of CellDesigner species and SBGN-ML glyphs,
  and are read back.
- SBGN-ML: a compartment inside another gets its parent compartment.
- CellDesigner: free-text units of information written and read as CellDesigner saves them.
- GraphML: state variables 18 x 18 (up to two letters) or a capsule 18 high, units of information 16
  high, the width from the text.
- Files for Newt: the margin measured in Newt (none extra for complexes, none for inner compartments).
- Clone markers are not written.

## 2026-10-21

- SBGN-ML and SBGN-ML for Newt: the Newt adjustments only in the files for Newt
 . New buttons: SBGN-ML (Newt),
  SBGN-ML (plain), each also in straight line, and Open in Newt.
- yEd's Submap glyph read as a phenotype, as in CellDesigner.
- "Process glyph" in every message.

## 2026-10-20

- GraphML (standard sizes): made for a map drawn at another scale, or for every map when asked.
- SBGN-ML: phenotypes kept without their outgoing arcs. Grown compartments cover a node they cut.
- CellDesigner: stimulation, modulation, trigger and unknown arcs between entities and out of a gate.
- CellDesigner reader: the bends of added reactant and product links.
- CellDesigner (positions kept) in place of the tick boxes for the small moves.

## 2026-10-19

- The restructured converter on the page: one model of biology and drawing, one CellDesigner species
  per molecule, every message with a kind, the routes from the converter
 .
- Fixed: SBGN-ML to GraphML on a map with a multimer simple chemical.

{% endraw %}
