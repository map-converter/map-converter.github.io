---
layout: converter-docs
title: "Design decisions"
permalink: /converter/docs/decisions/
sitemap: false
noindex: true
---
{% raw %}

Open design questions of the converter, one per session (user, 2026-10-24). Each entry: the question,
what is known, the options, status. When decided, the decision goes where it belongs (CLAUDE.md,
PLANNED.md, the docs of the format) and the entry says where.

## Criteria for a decision (draft, 2026-10-24; to discuss in a session of its own)

The user asked for words to judge whether a decision makes the converter better, more efficient, or too
rigid to develop. Draft list, each as a question:
- Simplicity: does it remove code, parameters, special cases, or add them?
- Locality (coupling): does a change stay in one module, or do other rules depend on it?
- Reversibility: can it be undone later without remaking files or breaking what users made with it?
- Idempotence (stability): applied twice, is the result the same as once? (No drift over round trips.)
- Fidelity: does what the user drew survive the conversion, and is every change said in the messages?
- Predictability: can a user tell what the output will be from the input and the rule?
- Evolvability (extensibility): does a new target, a new map or a new rule fit without changing this one?
- Robustness: does it hold on maps not seen yet, and on files edited afterwards in the other program?
- Lock-in: does it tie the converter to one program's behaviour, or to one map?
- Cost of being wrong: if it proves wrong, how much is lost (files, user's edits) and how is it found?

## Points to discuss, one per session

Settled 2026-10-24 (user): 1. the tidy module removed, 2. the process glyph by hidden edit points,
over 3 px, 3. no node moved, multimers as dimers with N:x, 4. a hidden point under the node, 5. no
default left to choose ([D14](/converter/docs/design/#d14-no-node-moved-the-process-glyph-and-ports-by-hidden-edit-points),
[D15](/converter/docs/design/#d15-multimers-drawn-as-dimers-the-count-as-a-unit)).

6. Complex name room (PLANNED.md): grow the complex, or move its members.

7. Species on a compartment's edge (2026-10-28, ExposomeMap-PM; ISSUES.md, Known faults). CellDesigner draws a
   membrane protein across its compartment's border, a member of the compartment; yEd draws a group round all its
   members, and the GraphML check refuses a member outside its group, so the trip CellDesigner > GraphML >
   CellDesigner loses it and its reactions. Options: (a) the check accepts a member whose box overlaps its
   compartment (on the membrane), yEd's group grows a little on opening; (b) CellDesigner to GraphML makes such a
   species a top-level node and keeps the compartment as a node property, read back to CellDesigner; (c) the
   species moved inside, against "no node moved". Proposed: (a), the smallest; it keeps membership and
   position, and the growth is the known fault already listed.

8. Reduced notation to SBGN-ML (user, 2026-11-13). Now: an arc between two entities (CellDesigner's reduced
   notation, the same drawn in yEd) is written into the Process Description file as a stimulation, inhibition,
   modulation or trigger from entity to entity, dashed ones with "unknown" in the arc's notes. The XSD accepts it,
   Newt draws it, our reader reads it back; libsbgn's PD rules flag it (SREBP), as PD takes a modulation only on
   a process. Nothing is lost, but the file is not valid PD. A map in reduced notation only would be fully
   Activity Flow: every entity an activity (rectangle) with a unit of information for what it is (macromolecule,
   simple chemical, complex, nucleic acid feature, unspecified entity), the arcs positive, negative or unknown
   influence and necessary stimulation, gates and phenotypes as they are; the mapping is the one MINERVA
   discussed for its AF view (its issue 486), the reverse of our AF reader (SBGNML.md).
   Elsewhere: cd2sbgnml (Balaur et al. 2020, used by Newt) writes PD only and says losing reactions of one kind is
   unavoidable for mixed maps; MINERVA's SBGN-ML export has had issues of reduced arcs refused as invalid arc
   types and of modifier reactions to phenotypes turned into processes (its issues 1320, 1445; not read, the
   tracker blocks automated reads). MINERVA's current output not checked: a test would send a small file of ours
   to its convert API.
   Options: (a) keep as now; (b) leave the arcs out (the map loses its regulation, against "as little changed as
   possible"); (c) a reduced-only map written as Activity Flow, a mixed map as now; (d) a mixed map as Newt's
   hybrid, an activity beside each entity that has reduced arcs (our reader already folds it back); (e) a mixed
   map as two files, PD and AF. Proposed: (c), the AF writer being the reverse of the reader; (b) not.
   Priority (user, 2026-11-13): low. The pipeline is GraphML, CellDesigner and MINERVA (maps to MINERVA); SBGN-ML
   is a side branch, so (a) stays until SBGN output is needed.
   MINERVA's output (2026-11-13, from its SBGN-ML of SREBP of 2026-11-10, kept in the workbench's F005-srebp/minerva/):
   the same as ours. Language process description, the two REDUCED_PHYSICAL_STIMULATION reactions written as
   stimulation arcs from entity to entity, one from a protein to a phenotype, one from a phenotype to a phenotype (which
   our converter leaves out, SBGNML.md). No Activity Flow, no process made, nothing dropped. The other kept exports
   (glycogen, iNOS, eNOS, estrogen, BCAA, nNOS) have no reduced arcs; inhibition, modulation, trigger and dashed types
   are untested. A live test of those (the small files in tests/celldesigner/) was refused on 2026-11-13: the instance
   answered 418 "Request Rejected" to every call, as for some minutes on 2026-11-10 after many calls; a temporary
   block, not a lasting one (the convert API worked from cloud sessions before, without login, notes/minerva-api.md
   in the workbench).

9. Logic gates in SBGN-ML (user, 2026-11-14). The spec gives a logic gate two ports, as a process: the incoming
   logic arcs go to one end, the outgoing arc leaves from the other. Our SBGN-ML gives gates ports but draws their arcs
   straight from centre to centre (rule of 2026-10-18), and our yEd maps draw a gate without antennas. Decided for now
   (user): keep it, knowing it is not strict SBGN ("we kind of have to stick to official SBGN rules ... otherwise,
   community will not accept it"); to be forced later. Open: the antenna length; that Newt breaks this rule on
   purpose for layout's sake (with antennas a good layout is harder to keep).
10. Phenotype and perturbing agent (user, 2026-11-14). In SBGN PD a phenotype takes incoming arcs only (it points
    to a result); a perturbing agent (ultraviolet light, an outside influence) has outgoing arcs only, to a process.
    CellDesigner has neither as such, and our maps use its phenotype for several things, submaps among them, so an
    arc leaving a phenotype is left out of SBGN-ML now (2026-10-17). Other groups' SBGN-ML maps draw both properly and
    must be shown as drawn: the perturbing agent then needs a glyph of our own in the yEd palette's place (the palette
    seems to have none). Open, problem by problem with the external maps.
    Decided (user, 2026-11-14: "we can read it, we can show it. This is enough. For conversion, it's a different matter
    ... during conversion, after conversion. But for now, it's okay"): reading and showing done (yEd's PerturbingAgent
    and the node property "SBGN class", drawn by yrender as SBGN's glyph). A file converted from SBGN-ML into our
    formats takes our maps' conventions: a perturbing agent becomes a phenotype in GraphML and CellDesigner, and a
    submap a phenotype too in place of yEd's rectangle (CellDesigner does both already: its phenotype); tags are left
    out where they stand alone, with no submap (they are now everywhere, so nothing changes). Not built: the drawing
    route (the viewer) and the conversion would then part on these glyphs; for later, on the user's word.

{% endraw %}
