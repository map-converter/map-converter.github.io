---
layout: converter-docs
title: "Messages"
permalink: /converter/docs/messages/
sitemap: false
noindex: true
---
{% raw %}

Every conversion says what it did in a list of messages, shown under the map on the Converter page
and printed on the command line. Each message has a kind (`mapconv/report.py`):

| Kind | Meaning | Example |
|---|---|---|
| problem | A rule of SBGN the map breaks, found by the check before conversion. The element is left out and drawn red in GraphML (marked). | a production arrow points away from its process |
| left out | Something the output format cannot hold, not converted. | clone marker: 8 left out |
| changed | Moved, joined or written another way. | compartments *a*, *b*: moved *n* px apart, so that Newt does not overlap them |
| warning | Converted, worth a look. | *process*: the arc from *modifier* runs through *node* |
| summary | What a written file holds. | *map*: *n* species, *n* proteins, *n* reactions |
| check | The count check found a difference between the input and the file made that no other message explains. Red on the Converter page. | count check, catalysis: 3 in the input, 2 in the output, not explained by a message |

On the Converter page the messages are grouped by the files they come from, the files named over each
group as on their buttons. The messages of several files come first, then those of each file alone.

What a file loses always appears as `left out`. A loss that is not in the messages is a bug.

## The count check

After each file is made in another format, its input and the file are counted from their XML, by kind: entities by
class (each drawn instance, with its name: proteins, simple chemicals, nucleic acid features, unspecified entities,
phenotypes; complexes and sources by number), compartments, processes, logic gates, consumption and production arcs
together (a reversible process draws its reactants as products), modifier arcs by type and logic arcs. The count reads
the files on its own, not through the converter's readers, so a lost arc or two nodes merged show up as a difference.

A difference that another message of the same file names (a `left out` line for a loss, a `changed` line that joins,
splits or rewrites) is listed as a summary ending "as said above"; one that no message names is a `check` message,
shown in red. A CellDesigner file is also checked for its two layers: a reaction whose reactants, products or modifiers
differ between the SBML core (what MINERVA and SBML tools read) and the CellDesigner annotation (what CellDesigner
reads) is a `check` message. Not counted: GraphML (marked), GraphML (corrected) and GraphML (standard sizes), in the
input's own format; SBGN-ML (for Newt), beside SBGN-ML; SBML-qual, another model. An SBML file is counted by its
glyphs, entities and compartments only. CellDesigner has no tag, so a submap's terminals are not counted there.

{% endraw %}
