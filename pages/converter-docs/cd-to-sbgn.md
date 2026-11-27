---
layout: converter-docs
title: "CellDesigner to SBGN PD (yEd): the rule table"
permalink: /converter/docs/cd-to-sbgn/
sitemap: false
noindex: true
---
{% raw %}

Rules for the backward direction (CellDesigner -> GraphML). Implemented in `celldesigner.read` +
`graphml.write` (`python3 -m mapconv <map.xml> <out.graphml>`), for the CellDesigner files the converter
writes (as a round trip) and for CellDesigner's own files: the PD map (autumn 2025 version, 41 files)
reads without error. Branched reactions (association, dissociation, truncation) become one
process where CellDesigner draws its glyph: midway on segment tShapeIndex of the single arm (from the
branch point to the product of an association, from the reactant to the branch point of a
dissociation). The branch point: the last edit point in the frame of the three species (origin
the first, axes to the other two), each branch's edit points (num0, num1, num2) in the frame
branch point -> its species (cd2sbgnml, AssociationReactionModel); the two other branches run
through it to the process. Logic gates on reduced arcs
are BOOLEAN_LOGIC_GATE reactions (inputs as base reactants, the gate at the edit point,
absolute; GateMember list) both ways; CellDesigner has no gate feeding a gate. Inhibition
between entities: NEGATIVE_INFLUENCE (forward); modulation and trigger between entities:
REDUCED_MODULATION, REDUCED_TRIGGER (forward, so they come back as they went). From a
gate only stimulation and inhibition (a CellDesigner file with a gate's trigger would settle more). Not yet: binding regions and gene/RNA regions
(see Species), edit points of added reactant/product links (drawn straight), closeup compartments.
Checked against small test files saved in CellDesigner: a reversible reaction is marked only by
leaving out reversible="false" (both ways); yEd draws an omitted or uncertain process
as its Process labelled \\ or ? (no glyph of its own; read and written so, CellDesigner
KNOWN_TRANSITION_OMITTED, UNKNOWN_TRANSITION); unspecified entity template from a test file.
Dashed (unknown) arcs: UNKNOWN_CATALYSIS, UNKNOWN_INHIBITION, UNKNOWN_NEGATIVE_INFLUENCE; others
written solid with a note. Dashed border: hypothetical. Stimulation between entities stays
PHYSICAL_STIMULATION, the triangle (closest to SBGN; POSITIVE_INFLUENCE is an open arrow). Seeded from
**cd2sbgnml** (github.com/sbgn/cd2sbgnml, commit a35eff8: `model/ReactantModel.java`,
`model/Process.java`, `model/LinkModel.java`, `CD2SBGNML.java`, wiki page "Limitations"),
the CellDesigner <-> SBGN-ML converter by Ludovic Roy (Institut Curie)
(Balaur et al. 2020). Where the forward converter (`celldesigner.py`) already
decides a case, the table follows it, so a round trip comes back unchanged.

Coverage test: CellDesigner's own component sheet (`docs/components44-overview.png`; its
CellDesigner file `components44.xml` ships with cd2sbgnml in `samples/`) holds every glyph
CellDesigner 4.4 can draw: 13 classes, 4 protein types, 20 reaction types, 13 modifier types,
gene/RNA regions, hypothetical and active species, layers. Every element on it must convert
or give a warning.

Columns: **CellDesigner** element, **cd2sbgnml** (what it writes in SBGN-ML), **rule**
for the yEd maps (the choices behind it at the end). The yEd glyph names
are those of the yEd SBGN palette (`model.py` kinds).

## Species

| CellDesigner | cd2sbgnml | rule |
|---|---|---|
| PROTEIN, generic | macromolecule | Macromolecule |
| PROTEIN, receptor | macromolecule + unit of information "receptor" | **Macromolecule** |
| PROTEIN, ion channel | macromolecule + unit "ion channel", state variable "open"/"closed" (CellDesigner active/inactive) | **Macromolecule + state variable "open"/"closed"** |
| PROTEIN, truncated | macromolecule + unit "truncated" | **Macromolecule** |
| GENE | nucleic acid feature | NucleicAcidFeature + unit "ct:gene" (the maps' form) |
| RNA | nucleic acid feature + unit "RNA" | NucleicAcidFeature + unit "ct:mRNA" (the maps' form) |
| ANTISENSE_RNA | nucleic acid feature + unit "asRNA" | NucleicAcidFeature + unit "ct:asRNA" |
| SIMPLE_MOLECULE | simple chemical | SimpleChemical |
| ION | simple chemical | **SimpleChemical** |
| DRUG | simple chemical + unit "drug" | **SimpleChemical, white fill** to tell it apart |
| UNKNOWN | unspecified entity | UnspecifiedEntity |
| COMPLEX | complex | Complex, members inside |
| PHENOTYPE | phenotype | **Phenotype**; with the note line `SBGN class: submap` (or `perturbing agent`) yEd's Submap (or PerturbingAgent), the node property SBGN class kept. Nothing is guessed from the arcs |
| DEGRADED | source and sink | SourceAndSink |
| homodimer N | "... multimer" + unit "N:N" | the glyph as multimer + unit "N:N" (the maps' form) |
| hypothetical species (dashed border) | | **the glyph with a dashed border**, and a warning |
| active species (dotted outer border, "activated") | | **state variable "active"** |
| complex in brief view (members hidden) | complex | Complex with its members (from the species), drawn as in usual view |
| PROTEIN residue, binding region | state variable / unit | residue: state variable; **binding region: unit of information with its name** |
| GENE/RNA regions: modification site, coding region, regulatory region, transcription starting site | | modification site: state variable; **others: unit of information with the name** |

## States and units

| CellDesigner | cd2sbgnml | rule |
|---|---|---|
| modification residue, state phosphorylated, acetylated, ubiquitinated, methylated, hydroxylated, glycosylated, myristoylated, palmytoylated, prenylated, protonated, sulfated, don't care, unknown | state variable P, Ac, Ub, Me, OH, G, My, Pa, Pr, H, S, *, ? | the same symbols, placed at the residue's angle on the border (inverse of `border_angle`) |
| residue, state empty | empty state variable | empty state variable |
| structural state (free text: cAMP, active, Su) | state variable with that text | state variable with that text (the maps' bound-ligand and free-text form) |
| info unit ("ct:gene" etc.) | unit of information | unit of information, same text |

## Reactions (the process glyph)

| CellDesigner | cd2sbgnml | rule |
|---|---|---|
| STATE_TRANSITION | process | Process |
| KNOWN_TRANSITION_OMITTED | omitted process | OmittedProcess |
| UNKNOWN_TRANSITION | uncertain process | UncertainProcess |
| TRANSPORT (translocation) | process | Process |
| TRANSCRIPTION | process | Process |
| TRANSLATION | process | Process |
| HETERODIMER_ASSOCIATION | association | **Process** (the maps use no association or dissociation glyphs) |
| DISSOCIATION | dissociation | **Process** |
| TRUNCATION | dissociation (Limitations page) | **Process** |
| reactants, products, added reactant/product links | consumption, production | consumption, production arcs |
| homodimer formation (STATE_TRANSITION to a multimer), degradation (to DEGRADED) | process | Process; nothing special |
| bidirectional reaction (reversible="true", arrows on both ends) | production on both sides | production on both sides |
| reversible="true" without a consumption side | production on both sides | production on both sides (the forward rule, inverted) |

## Modifiers (arcs into a process)

| CellDesigner | cd2sbgnml | rule |
|---|---|---|
| CATALYSIS | catalysis | catalysis |
| UNKNOWN_CATALYSIS | catalysis | **catalysis, dashed** |
| INHIBITION | inhibition | inhibition |
| UNKNOWN_INHIBITION | inhibition | **inhibition, dashed** |
| PHYSICAL_STIMULATION | stimulation | stimulation |
| MODULATION | modulation | modulation |
| TRIGGER | necessary stimulation | necessary stimulation (trigger) |
| TRANSCRIPTIONAL_ACTIVATION, TRANSLATIONAL_ACTIVATION | production (marked TODO in cd2sbgnml) | **stimulation** |
| TRANSCRIPTIONAL_INHIBITION, TRANSLATIONAL_INHIBITION | production (TODO) | **inhibition** |
| BOOLEAN_LOGIC_GATE_AND, _OR, _NOT | logic operator + logic arcs | Operator AND/OR/NOT + logic arcs (the forward rule, inverted) |
| BOOLEAN_LOGIC_GATE_UNKNOWN | gate dropped, its inputs go straight to the process (Limitations page) | GraphML: Operator **?**; SBGN-ML: the gate and its arcs left out, with a message (no SBGN glyph) |

## Reduced notation (arcs between entities, no process)

cd2sbgnml writes them as arcs straight from entity to entity, which SBGN PD does not allow
(an Activity Flow idea inside a PD map). **They are kept as in CellDesigner**, entity
to entity: not a one-language map, but nothing is lost and the way back is possible. The forward converter writes one such case:
a yEd stimulation arc between two entities becomes PHYSICAL_STIMULATION in reduced notation
(SREBP, ACLY).

Geometry: such an arc starts and ends at the ports CellDesigner names (`linkAnchor` of its
base reactant and product) and its bends come from its edit points in the frame between those two points, as a
reaction's main line ([CellDesigner files](/converter/docs/celldesigner/)). A frame between the node
centres would shift every bend and break the shared lanes of a map drawn with them (ExposomeMap-PM: 280 of 492
segments level or upright, as CellDesigner draws them, against 15 with such a frame).

| CellDesigner | cd2sbgnml | rule |
|---|---|---|
| POSITIVE_INFLUENCE, UNKNOWN_POSITIVE_INFLUENCE | stimulation, entity to entity | stimulation arc, entity to entity (UNKNOWN_: dashed, as unknown catalysis) |
| NEGATIVE_INFLUENCE, UNKNOWN_NEGATIVE_INFLUENCE | inhibition, entity to entity | inhibition arc, entity to entity (UNKNOWN_: dashed, as unknown catalysis) |
| REDUCED_PHYSICAL_STIMULATION (+ UNKNOWN_) | stimulation | stimulation arc (UNKNOWN_: dashed, as unknown catalysis) |
| REDUCED_MODULATION (+ UNKNOWN_) | modulation | modulation arc (UNKNOWN_: dashed, as unknown catalysis) |
| REDUCED_TRIGGER (+ UNKNOWN_) | necessary stimulation | trigger arc (UNKNOWN_: dashed, as unknown catalysis) |
| a link pointing at another link | omitted (Limitations page) | omitted, with a warning |
| logic gate on a reduced arc (trigger 1 AND trigger 2 -> B) | logic arcs | Operator + logic arcs, then the reduced arc from the operator |
| a reduced arc ending on a reduced arc (c inhibits A -> B) | omitted | omitted, with a warning |

## Compartments, geometry

| CellDesigner | rule |
|---|---|
| compartment alias (SQUARE, OVAL) | yEd group node with the name; outline in the paint, fill the band's colour, the paint at alpha 63 over white |
| closeup compartments (SQUARE_CLOSEUP_*: a border line, no box) | a warning; drawn as a box to the map's edge | 
| alias bounds | node box (metabolite circles back to the yEd size, centre kept; multimers shrink 6 per unit beyond 2: inverse of the forward rules) |
| reaction | Process 18 x 18 (the maps' size) where CellDesigner draws the process glyph: midway on the main line's segment `rectangleIndex` |
| edit points of a reaction or modifier | yEd bends (sharp, as CellDesigner draws them; within 3 px of one line aligned on it), from the edit point frame (inverse of `cd_layout.to_frame`); a modifier's frame ends at the point of the process glyph `targetLineIndex` names (side middle, 5 px beside the centre, or corner) |
| arc ends | node centres (ports 0,0; CellDesigner's quarter ports only place the process glyph); advanced: ports as ports, a modifier at the point of the 18 px process `targetLineIndex` names (corners at 9, 9, side middles at 0, 9 across the flow) |
| MIRIAM annotation | node properties as `mapconv.annotate` writes them (HGNC symbol, HGNC, UniProt, ChEBI; a family's Members and Member annotation) |
| references on a reaction (`isDescribedBy`, bqbiol or bqmodel: PubMed, DOI, PMC, Reactome) | the process glyph's node property References, `prefix:id` separated by spaces (`pubmed:27260166 doi:10.1016/j.jaci.2020.12.155`); back to CellDesigner as `bqmodel:isDescribedBy`, one bag each |

## Not converted

| CellDesigner | rule |
|---|---|
| layers (free text, lines, shapes, layer comments) | left out, with a warning listing them; empty layers (CellDesigner's default two) say nothing |
| style variation (gradient fill, line width) | left out: the yEd style |
| colours of species | kept as fill (as the forward direction); a transparent one (alpha 00, or six digits, which CellDesigner reads as alpha 00) as no fill; an unknown species without an outline, as CellDesigner draws it |
| references on a reaction drawn as an arc (reduced notation, influences, a logic gate between entities) | left out, with a message naming the reactions: an arc holds no properties |
| reaction annotation other than `isDescribedBy` (`bqmodel:is` with a PMID, Reactome `hasVersion`) | left out, no message yet |
| species identifiers other than HGNC, HGNC symbol, UniProt, ChEBI (Entrez, Ensembl, RefSeq, InChI, PubChem, GO), and links under qualifiers that do not name the species (`isDescribedBy`) | kept as read in the node property Identifiers, written back to every format |
| species notes (MINERVA's Name, Synonyms, Charge text) | left out but for a family's lines (`annotation.from_notes`) |
| line colours | left out: the yEd style; a compartment's outline in its paint |
| font sizes (a 30 pt title on a 12 pt map) | kept, each species' own; CellDesigner has none for state variables and units, which get the converter's (10) |

## The forward direction (GraphML -> CellDesigner) stays with the maps' symbols

Going from GraphML to CellDesigner never brings back CellDesigner's extra
kinds (receptor, ion channel, truncated, transport, association, ion, drug class...): the maps'
glyphs are written as CellDesigner's plain ones (generic protein, state transition, simple
molecule). The backward direction is a one-way normalisation of those kinds onto the maps' set.
Only arcs between entities (reduced notation) need CellDesigner's reduced types, for maps
that mix Activity Flow into Process Description. One SBGN stimulation arc in yEd stands
for both POSITIVE_INFLUENCE and REDUCED_PHYSICAL_STIMULATION in CellDesigner; written back as
REDUCED_PHYSICAL_STIMULATION, the SBGN arrowhead ([CellDesigner files](/converter/docs/celldesigner/)). Rules, not training: the
converter needs one example of each case (the component sheet has them) and real mixed maps
only to check against.

## Choices behind the table

- Receptor, ion channel, truncated protein: a plain macromolecule (cd2sbgnml adds a unit of information
  naming the kind, so it survives a round trip back to CellDesigner).
- A truncated protein (a fragment such as CDK5R1 (p25)) is another entity than its full protein, though both carry
  one identifier: it gets the unit not drawn "truncated" (the node property Unit of information, a notes line in
  SBGN-ML and CellDesigner), so it is never merged with the full protein.
- Ion channel open/closed: a state variable, as in cd2sbgnml.
- ION and DRUG: simple chemical, a drug told apart by a white fill (cd2sbgnml adds a "drug" unit); the drug
  maps (aspirin) draw drugs as plain simple chemicals.
- Phenotype comes back as Phenotype, unless its notes say `SBGN class: submap` or `perturbing agent` (written by this converter).
- Truncation: a plain Process with the truncated protein as product (cd2sbgnml: Dissociation).
- Unknown catalysis and inhibition (dashed in CellDesigner): the arc dashed in yEd, to keep the "unknown".
- Transcriptional and translational activation and inhibition: stimulation and inhibition arcs (cd2sbgnml
  leaves a TODO).
- Reduced notation: the entity-to-entity arcs kept (as cd2sbgnml, and as the forward converter for
  stimulation), not drawn through an added omitted process and not left out.
- Hypothetical species (dashed border in CellDesigner): dashed border in yEd, and a warning.
- Active species ("activated", dotted outer border): a state variable "active", as the maps mark activity.
- Protein binding regions and gene/RNA regions (coding, regulatory, transcription starting site): units
  of information with the region's name. Modification sites become state variables in any case.

## Known faults, not fixed yet

Found on the PD map
submaps in `tests/external/pd-map/submaps/` and AsthmaMap's PD02 in `tests/external/asthmap/submaps/`:

- **Added links in a branched reaction lose their bends**: "edit points of an added link left out". Elsewhere an added
  link's edit points are read (CELLDESIGNER.md, Added link's edit points); the writer writes added links straight.
- **SBGN-ML writer stops on a family member without an HGNC symbol** (pd-autophagy):
  `annotation.miriam` reads `p['HGNC symbol']`, KeyError. The website's converter page fails
  the same way on this file (CellDesigner -> SBGN-ML). Fix: a member without the symbol gives
  only the identifiers it has.

{% endraw %}
