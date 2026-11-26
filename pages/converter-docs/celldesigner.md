---
layout: converter-docs
title: "CellDesigner files: conventions"
permalink: /converter/docs/celldesigner/
sitemap: false
noindex: true
---
{% raw %}

Here the converter is `mapconv/graphml.py` (reader), `model.py` and `celldesigner.py` (writer), and the
symbol sheet is `docs/components44-overview.png`. Paths of map files below (`F018-estrogen/sources/...`)
are those of the working repository of the maps.

The conventions were learned from the 19 CellDesigner files on the website, checks of converted files in
CellDesigner 4.4.2, and calibration through MINERVA's converter.

## When a convention is unclear

Do not guess. Draw a small test diagram of the case in CellDesigner, save it and read the convention
from the saved file. Checks through MINERVA's converter are fine for geometry, but CellDesigner's own
file is the reference.

## Versions

Every CellDesigner file made for checking carries a version:
`<map>/celldesigner/<map>-vNN.xml` (v01, v02, ...). Each file is checked in CellDesigner, and that is
the check. MINERVA's converter is only a tool for working out geometry (absolute positions from
SBGN-ML), not a check of a new version, and no MINERVA renders are made for new versions (older
`-minerva.png` files stay). Files edited in CellDesigner keep the version they were made from in their
name (`sources/<map>-vNN-cd442-....xml`). The map README has a table of the versions and what changed.

## Older CellDesigner files

Files in CellDesigner's older layout (SBML Level 2 Version 1, model version 4.0, as 35 of the ACSN 2.0 archived
downloads) put the CellDesigner elements straight in each `<annotation>`, with no `<celldesigner:extension>`, and use SBML's
older namespace. The reader takes them as CellDesigner 4.4 does on opening: each annotation's CellDesigner elements as
its extension, the SBML elements in the current namespace, and says so in the messages. Files are written in the
current layout only. Test: `tests/test_maps.py` (ACSN 2.0's single-strand annealing map).

## Round trip

Goal: CellDesigner opens the file without warnings and
saves it without dropping anything. Small numeric differences after a save
(e.g. last-digit rounding of modifier edit points, glycolysis v05) do not
matter: do not chase them. A diff with a returned file is for finding real
changes (dropped or rewritten content, moved elements).

The converter writes the file the way CellDesigner 4.4.2 saves it (numbers
with .0, the full set of RDF namespaces, no indentation, double-quoted XML
declaration). Eicosanoids v03 is byte-identical to v02 opened and saved in
CellDesigner, so `diff` against a returned file shows only real changes.

## Annotation (MIRIAM, in the species' `<annotation>` after the extension)

- One entity: `bqbiol:is`. A family (one node, several genes): `bqbiol:hasVersion`
  listing every member. All 19 old files keep this rule (678 `is`, 1198
  `hasVersion` entries; never `is` with several proteins or `hasVersion`
  with one).
- Proteins: `urn:miriam:hgnc.symbol:X` and `urn:miriam:uniprot:Y`, in member
  pairs. The old files have no HGNC numeric ID; the converter adds
  `urn:miriam:hgnc:N` (CellDesigner keeps it).
- Metabolites: `urn:miriam:obo.chebi:CHEBI%3A12345`. Other forms are dropped
  by CellDesigner on saving, without a message.
- References on a reaction: `bqmodel:isDescribedBy` with
  `urn:miriam:pubmed:N` in the reaction's annotation (F021 has three), one bag per
  reference, as MINERVA maps hold them (some in `bqmodel`; the PD map mostly
  `bqbiol`, and MINERVA shows both). Written from the process
  glyph's property References and read back into it; a DOI as
  `urn:miriam:doi:10.1016%2Fj.jaci.2020.12.155`.
- Species inside a complex (`listOfIncludedSpecies` in the model extension)
  carry their MIRIAM RDF inside `celldesigner:notes/html/body`, not in an
  annotation element: CellDesigner's own convention for included species.
- Model `<notes>`: some old files hold conversion warnings ("Invalid element
  id", "requires thickness to be at least 2.5"). Leave model notes empty.

## Required for a clean open in CellDesigner 4.4.2

- The five unit definitions (substance, volume, area, length, time) and
  `units="volume"` on the compartments; without them a warning on opening.
- Compartment double line thickness at least 2.5.

## Geometry (checked through MINERVA)

- Residue angle: runs linearly along the box border; 0 east, pi/4 north-east
  corner, pi/2 north, pi west, 3pi/2 south. Sites without a value need
  `state="empty"`, else they are not drawn.
- Reaction edit points: frame with origin = reactant port, x axis =
  product port - reactant port, y axis = x axis turned 90 degrees (screen
  coordinates). The process glyph sits mid-segment `rectangleIndex`.
- Modifier `targetLineIndex="-1,2"` = left of the reaction flow, `-1,3` =
  right (side middles); `-1,4`/`-1,5` the left corners, upstream/downstream, `-1,6`/`-1,7`
  the right ones (MINERVA's `getAnchorPointOnReactionRect`; confirmed by MINERVA's SBGN-ML of
  a hand edit of PDH, which uses 6 and 7).
- Modifier edit points: attribute `editPoints="u,v ..."` on the
  `modification` element, one `lineDirection` per segment. Frame: origin =
  the modifier's port, x axis = to the arc's end on the process
  glyph's side (process glyph 10 wide: centre +- 5 across the flow), y axis = x
  axis turned 90 degrees. Found from bends drawn by hand in glycolysis v01 and
  MINERVA's SBGN-ML (match to 1e-7).
- Unknown species (class UNKNOWN): drawn without an outline. A colour of six hex digits (`ffffff`) is read as
  alpha 00, transparent: ExposomeMap-PM's name tags beside proteins (ERK1 beside MAPK3) and its AOP headings
  are bare text in a PDF exported from CellDesigner 4.4.
- Phenotypes: the ports lie on the hexagon, not on its box (a PDF of ExposomeMap-PM exported from
  CellDesigner 4.4, 190 x 40 boxes, every point that map uses found as a line end in the PDF): the
  tips E and W at the box's middle height, the corners NE, SE, SW, NW h/2 in from the sides, N and S in the middle
  of the flat edges, NNE, SSE, SSW, NNW halfway between the middle and the corner, ENE, ESE, WSW, WNW halfway along
  the slanted edges. Read and written so (`anchor_point`, hexagon). Inset h/2 measured on one box size only.
- Multimers: lines attach to the front shape, the box 6 smaller in width and
  height per unit beyond 1. Confirmed for N:4 by a hand edit of ASL (iNOS,
  `F007-inos/sources/F007-inos-asl-tetramer-cd442-edited.xml`): homodimer
  2 -> 4 made CellDesigner grow the box 80x40 -> 92x52, top left kept, so
  the front shape stays 74x34.
- Two processes on the same two species: no edit points, quarter ports (section "Twin processes by
  quarter ports"). Otherwise a straight line with the process glyph midway (`rectangleIndex="0"`).
- Bends on extra reactant/product links: not needed.
- Metabolites: 40x40 circles, centre kept.

## Complexes, multimers, bound ligands

Taken from F012-camp, a file saved by CellDesigner, and checked through
MINERVA (glycolysis v01).

- Complex: `complexSpeciesAlias` in `listOfComplexSpeciesAliases`, with
  `backupSize w="0.0" h="0.0"` and `backupView state="none"` after `view`;
  brief view `singleLine` width = box width. The complex species (class
  COMPLEX) is in `listOfSpecies` with a name (members joined by `:` when the
  yEd complex has no label; CellDesigner draws it at the bottom of the box).
- Members: `speciesAlias` with `complexSpeciesAlias="<complex alias>"`, usual
  view `innerPosition` = offset from the complex's top left corner. The
  species go into `listOfIncludedSpecies` (`celldesigner:species`, MIRIAM RDF
  in `celldesigner:notes/html/body`, `celldesigner:annotation` with
  `complexSpecies` and `speciesIdentity`), not into the SBML species list.
- Multimers: `<celldesigner:homodimer>` first in `state`; the count from the yEd N:x unit of
  information (an icon, or a second boxed label as iNOS ASL "N:4"); yEd's `mcount` is only the number of
  shapes drawn (always 2), used only when there is no N:x (taken alone, it would give NOSTRIN N:3, HMGCR and
  ACAT2 N:4, ASL N:4 as 2). Every multimer is written as homodimer 2 at the yEd size, the SBGN way, and a
  count beyond 2 as the unit
  `<celldesigner:info state="open" prefix="N" label="3"/>` (after a ct: unit, before other free text; one info
  per alias), so a tetramer does not grow 18 px and reach its neighbours. The form is AsthmaMap's
  (PD01 Mast Cell: N:4 and N:3 on homodimer 2), shown as "N:3". Free input is not used, as it would add
  "free input:" in MINERVA. The reader takes N:x on a dimer
  as its count; a file with homodimer 3 or more (CellDesigner's own, the box grown 6 per unit) is read by
  that count. MINERVA draws N:x at the top middle: keep it free; state
  variables go on the sides (lower half) or at the corners.
  The converter warns when a residue of a multimer sits there (none in the
  current maps).
- Bound ligands (yEd state variable "cAMP"): one `structuralState` per
  species (`listOfStructuralStates`, after the modifications), plus
  `<celldesigner:structuralState angle="..."/>` on the alias after `view`.
  All old files do the same (cAMP, AMP, ATP, Ca2+). Two cAMP icons become one
  "cAMP": CellDesigner has one structural state per species. F018 writes
  "1:cAMP" and "2:cAMP" for different counts.
- Reversible reaction: no `reversible` attribute (true is the SBML default;
  CellDesigner drops `reversible="true"` on saving and keeps
  `reversible="false"`); MINERVA draws arrowheads at both ends.
- Learned from CellDesigner's save of glycolysis v01: in the notes of included
  species CellDesigner writes the RDF namespaces in alphabetical order (bqbiol,
  bqmodel, dc, dcterms, rdf, vCard); the complex's brief-view `singleLine`
  width is stored as a float (107.45129863291555 -> 107.45130157470703);
  extra reactant and product links get a `connectScheme` (direct, one line
  direction "unknown") between `linkAnchor` and `line`.
- Learned from three round trips of the viewer's editor files through CellDesigner 4.4.2: in a complex member's
  notes the RDF comes one element per line, also after the family's name; a species' notes text ends with a line
  break before `</body>`; `listOfCatalyzedReactions` follows the order of the reactions in the file. Left as they are:
  a modifier's bend point fraction (CellDesigner recomputes it and may change its last digit) and a gate input's two
  forms (CellDesigner writes both itself).
- Names: commas stay as they are (no `_comma_`; MINERVA does not decode it,
  the old files keep the comma).

## Modifications, genes, RNAs, source/sink (glutaminase v01)

- Residue sites carry no name: the converter writes only the modification
  state, so CellDesigner shows the symbol in the circle (P, Ac, Ub, Me, ...)
  and no site label. The sites go into the species' notes instead, one line
  `PTM: P@S1177 Pa@C26 Pa@C15 My@G2`: every site of the species, its state
  variables' first, then the property PTM's; read back into PTM. CellDesigner 4.4.2 draws a named residue's site as text beside its circle, where it
  runs over the species' name (eNOS with S1177, C15, C26, G2: the name unreadable). Nodes of one protein share one residue when
  the icons name the same site (Pa@26), wherever they sit; icons without a
  site share one by place. By place alone, eNOS, with 4 sites
  drawn at 7 places, would get 7 residues (Pa@26 at 165, 179 and 195 degrees), and
  the SBGN-ML export 7 state variables, 3 of them empty; EGFR
  (phosphoinositides) 2 for one site.
- Sites kept without CellDesigner drawing them (CellDesigner 4.4.2, a test file of four NOS3 proteins, opened and
  saved once): a residue's name is drawn inside the shape beside its circle; a site written as the residue's id
  (`id="S1177"`, the modification's `residue` the same) is not drawn and is kept by a save byte for byte; a line
  `PTM: P@S1177 Pa@C26 Pa@C15 My@G2` in the species' notes or in the protein's notes is not drawn and is kept, the save
  adding only a line break before `</body>` (and after `<body>` in the protein's notes).
- Reading: a residue belongs to the protein, and CellDesigner draws every residue of a protein on every species of
  it, an empty circle where the species sets no state. The reader gives each species all of them: its own states in
  its own order, then the protein's other residues, empty, so a protein drawn several times has the same state
  variables on each glyph in SBGN-ML and GraphML. Protein entries of one name and type count as one protein (files
  written by other tools often hold one entry per species): their residues are joined, by site name, an unnamed one
  by its angle. The writer already keeps one protein per name, its residues gathered from every glyph (above).
- CellDesigner 4.4 Startup Guide (pp. 39-40, 84): the
  modification menu offers phosphorylated, palmytoylated, acetylated,
  prenylated, ubiquitinated, protonated, methylated, sulfated, hydroxylated,
  empty, glycosylated, don't care, myristoylated, unknown. A residue's name
  is optional (the residue dialog has id, name, type, side, angle). Genes and
  RNAs only take phosphorylated, acetylated, methylated, unknown, don't care.
  XML values for protonated, don't care and unknown: "protonated", "don't
  care", "unknown" (checked through MINERVA).
- Nucleic acid feature: GENE, or RNA when it carries a ct:...RNA unit of
  information (ct:mRNA). One `gene` / `RNA` per label in `listOfGenes` /
  `listOfRNAs`; the species points to it with `geneReference` /
  `rnaReference`. The ct unit stays as
  `<info state="open" prefix="ct" label="gene" angle="-1.5707963267948966"/>`
  (the old files' form).
- Source/sink (yEd EmptySet): class DEGRADED, one species per yEd node, named
  after its id (CellDesigner names a new one s48 and the like). yEd size kept.
- Transcription and translation stay as drawn in yEd: STATE_TRANSITION from
  a source with a TRIGGER from the gene (or the mRNA). CellDesigner also has
  TRANSCRIPTION and TRANSLATION reaction types (gene -> RNA -> protein
  lines); not used.
- `listOfCatalyzedReactions` on a species lists every reaction it modifies
  (catalysis, trigger, stimulation, inhibition), not only catalysis:
  CellDesigner's save of glutaminase v01 added the trigger and stimulation
  ones; F021 (made in CellDesigner) lists an inhibitor.
- Greek letters in names: `_epsilon_` and the rest of the alphabet, as
  `_alpha_`.

## CellDesigner symbols and the yEd maps

`docs/components44-overview.png`: a picture of
CellDesigner's symbol sheet (`<CellDesigner folder>/samples/components44.xml`).
The yEd SBGN of the maps is mostly a subset of it. Scan of 14 annotated maps:

- Modification states used: empty (81), P (79), Pa (22), My (11), Ac (2).
  All in CellDesigner's menu.
- State variables without a modification: active (13), inactive (9), cAMP,
  Ca, Ca2+, AMP, ATP, cGMP, 1:cAMP, 2:cAMP. The converter writes them as a
  structural state, as the old website files do (13 "active", 9 "inactive"
  there). No node has two of them.
- Units of information: ct:gene (4), ct:mRNA (7) only.
- Arcs into processes: consumption 274, catalysis 94, stimulation 18,
  necessary stimulation (trigger) 10, inhibition 1.
- Also on the maps: logic operators (6, with 12 input arcs; CellDesigner
  boolean gates), submaps (2; no CellDesigner symbol, written as a phenotype), a stimulation arc to
  a phenotype (1; CellDesigner draws it as a reduced stimulation),
  compartments.

## Compartments, bends, ports (estrogen and eNOS v01)

- Compartments: yEd group nodes without an SBGN class. `compartmentAlias`
  class SQUARE at the yEd box, `namePoint` at the top left of the yEd label,
  `doubleLine thickness="12.0" outerWidth="2.0" innerWidth="1.0"` (as F021,
  made in CellDesigner), colour: the paint whose band shows the yEd fill
  blended over white (yEd fills are transparent); CellDesigner draws the
  two lines in the paint and the band at alpha 63 of 255. SBML `compartment` with `outside` = the enclosing
  compartment or `default` (nesting: F018 nucleus and mitochondria in the
  cytoplasm). Outer compartments first in both lists. Species and complex
  aliases carry `compartmentAlias`, species `compartment`; complex members
  carry neither (F021). Checked through MINERVA: boxes land on the yEd boxes.
- yEd ports sit at the tips of the process arms, one process
  width from the centre; points there are ports, not bends.
- Consumption arcs drawn in yEd from the process to the reactant (no
  arrowhead; F008 has five): reactants. Production = an arc from the process
  with an arrowhead.
- Line ends off the node centre in yEd (port offset, e.g. a line leaving a
  complex at its bottom left), in the advanced layout: the nearest of CellDesigner's 16
  ports (N, NNE, NE, ENE, E, ...; corners, side centres and quarter points;
  Startup Guide Appendix 2.3). Positions of the quarter points assumed at
  1/4 and 3/4 of the side; MINERVA places them there. Metabolites follow
  "Metabolite circles: where lines meet them".

## Centre position and other lessons from the estrogen edit

`F018-estrogen/sources/F018-estrogen-v01-cd442-edited.xml` (v01 edited and saved
in CellDesigner):

- Centre position: a base reactant/product without `linkAnchor`, a modifier
  without `linkTarget`, an extra link without `linkAnchor`: the line goes to
  the node centre (cut at the border). This is the default; it is
  yEd's default port (offset 0,0). The converter writes it for central
  yEd ports and for ports at the middle of a side; other offsets get the
  nearest of the 16 ports.
- Edit point frame with a centre end: origin the node centre (checked
  through MINERVA: bends land on the yEd points). For a multimer, the centre
  of the whole box, not of the front shape (eNOS NOSTRIN).
- Bound ligands: one structural state "cAMP", no counts ("1:cAMP/2:cAMP" is
  confusing). Placed at the icon with the highest count.
- CellDesigner on saving: compartment `namePoint` 12.5 lower (the text
  baseline); a `celldesigner:name` in each compartment's annotation; the
  usual-view `innerPosition` of an alias in a compartment = its offset from
  the top left of its (innermost) compartment. The converter writes all three.

## How CellDesigner builds a reaction (eNOS)

`F008-enos/sources/F008-enos-v01-cd442-isolated.xml`: one reaction redrawn in
CellDesigner (HSP90 + CAV1:CaM:eNOS -> CaM:HSP90:CAV1:eNOS + CaM).

- CellDesigner builds a reaction in two steps: first the main direction,
  one source and one target (here complex centre to complex centre), then
  further substrates and products as extra links. The converter picks as
  base reactant and product the pair that faces each other through the
  process (the process between their centres, least off their line); the
  others become reactant/product links.
- Main vs additional: `baseReactants`/`baseProducts` are the main source and
  target (the base line through the process glyph); `listOfReactantLinks`/
  `listOfProductLinks` are the added ones, attached to the base line
  (`targetLineIndex` -1,0 reactant side, -1,1 product side). Only layout:
  SBML `listOfReactants`/`listOfProducts` make no difference.
- Choosing the main pair: first avoid metabolites (simple molecules,
  source/sink) as long as larger species are there (complex to complex,
  as in the eNOS v03 edit, BH4/BH2 exchange), then the pair the process sits
  between, least off their centre line.
- No bend points by default, on main lines, extra links and modifiers: bends are for a
  few long connectors (section "Significant bends"), and working out many
  bends to fit the yEd look is not the aim.
- Straight layout: every line end at the centre, whatever port offset yEd has (offsets come from
  the yEd layout; in the eNOS v03 edit DNM2 joining goes from complex centre
  to complex centre, not ENE to N). The 16 ports are used only in the advanced layout.
- Extra link to a node centre: `linkAnchor position="INACTIVE"` (base links:
  no linkAnchor; modifiers: no linkTarget).
- Reaction ids: yEd's `n0::n17` is no SBML id; `re_n0_n17`.

## Logic gates, submaps, arcs without a process (test files saved in CellDesigner)

- Gate (`F003-mevalonate/sources/F003-mevalonate-v01-cd442-gate-example.xml`):
  in the reaction's `listOfModification`, one `modification` with
  `type="BOOLEAN_LOGIC_GATE_OR"` (AND, NOT), `modifiers` and `aliases` listing
  the inputs (comma separated, left to right), `modificationType` = the arc
  from the gate to the process (CATALYSIS, TRIGGER, ...), `targetLineIndex`,
  and `editPoints="x,y"` = the gate's absolute position (MINERVA puts the gate
  there). The gate can sit anywhere: the converter uses the yEd
  operator's position. A gate CellDesigner saved with bends (PD map histamine signalling): the gate is the last point of `editPoints`, the points
  before it the bends of the line gate -> process, in the frame gate -> process; each input's
  modification carries its port (`linkTarget`) and its bends in the frame input -> gate. Then one `modification` per input, of the
  modificationType, with `linkTarget` port INACTIVE and no targetLineIndex.
  Any number of inputs (`tests/celldesigner/gate-or-multiple.xml`: an OR of
  five on a catalysis, the gate's line at targetLineIndex -1,2): every input in `modifiers` and `aliases`,
  one modification each; AND, NOT and the unknown gate ? are read and written the same way (every gate
  works the same in CellDesigner, NOT included). Drawn in CellDesigner: the gate made the usual way (two inputs, then the target),
  further inputs with the add-reactant tool; CellDesigner saves an added input as one of the first two.
  A NOT with one input (SBGN's NOT), as the converter writes it, opens in CellDesigner and is saved as written:
  the gate's modification and the input's with `targetLineIndex="-1,0"`, no `linkTarget`
  (`tests/celldesigner/gate-not-one-input.xml`, as CellDesigner saved it).
  Every input is a modifierSpeciesReference and lists the reaction in its
  listOfCatalyzedReactions. yEd: Operator node, inputs joined by plain arcs
  in either direction.
- Gate between entities (reduced notation, no process; the test file
  `tests/celldesigner/gate-trigger-modulation.xml`): a reaction of type
  BOOLEAN_LOGIC_GATE, the inputs as base reactants, the target as base product, a
  GateMember of the gate's type with `modificationType` the arc out of it
  (REDUCED_TRIGGER, REDUCED_MODULATION; REDUCED_PHYSICAL_STIMULATION for a
  stimulation, NEGATIVE_INFLUENCE for inhibition; the PD map's POSITIVE_INFLUENCE is read), then one GateMember per input of
  that type. All four are written and read.
- Unknown gate (`BOOLEAN_LOGIC_GATE_UNKNOWN`, the question mark): the
  yEd Operator **?**, both ways, as a modification gate and between entities; an equivalence operator is written as
  it.
- Unknown (dashed) reduced arcs (the test file `tests/celldesigner/unknown-reduced.xml`):
  UNKNOWN_ before the type, between entities (UNKNOWN_POSITIVE_INFLUENCE,
  UNKNOWN_NEGATIVE_INFLUENCE, UNKNOWN_REDUCED_PHYSICAL_STIMULATION, UNKNOWN_REDUCED_MODULATION,
  UNKNOWN_REDUCED_TRIGGER) and out of a gate (its modificationType and each input's
  GateMember). There is no UNKNOWN_PHYSICAL_STIMULATION: a dashed stimulation between
  entities is written UNKNOWN_REDUCED_PHYSICAL_STIMULATION, the same head as the solid one.
- A gate into a gate has no CellDesigner form. When the second
  gate (the one nearer the target) is OR, it goes: each of its inputs, entity or
  gate, points at its target with the type of its arc out, since several arcs onto
  one target read as any of them (Newt's TGF-beta: AND into OR into Gene
  transcription). When it is AND, the arc is left out with a message.
- Submap: no CellDesigner symbol; a PHENOTYPE at the yEd box (the SREBP
  file `F005-srebp/sources/F005-srebp-v01-cd442-phenotype.xml`).
- Phenotype, submap and perturbing agent share CellDesigner's PHENOTYPE. A species written from a submap or a
  perturbing agent (Activity Flow's perturbation too, written as a perturbing agent) carries the line
  `SBGN class: submap` (or `perturbing agent`) first in its notes; reading it back, on a PHENOTYPE only, gives that class again, so SBGN-ML gets the submap or perturbing
  agent and GraphML keeps it as the node property SBGN class. A PHENOTYPE without the line stays a phenotype, with
  every arc it has, in and out: the arcs do not tell the three apart, so the class is never guessed from them.
- Arc between two entities without a process (stimulation of a phenotype or
  submap): a reaction with `reactionType` REDUCED_PHYSICAL_STIMULATION, also out of a logic gate,
  its white arrowhead SBGN's (POSITIVE_INFLUENCE, an open arrow with no SBGN equivalent, is read as a
  stimulation and never written; onto a process the PHYSICAL_STIMULATION modifier), base reactant
  and base product only, both `linkAnchor position="INACTIVE"`, no process,
  `reversible="false"`. Only the yEd stimulation arrow (white_delta) is
  mapped; other arrows get a warning.
- Added link's edit points (the test file `tests/celldesigner/added-link-bends.xml`;
  checked through MINERVA on all 22 such links of PD map autophagy and
  histamine signalling, exact): a frame as for modifiers, from the link's species end
  (its port, else its centre) to the point where the link joins the main line, or the
  other way for a product (join -> species). The join is on the segment with the process glyph
  (rectangleIndex), at 3/8 of it for a reactant, 5/8 for a product, the segment's ends
  where CellDesigner draws them (a species' port, else its border). Read; the writer
  still writes added links straight.
- Added reactant/product links to a centre: no linkAnchor (CellDesigner's
  save of mevalonate v01 drops an INACTIVE written there).

## Twin processes by quarter ports; gate inputs as saved

From a hand edit of mevalonate v03 in CellDesigner
(`F003-mevalonate/sources/F003-mevalonate-v03-without-twin-rule-cd442-edited.xml`):

- Two processes on the same two species (phosphorylation and
  dephosphorylation of HMGCR): no edit points. Each is a straight line
  between quarter ports on the facing sides of the two boxes: the
  process above the line between the centres uses the upper quarters (ENE /
  WNW), the one below the lower (ESE / WSW); for boxes stacked vertically the
  left (NNW / SSW) or right (NNE / SSE) quarters. Which side: where yEd has
  the process.
- Gate inputs: `targetLineIndex="-1,0"` and no `linkTarget` (as CellDesigner
  saved them).
- Regulatory arcs: attached to the side of the process glyph facing the modifier
  (targetLineIndex -1,2 / -1,3, a one-line test). Arcs that cross another
  line because of where the modifier sits are left to the manual pass
  (avoiding them needs routing).

## Straightening slightly-off main lines (glycolysis edit)

`F001-glycolysis/sources/F001-glycolysis-v08-cd442-edited-orthogonal.xml`: the
PKA complexes and PKA cat put on one vertical line by hand. In the advanced layout the converter does
it (`cd_tidy.py`): nodes joined by a main line at most 10 px off the vertical get one common x, off the
horizontal one common y. Across all maps such lines are 0-5 px off and the next ones 20+ px (intended
diagonals). The other layouts move no node in conversion: there straightening belongs to the source map, the
layout skill's `standardise.py`, if wanted.

## Significant bends (`mapconv/layout.py`, bends)

From hand edits (glycolysis v08: two PFKFB2 catalysis arcs; aspirin
v02: arachidonate -> 15R-HETE), one corner each, matching the yEd elbow.

- Found in yEd: the route of an arc (node centre, bends without the process
  ports, process centre), simplified (Ramer-Douglas-Peucker, 20 px); a bend
  counts when exactly one corner remains and the route is at least 150 px
  long. From yEd only the way the L turns (horizontal or vertical first).
- Corner built from the CellDesigner file: x of one end, y of the other.
  Main line: ends at the reactant and product centres; one bend on the
  reactant arc or on the product arc (not both); the process glyph goes on the
  segment where yEd has the process (after the corner for a reactant-arc
  bend: `rectangleIndex` 1). Modifier: from its centre to the arc's end on
  the process glyph's side (5 px from the process glyph centre); frame origin the modifier
  centre, x axis to that end (checked through MINERVA: the corner lands
  exactly).
- From a hand edit of phosphoinositides: (1) a line that leaves a metabolite circle below its
  centre (where the name is not) keeps its first bend at that height, not at the circle's centre (a 7 px jog on
  PI(3,4)P2 -> PI4P and PI3P); (2) the two points that hold a process glyph where yEd has it stay at least 3 px
  outside both end nodes, or are left out and the glyph sits midway (a point 1 px inside GRB2:GAB1); (3) a bent
  modifier arc ends on the side of the process glyph facing its last bend, not its modifier's centre (EGF:EGFR,
  which catalyses its own step, sits on the main line: the arc ended on the far side and its arrowhead was hidden).
  Confirmed by the edited file: the bends placed by hand match (1) within 0.6 px.
- Quarter points on circles (metabolites) sit on the circle at 22.5 degree
  steps (ENE = 22.5 degrees), not at the box quarters (twin
  process glyphs between metabolites are otherwise 2 px off).
- Result over the full set: 24 bends, every corner a right angle (within
  0.5 px, MINERVA).
- Added reactant/product links stay straight (not needed).

## Hand edits of the full set

`<map>/sources/<file>-cd442-edited.xml` (zip `celldesigner-all-edited`). Same
species and reactions everywhere; geometry only; iNOS and glycogen liver
unchanged. Published on the website as they are (17 maps; glycogen liver
from the muscle edits, `F004-glycogen/build_liver_from_muscle_edits.py`).

What the edits show:
- Modifiers moved so their arc meets the process glyph straight: 23 times
  (offsets 2-15 px, once 45); never the other way. In the converter's advanced layout
  (automatic when the move is small and nothing overlaps):
  after straightening, a modifier is moved up to 15 px (ALIGN) along one axis
  so its arc meets the process glyph straight; the same move for every reaction it
  acts on; not if it ends a main line straight on that axis, not if it would
  leave its compartment or overlap another node; complex members move with
  their complex; L-shaped arcs are left alone. Against the edits: of
  the modifiers it moves, 29 of 45 are aligned in the edited files too (often
  the other end was moved instead), 16 were left as they were.
- Lines through other nodes: 5 in the full set, 3 fixed by hand.
- Bends: most changed values are CellDesigner recomputing the edit points
  after moves; the converter's bends were kept. New by hand: 3 (a modifier
  in mevalonate, a main line in glycogen muscle, a modifier in
  phosphoinositides); removed by hand: 2 (TAG stimulation arcs). No rule.
- Stimulations without a process: CellDesigner drops the INACTIVE ports;
  the converter writes none (SREBP, ACLY).
- Modifier attachment: CellDesigner also uses targetLineIndex -1,5 (TAG);
  the Startup Guide's figure numbers the process glyph's points 2-4 (top) and 5-7
  (bottom). The converter keeps 2/3, except in the advanced layout (section "Advanced layout:
  the rules", modifier arcs).
- Many moves are spacing (blocks shifted, room for labels): no rule.
- iNOS (`F007-inos/sources/F007-inos-v05-cd442-edited.xml`):
  three urea-cycle reactions redrawn so the main line follows the cycle
  (arginine -> citrulline, citrulline -> argininosuccinate,
  argininosuccinate -> arginine), side metabolites (O2, NO, aspartate,
  fumarate) as added links. Which metabolite is the main one is a biological choice: the rule
  "backbone first" (prefer species that also take part in another process), first or as a
  tie-breaker after "avoid metabolites", fixes two of the three but breaks others (eNOS
  ADMA -> DMA becomes H2O -> citrulline, arginine -> NO becomes O2 -> NO).
  A possible exact route: a marker on the main arcs in
  yEd (custom property or line width) that the converter reads.

## SBML through MINERVA; ids and complex names

- SBML and SBGN-ML downloads (website `atlas-downloads/`) are made by `tools/minerva_exports.py
  <website repo>/atlas-downloads [maps]` (or `/downloads` for the official copies), a script of the
  working repository of the maps (MINERVA's conversion service). MINERVA cuts ids at a double underscore:
  `re_n1__n28` and `re_n1__n31` both become `re_n1`, and the SBML export
  fails ("Problem with exporting bioEntity"; glycogen, eNOS, iNOS, estrogen,
  ...). The script sends reaction ids with single underscores; the converter
  writes all ids that way (`n1::n28` -> `n1_n28`).
- Unnamed complexes inside unnamed complexes are named inner first,
  each member once ("PKA reg:cAMP", not "PKA reg:cAMP:cAMP").

## Seen in the old files

- Extra reactants/products: `listOfReactantLinks` / `listOfProductLinks`
  with their own port, connect scheme and line.
- Modifiers TRIGGER, PHYSICAL_STIMULATION, INHIBITION (all written by the converter).
- Classes used: PROTEIN, SIMPLE_MOLECULE, COMPLEX, RNA, GENE, ION, DEGRADED,
  PHENOTYPE.
- States used: phosphorylated, palmytoylated (CellDesigner's spelling),
  myristoylated, acetylated, ubiquitinated, empty.

## Units of information: two yEd glyphs

yEd draws a unit of information either as a plain box icon (ShapeNode: iNOS,
estrogen, glutaminase, the N:x of most maps) or as its SBGN glyph (GenericNode
com.yworks.sbgn.UnitOfInformation: ACLY ct:gene/ct:mRNA, glycogen, SREBP), or
as a second boxed text label (iNOS ASL "N:4"). The converter reads all three.

## State patch of the published files

`tools/cd_fix_states.py <published.xml> <converter output.xml> <out.xml>` (a script of the working
repository of the maps) gives each protein the converter's residues and each species its identity
(class, protein/gene/RNA reference, state; the published name kept), the gene
and RNA lists and each alias's unit of information (ct:) follow the converter; a multimer whose count changes grows 6 per unit,
top left kept. Nothing else changes (the published files are edited by hand).

## SBGN within CellDesigner

- CellDesigner offers more classes and reaction types than SBGN; the converter uses only
  the SBGN ones. Reactions: STATE_TRANSITION (also across compartments, e.g.
  cholesterol cytoplasm -> mitochondria; no TRANSPORT), REDUCED_PHYSICAL_STIMULATION
  for arcs without a process. No ION: every metabolite is SIMPLE_MOLECULE
  (SBGN has only simple chemical); an ION in a file is an error to fix. The
  converter writes none of the others (atlas set checked: classes PROTEIN,
  COMPLEX, SIMPLE_MOLECULE, GENE, RNA, PHENOTYPE, DEGRADED only).
  Older files in the official `downloads/` still break it: ION Ca2+ in glycogen liver and muscle; HETERODIMER_ASSOCIATION
  (mevalonate), UNKNOWN_TRANSITION (estrogen), REDUCED_PHYSICAL_STIMULATION (ACLY).
- Bound ligand as structural state: written once ("cAMP"), no counts.
  CellDesigner has one free-text structural state per species, nothing else
  can carry a ligand, so the yEd icons collapse to one: CaM with four "Ca"
  icons (mevalonate) -> structural state "Ca"; two "cAMP" (glycolysis, TAG)
  -> "cAMP". The yEd maps stay as they are: the limit is CellDesigner's, not the GraphML's.
- The rule (from CellDesigner's symbol sheet, `docs/components44-overview.png`): a state
  variable that is one of CellDesigner's modification circles (P, Pa, Ac, Pr,
  Ub, H, Me, S, OH, G, My, empty, * don't care, ? unknown) is a residue, as
  many as the node has; anything else (active, inactive, cAMP, Ca, ATP, ...)
  goes into the one free-text structural state (different texts joined by
  "/"; none in the current maps). The converter does this for all of them;
  XML values for H, * and ?: "protonated", "don't care", "unknown" (checked
  through MINERVA, which shows H, *, ? and rejects other spellings).

## Reversible processes with several arcs; free-text-only proteins

- A reversible process (production arcs on both sides, no consumption arc) with more than two
  arcs (BCAT2 in F022: leucine + alpha-ketoglutarate <-> alpha-ketoisocaproate + glutamate):
  the arcs on the upper (or left) side of the process are the reactants. An arc's side is that
  of its first yEd bend, else of its entity; the axis is the one along which the arcs spread
  most. Then the main pair is chosen as for any reaction.
- A protein whose marks are all free text (Su, Glut: not in CellDesigner's menu; CPS1 in F021)
  gets no residues: its empty circles (OVAV in yEd) are dropped, the marked nodes get the
  free-text structural state, unmodified nodes nothing.

## The layouts, first worked out on F022 BCAA v04

The CellDesigner file comes in layouts (`--layout`): `straight`, the default, is the necessary minimum
(simple rules, a basic and reliable conversion improved by hand); `advanced` gives a layout that already
looks good in CellDesigner. Their rules were first worked out by a map-specific script for F022 BCAA v04
(`F022-bcaa/cd_layout_v04.py`), which post-processed the converter output:
- Modifier arcs with yEd bends or an off-centre start get edit points (frame of `cd_layout.to_frame`),
  snapped orthogonal against the CellDesigner positions; an off-centre start becomes one point 1 px
  outside the node at the process glyph's height.
- A process glyph where yEd has the process: two edit points on the straight main line, 8 px either side,
  `rectangleIndex="1"`, three line directions.
- Lanes leave a metabolite circle 12 px below its centre, so they do not cross the name.

Differences in the converter from the script:
- The process glyph is placed before the modifiers are aligned onto it, so the small alignment moves
  (up to 15 px) aim at the process glyph where yEd has it. On the 24 test maps every node this
  changes ends up closer to its yEd position (49 nodes).
- No node is moved for a route. A routed arc that runs through another node is reported
  ("n1::n38: the arc from α-ketoisocaproate runs through PPM1K:Mn2+"), to be moved by hand in
  CellDesigner (the BCAA check moved PPM1K:Mn2+ 36 px right).
- Lanes leaving a metabolite: see "Metabolite circles: where lines meet them".
- A modifier arc with no bend that starts off its node's centre takes the nearest of the node's 16 places,
  not a point 1 px outside the node: such a point stays behind when the node is moved in CellDesigner.
BCAA: as v04 except the 20 px move of PPM1K:Mn2+ and its modifiers leaving off their centres, which start at
a place (six edit points fewer).

## Metabolite circles: where lines meet them (advanced)

A metabolite is a circle with its name drawn across the middle. In the advanced layout a line
meets it where the name is not (from PD02 eicosanoids: 85 of 104 lines from
above or below at N or S, sideways lines mostly at ESE or WSW): at N or S when it leaves up or
down, at ESE or WSW (the lower quarter of the side) when it leaves sideways. The way it leaves:
the first leg of an L, else towards the process; for a modifier, towards its first bend or the
process glyph. Main lines get linkAnchor, modifiers a linkTarget with linkAnchor (as the PD map), the
modifier's first bend in line with that point. Two processes on the same two species keep their
quarter points. The straight layout keeps lines at the centres.

## Advanced layout: the rules

Worked out on PD02 eicosanoids (CellDesigner -> GraphML -> CellDesigner, `test_round_trip`) and
hand edits in CellDesigner of pyrimidine (v05-v08), iNOS (v07, v08), urea cycle (v02), BCAA
(checked v04). Principle: write a port or edit point only where it changes the drawing,
and move a node before adding bend points; points that change nothing make relayout by hand
harder. When the converter already has a line straight, keep it: CellDesigner's view can show it
a few px off (hand moves of ERK1/2, 6 px, and SIRT5, 4 px, made lines the converter had
level 3-4 px off by its reading).

Main line of a process with several reactants or products, in order: larger species before
metabolites; never a pair whose midway process glyph would sit on another node; a pair drawn straight
through the process in yEd (3 px); a pair on a cycle, the product leading back to the reactant
through other processes (iNOS: arginine, citrulline, argininosuccinate main, O2, NO, fumarate,
aspartate added; urea cycle ASS1); the pair nearest the process.

Geometry of a main line:
- Edit points: one long L keeps the corner rule (x of one end, y of the other); the L is read
  with the yEd bend at the process's port, which says from which side the line comes in (iNOS
  ASL, ASS1). An L whose bend is more than 20 px from that corner keeps its slanting leg; other
  routes keep every bend that moves the line by more than 20 px (`layout.bends`: PD02's Z
  routes and detours round other nodes).
- Ports: where the yEd arc meets the entity's border (nearest of CellDesigner's 16; on a
  metabolite E and W become ESE and WSW), else on a metabolite where its name is not (section
  above). Kept only if it moves the line more than 2 px from the line to the centre.
- Two processes on the same two species, both drawn straight: quarter points.
- The process glyph where yEd has the process (no node moved), when that is more
  than 3 px from midway on its segment (`SHIFT`; also on a bent line), within 12 px of the line (a
  metabolite's line leaves 10 px off its centre, under its name) and between 0.1 and 0.9 of it: two edit
  points half way from the process glyph to the nearer end on either side, at least 3 px outside the end
  nodes and at the same distance from the process glyph,
  so the arcs keep visible antennas (points 8 px beside the process glyph look as if the arcs ran into it; a
  hand edit of CAD put them about 0.6 of that way). On the line, so CellDesigner draws nothing more. Else midway (CellDesigner's own
  rule). 3 px: the yEd offsets run on without a gap (0-5 px 23 processes, 5-10 px 39, of 168 placed on
  the 28 Atlas maps), and below 3 px two points per reaction would add clutter for nothing seen.
- A line's end off a species' centre goes to the nearest of its 16 places, never through a point added
  outside the node: such a point stays where it is when the species is moved in CellDesigner. Where the line
  has a bend of its own next to that end, the bend moves into line with the place, so a straight leg stays
  straight; a line without one may tilt by a few px. Lines share a place when a side has more lines than
  places, as CellDesigner does. The messages list, per species, the places shared and the ends moved more
  than 5 px.

The rules above are for CellDesigner (as drawn), `-drawn.xml`. CellDesigner
(straight & bends), `-bends.xml`, has the drawing below without the moves. CellDesigner (advanced) keeps the
tidy moves (`cd_tidy.py`): main lines up to 10 px off straightened,
the other end of a level line into a larger node beside its centre moved in line with where the line meets
that node, its centre or the place it takes (iNOS CaM 23.6 px onto the centre line; moved 25 px by hand twice), a modifier up to 15 px onto its process glyph, on a drawing with the
process glyph placed only for a modifier straight across that could not be moved. Straight line moves no
node.

Modifier arcs: the end on the process glyph. A process with several modifier arcs, one of which yEd
ends off the process's centre (more than 2 px): that arc ends at the process glyph's point nearest its yEd
port (a corner, `-1,4` to `-1,7`, or a side middle), so the arcs do not merge into one line
(PDH: PDK, pyruvate and dichloroacetate on the PDK step, acetyl-CoA and NADH on
PDH; a hand edit of PDH in CellDesigner has the same points). Else the side facing the
modifier. A modifier arc counts as straight across when it is in line with its yEd port
or with the process's centre. This applies to TAG (2 arcs), BCAA (4), PDH (6; PDK 5 px left onto its
corner). Back to yEd (advanced) the arc ends at the same point of the 18 px process: corners at
(9, 9), side middles at (0, 9) across the flow, so GraphML -> CellDesigner ->
GraphML -> CellDesigner gives PDH's drawing twice (`test_repeat`).
The route: the yEd route made orthogonal; a straight arc from off the centre takes the nearest of the
16 places when that moves the line by more than 2 px. No edit point on a
straight line between its neighbours (`layout.unbent`, also used on the way back).

Both layouts: CellDesigner writes a complex's name at the bottom inside it. Its members move up to
leave NAME_ROOM (14 px) below their outline (a state variable on the bottom edge reaches 8.5 px
below the node, yEd's second shape of a multimer 6 px), as far as 8 px above them allows; the
complex grows down for the rest. 14 px is the bottom of the complex packing rule of the
sbgn-human-like-layout skill (`complex_pack.py`), so a packed GraphML keeps its geometry in
CellDesigner. MINERVA writes the name about 3.6-12.5 px above the complex's
bottom edge, so it stays about 1.5 px clear of a bottom state variable.

Results: PD02 round trip every process glyph within 38 px; pyrimidine and iNOS advanced equal
the last hand edits apart from rounding and the antenna length; urea cycle v02 needed only
SIRT5 4 px and CPS1 1 px; BCAA looks as checked. Squares placed by edit points: BCAA 8, iNOS 4,
pyrimidine 1, mevalonate 1, glycolysis and nNOS none.

Open:
- Move a whole subpathway in place of bend points (RAF1, MEK1/2 and ERK1/2 moved together by
  hand, keeping equal distances). Needs knowing what a subpathway is; separately.
- What remains on CellDesigner's own maps: the yEd-oriented moves (modifiers onto process glyphs,
  straightened main lines) also act on them; metabolites become 40 px circles.

## Hidden bends, reading CellDesigner

CellDesigner draws its nodes over the arcs, so a file holds edit points nobody sees: inside the
arc's own source or target (on influence arcs and modifiers above all), or on the straight line
between their neighbours. yEd and Newt draw them (an arrow folded back inside its target). The
reader keeps only the bends CellDesigner shows (`layout.visible`): the run of points at the start
of an arc inside its source and at its end inside its target is left out, and the arc's port goes
to where CellDesigner's line crosses the node's border, when a line from the old port would differ
(a process or operator keeps its port); then the points on the straight line, measured from the
ports. Points of an arc that leaves a node and crosses it again are
seen in CellDesigner and kept. Measured on 97 CellDesigner files (official, PD map, AsthmaMap,
ACSN): 1186 of 18509 edit points left out, inside an end node 1151 -> 10.

## Units of information: CellDesigner's prefixes and free text

CellDesigner 4.4.2's Edit Information window offers five prefixes: pc with the labels T, V and pH;
mt with ion, rad, rna, dna, prot and psac; ct with gene, tss, coding, grr and mRNA; N with any label;
and "free input" with any text. The file holds the choice as prefix and label,
`<celldesigner:info state="open" prefix="mt" label="prot" angle="..."/>`. The writer gives a unit
written pc:, mt: or ct: with one of that prefix's own labels (in any case) that prefix and label,
spelled as CellDesigner spells them (ct:mrna as ct and mRNA); N:x (or n:x) prefix N and the label
x; every other text, a label its prefix lacks included (ct:asRNA), the free-text form below.

CellDesigner saves a unit of information with free text on the species alias as
`<celldesigner:info state="open" prefix="free input" label="exampletext" angle="..."/>`
(`tests/celldesigner/free-text-unit.xml`, saved in CellDesigner), the same element as ct:gene with
another prefix. The writer gives every other unit this form (SREBP "precursor",
"processed form", "mature form"); the reader takes the
label alone. One info per alias: a node with more units keeps a ct: unit first, the rest is
reported left out. CellDesigner shows the label alone ("example..." cut to the box); MINERVA (22.0.1)
draws and exports "free input:precursor", the prefix with the label.

## Notes: family name and members' sites

What MIRIAM cannot hold goes into the species' SBML notes (XHTML body, CellDesigner's notes panel,
MINERVA's notes), one line each: "Family: PKA regulatory subunits" and "MAPK3: P@T202 P@Y204" per
family member with sites (`annotation.notes`, read back by `annotation.from_notes`). An included
species (complex member) has the lines before its RDF in the same body, each ended by a line break:
CellDesigner 4.4.2, on saving, drops the text on the same line as the RDF. Saves of carnitine and
glycolysis in CellDesigner lost "Family: PKA regulatory subunits" and "PRKAA2: P@T172" that way, the identifiers
kept; the TLR9 test below lost its second line for the same reason. The entity's own sites stay in
the GraphML property PTM only.

Units of information not drawn: the GraphML property "Unit of information", one unit per line,
holds what tells a form apart that the drawing does not show (two cleavage fragments of TLR9, one HGNC identifier:
"C-terminal fragment", "trimmed"). It is part of the entity key, so such forms are two CellDesigner species, and it
goes into the notes as one line, "Unit of information: C-terminal fragment; trimmed". Drawn units stay free for
CellDesigner's one unit per alias (ct:, or N:x, which is not free text and takes the place). One line, because
CellDesigner's save of a TLR9 test (`tests/celldesigner/tlr9-units-in-notes-v01.xml`) kept every line of a species' SBML
note but only the first line of a complex member's note: "trimmed", on a second line, was lost on both members.
The family lines above may be cut the same way on a complex member (not yet seen in a file).

## A species' location without a drawn compartment

Whether a map without compartment boxes can still tell NRF2 in the cytoplasm from NRF2 in the nucleus. Two files,
opened and saved in CellDesigner 4.4 (`tests/celldesigner/location-in-compartment-v01.xml`,
`location-in-notes-v01.xml`): both open, and both keep the location after CellDesigner's own save.
- Compartments in the model with no box (`listOfCompartments`, each species in its compartment, no
  `compartmentAlias`): kept byte for byte.
- No compartments, the location as each species' SBML note ("location: nucleus"): kept, CellDesigner adds a line
  break before `</body>`.

## Font sizes (measured in CellDesigner 4.4's PDF export)

The file stores one font property: `<celldesigner:font size="..."/>` on a species or complex alias, the size of its
name, set in CellDesigner by right-click, Change Font (window Change Species Name Font, Font Size, a Default button).
Sites, states, structural states and units of information carry none: CellDesigner draws them at fixed sizes, and no
file changes them. No font family is stored.

Measured in two PDF exports kept with the viewer's check files: `glutaminase-celldesigner-edited`
(names at 14 from the converter) and `font-sizes/font-sizes-celldesigner-user` (made from a new file in CellDesigner
4.4.2: proteins left at the default, one set to 14). Text is drawn as outlines, so each size comes from
letter heights against a name of known size: at 12 the flat capital P is 8.67, the round O 9.08; at 14 they are
10.13 to 10.16 and 10.66. A name set to 14 is drawn at 14.0 (P 10.13 against 8.67 at 12).

| Text | Letters measured | Size |
|---|---|---|
| Species name, new species (CellDesigner's default) | `font size="12"` written for every new protein | 12 |
| Species name set by the user | Prot D at 14: P 10.13 | as set |
| Unit of information (`N:6`, `ct:gene`, `ct:mRNA`) | N 8.67 at names of 12; R, N, A 8.70 at names of 14 | 12 |
| Residue site name (`S10`, `@S314`) | S 7.58 and 7.61 (round) | 10 |
| State symbol in the residue circle (P) | P 6.50 and 6.52 | 9 |
| Structural state (`active`) | t 5.83, a 5.00 against 7.79 and 6.67 at 12 | 9 |
| Complex name, new complex (default) | `font size="12"`; M, P 8.67 | 12 |
| Complex name set by the user | 14: M, P 10.12 | as set |
| Compartment name | E 8.67, t 7.79 (no font element; CellDesigner offers no way to change it) | 12 |

The structural state's ellipse in that file is 50 x 16 for `active`. The renderer (`cdrender.js` and `.py`) draws
all these sizes.

A complex's name sits with its baseline 7 above the bottom of the complex at 12 and at 14 alike, and the renderer
draws it so. Second test file: `font-sizes/font-sizes-celldesigner-user-v02`.

## Stoichiometry (cardinality)

CellDesigner 4.4.2 keeps a stoichiometry on every reactant and product (the SpeciesReference window: stoichiometry,
stoichiometryMath) and does not draw it on the line. It is SBGN's cardinality. In the file it is an attribute of the
reaction's `speciesReference` (listOfReactants or listOfProducts), written only when it is not 1:
`<speciesReference metaid="CDMT00001" species="s_n1" stoichiometry="2">`. Saving such an edit, CellDesigner gives the
edited `speciesReference` a metaid of its own series (CDMT...) and moves the numbers of its unit definitions up by one;
that numbering is CellDesigner's and is left to it.
The converter reads and writes it in every format: a number labelled on a yEd consumption or production line (the
GraphML maps draw it so, a boxed number), SBGN-ML's `cardinality` glyph of the arc, CellDesigner's stoichiometry other
than 1; written only where one is set, nothing for 1 (CellDesigner holds numbers only). Its box is placed beside the
line near the species, above it (right of a line near upright), past a product's arrowhead.

{% endraw %}
