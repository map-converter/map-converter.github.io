# Read SBML with its Layout (Level 3 package, or the Level 2 annotation of the same elements) into the map model,
# drawn as the file places it: compartment and species glyphs as boxes, a reaction glyph as a process, its species
# reference glyphs as arcs. Glyph kinds come from SBO terms (SBO below); a species without one is an unspecified
# entity. Colours, outlines and font sizes from Render styles where the file has them. Read only; the rules in
# docs/SBML.md.
import os, re
from lxml import etree
from . import report
from .annotation import to_properties
from .model import Map, Node, Arc
from .sbgnml import colour, urn

RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
# species SBO term -> the map's glyph (SBGN PD), with a unit of information where SBGN draws one
SPECIES = {'0000245': 'Macromolecule', '0000252': 'Macromolecule', '0000289': 'Macromolecule',   # protein; Reactome's sets
           '0000297': 'Complex', '0000253': 'Complex',
           '0000247': 'SimpleChemical', '0000327': 'SimpleChemical', '0000299': 'SimpleChemical', '0000298': 'SimpleChemical',
           '0000354': 'NucleicAcidFeature', '0000250': 'NucleicAcidFeature', '0000251': 'NucleicAcidFeature',
           '0000278': ('NucleicAcidFeature', 'ct:mRNA'), '0000243': ('NucleicAcidFeature', 'ct:gene'),
           '0000291': 'EmptySet', '0000358': 'Phenotype', '0000285': 'UnspecifiedEntity'}
# reaction SBO term -> process glyph, and the SBGN class it is drawn as
REACTION = {'0000397': ('OmittedProcess', None), '0000396': ('UncertainProcess', None),
            '0000177': ('Process', 'association'), '0000180': ('Process', 'dissociation')}
# modifier SBO term or role -> the arc's head
MODIFIER = {'0000013': 'catalysis', '0000020': 'inhibition', '0000459': 'stimulation', '0000461': 'trigger',
            '0000594': 'modulation', '0000019': 'modulation', '0000021': 'stimulation', '0000170': 'stimulation',
            '0000171': 'trigger', '0000169': 'inhibition',
            'modifier': 'modulation', 'activator': 'stimulation', 'inhibitor': 'inhibition'}
PROCESS = 24  # px, a process glyph's side where the reaction glyph gives only a point or a large box
POINT = (60.0, 30.0)  # px, a species given as a point drawn at this size round it
SINK = 20  # px, the least side of a source or sink, drawn as a circle round its glyph's centre (COPASI gives a point, 1 by 1)


def kids(el, name):
    return [c for c in el if isinstance(c.tag, str) and etree.QName(c).localname == name]


def kid(el, name):
    return next(iter(kids(el, name)), None)


def all_(el, name):
    return [c for c in el.iter(etree.Element) if etree.QName(c).localname == name]


def attr(el, k):  # an attribute, with or without the package's prefix (layout:x, x)
    if el is None:
        return None
    for a, v in el.attrib.items():
        if etree.QName(a).localname == k:
            return v
    return None


def sbo(el):
    v = attr(el, 'sboTerm') or ''
    return v[4:] if v.startswith('SBO:') else v


def box(g):
    b = kid(g, 'boundingBox')
    if b is None:
        return None
    p, d = kid(b, 'position'), kid(b, 'dimensions')
    if p is None:
        return None
    f = lambda e, k: float(attr(e, k) or 0)  # no dimensions: a point (MonaLisa's Petri net places)
    return f(p, 'x'), f(p, 'y'), f(d, 'width'), f(d, 'height')


def points(g):
    # a curve's points in order: each segment's start, the last segment's end (Bezier control points not kept)
    c = kid(g, 'curve')
    segs = kids(kid(c, 'listOfCurveSegments'), 'curveSegment') if c is not None and kid(c, 'listOfCurveSegments') is not None else []
    pts = []
    for s in segs:
        for e in (kid(s, 'start'), kid(s, 'end')):
            if e is not None and num(attr(e, 'x')) is not None and num(attr(e, 'y')) is not None:
                p = (float(attr(e, 'x')), float(attr(e, 'y')))
                if not pts or abs(pts[-1][0] - p[0]) > .01 or abs(pts[-1][1] - p[1]) > .01:
                    pts.append(p)
    return pts


def annotations(el):
    # an element's MIRIAM identifiers (bqbiol is, hasVersion) as node properties
    a = kid(el, 'annotation')
    d = next(iter(a.iter('{%s}Description' % RDF)), None) if a is not None else None
    data = {}
    for q in (d if d is not None else []):
        urns = [u for u in (urn(li.get('{%s}resource' % RDF) or '') for li in q.iter('{%s}li' % RDF)) if u]
        if urns and etree.QName(q).localname in ('is', 'hasVersion'):
            data.update(to_properties(etree.QName(q).localname == 'hasVersion', urns))
    return data


def styles(model, lay):
    # Render: glyph id or glyph type -> its style's fill, stroke, stroke-width and font-size, from its first shape
    # where the shape sets them (what is drawn), else from the style's group; the layout's own styles over the global ones
    defs, by_id, by_type = {}, {}, {}
    glob = [e for e in all_(model, 'listOfGlobalRenderInformation')]
    local = [e for e in all_(lay, 'listOfRenderInformation')]
    for ri in glob + local:
        defs.update({attr(c, 'id'): attr(c, 'value') for c in all_(ri, 'colorDefinition')})
        for st in all_(ri, 'style'):
            g = kid(st, 'g')
            if g is None:
                continue
            shape = next((c for c in g if isinstance(c.tag, str)), None)
            v = {k: attr(shape, k) or attr(g, k) for k in ('fill', 'stroke', 'stroke-width', 'font-size')}  # a shape's own over its group's
            v = {k: x for k, x in v.items() if x}
            for i in (attr(st, 'idList') or '').split():
                by_id[i] = v
            for t in (attr(st, 'typeList') or '').split():
                by_type[t.upper()] = v
    return defs, by_id, by_type


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def signs(t):
    # a transition's inputs read from its function terms where the inputs give no sign: id -> 'positive', 'negative' or
    # 'dual', by what each is compared with where the result is reached (= 0 or < 1: negative; = 1 or more: positive)
    out = {}
    for ft in all_(t, 'functionTerm'):
        for a in all_(ft, 'apply'):
            c = [x for x in a if isinstance(x.tag, str)]
            if len(c) != 3 or etree.QName(c[0]).localname not in ('eq', 'geq', 'gt', 'lt', 'leq'):
                continue
            ci = next((x.text.strip() for x in c[1:] if etree.QName(x).localname == 'ci' and x.text), None)
            cn = next((num(x.text) for x in c[1:] if etree.QName(x).localname == 'cn'), None)
            if ci is None or cn is None:
                continue
            op = etree.QName(c[0]).localname
            neg = (op == 'eq' and cn == 0) or (op in ('lt', 'leq') and cn <= 1)
            v = 'negative' if neg else 'positive'
            out[ci] = v if out.get(ci, v) == v else 'dual'
    return out


INFLUENCE = {'positive': 'stimulation', 'negative': 'inhibition'}  # Activity Flow's influences (sbgnml.HEAD); else modulation


def transitions(model, acts, arcs, skipped):
    # SBML-qual transitions as Activity Flow influences, drawn straight from each input's box to each output's: the sign
    # from the input, else from the function terms (signs)
    for t in all_(model, 'transition'):
        tid = attr(t, 'id')
        outs = [attr(o, 'qualitativeSpecies') for o in all_(t, 'output')]
        ins = [(attr(x, 'qualitativeSpecies'), attr(x, 'sign')) for x in all_(t, 'input')]
        read = signs(t)
        if not ins:
            ins = [(i, None) for i in read]
        k = 0
        for q, sign in ins:
            for o in outs:
                if q not in acts or o not in acts:
                    skipped.setdefault('influence to or from a species without a box', []).append(tid); continue
                arcs.append(Arc(id='%s.%d' % (tid, k), source=acts[q], target=acts[o],
                                head=INFLUENCE.get(sign if sign in INFLUENCE else read.get(q), 'modulation')))
                k += 1


def read(path):
    root = etree.parse(path).getroot()
    model = kid(root, 'model')
    layouts = all_(model, 'layout')
    if not layouts:
        raise ValueError('no layout in this SBML file: nothing to draw as the file places it')
    lay = layouts[0]
    if len(layouts) > 1:
        report.say('left out', 'layouts after the first: %d' % (len(layouts) - 1))
    sp = {e.get('id'): e for e in all_(model, 'species')}
    comp = {e.get('id'): e for e in all_(model, 'compartment')}
    meta = {e.get('metaid'): e for e in model.iter(etree.Element) if e.get('metaid')}
    rx = {e.get('id'): e for e in all_(model, 'reaction')}
    qsp = {attr(e, 'id'): e for e in all_(model, 'qualitativeSpecies')}  # SBML-qual: activities, drawn as Activity Flow
    refs = {}  # reaction id -> [(role, species, SBO term, the reference's id)]
    for i, r in rx.items():
        for lst, role in (('listOfReactants', 'substrate'), ('listOfProducts', 'product'), ('listOfModifiers', 'modifier')):
            for s in (kids(kid(r, lst), 'speciesReference') + kids(kid(r, lst), 'modifierSpeciesReference')) if kid(r, lst) is not None else []:
                refs.setdefault(i, []).append((role, s.get('species'), sbo(s), s.get('id')))
    text = {}  # glyph id -> its text glyph's text
    for t in all_(lay, 'textGlyph'):
        g, o = attr(t, 'graphicalObject'), attr(t, 'originOfText')
        e = next((d[o] for d in (sp, comp, rx, qsp) if o in d), None)
        v = attr(t, 'text') or (e.get('name') or e.get('id') if e is not None else None)
        if g and v and g not in text:
            text[g] = v  # 'unset': COPASI's text for a glyph it has no name for
    nodes, arcs, skipped = {}, [], {}
    for g in all_(lay, 'compartmentGlyph'):
        b, c = box(g), comp.get(attr(g, 'compartment'))
        if b is None or not b[2] or not b[3]:
            skipped.setdefault('compartment glyph without a box', []).append(attr(g, 'id')); continue
        nodes[attr(g, 'id')] = Node(id=attr(g, 'id'), kind='Compartment', box=b,
                                    labels=[text.get(attr(g, 'id')) or (c.get('name') or c.get('id') if c is not None else '')],
                                    data=annotations(c) if c is not None else {})
    comps = list(nodes.values())

    def inside(b):  # the smallest compartment glyph holding the box's centre
        cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
        hold = [n for n in comps if n.box[0] <= cx <= n.box[0] + n.box[2] and n.box[1] <= cy <= n.box[1] + n.box[3]]
        return min(hold, key=lambda n: n.box[2] * n.box[3]).id if hold else None

    acts = {}  # a qualitative species' id -> its glyph's id

    def activity(g, q, b):  # an SBML-qual species drawn as an Activity Flow activity (as sbgnml.read draws one)
        i = attr(g, 'id')
        acts.setdefault(attr(q, 'id'), i)
        nodes[i] = Node(id=i, kind='Macromolecule', box=b, parent=inside(b),
                        labels=[(text.get(i) if text.get(i) != 'unset' else None) or attr(q, 'name') or attr(q, 'id')],
                        data=dict(annotations(q), **{'SBGN class': 'biological activity'}))

    for g in all_(lay, 'speciesGlyph'):
        i, ref = attr(g, 'id'), attr(g, 'species')
        if ref in qsp:  # a qualitative species given a species glyph (Path2Models)
            if box(g) is None:
                skipped.setdefault('species glyph without a box', []).append(i)
            else:
                activity(g, qsp[ref], box(g))
            continue
        s = sp.get(ref) if ref else meta.get(attr(g, 'metaidRef'))
        b = box(g)
        if b is None:
            skipped.setdefault('species glyph without a box', []).append(i); continue
        named = ref or attr(g, 'metaidRef')
        sink = s is None and not named and text.get(i, 'unset') == 'unset'  # no species, no text: a source or sink (COPASI)
        if s is None and not sink:
            skipped.setdefault('species glyph naming no species of the model (drawn as an unspecified entity)', []).append(i)
        k = SPECIES.get(sbo(s) if s is not None else '', 'UnspecifiedEntity')
        kind, units = (k, []) if isinstance(k, str) else (k[0], [k[1]])
        if not sink and (b[2] < 1 or b[3] < 1):  # a point: a glyph of the usual size round it
            b = (b[0] - POINT[0] / 2, b[1] - POINT[1] / 2) + POINT
        if sink:
            kind, units = 'EmptySet', []
            if b[2] != b[3] or b[2] < SINK:  # a circle of its own size round the glyph's centre, never a stretched one
                d = max(SINK, min(b[2], b[3]))
                b = (b[0] + b[2] / 2 - d / 2, b[1] + b[3] / 2 - d / 2, d, d)
        nodes[i] = Node(id=i, kind=kind, box=b, units=units, parent=inside(b), species=s.get('id') if s is not None else None,
                        labels=['' if kind == 'EmptySet' else ((text.get(i) if text.get(i) != 'unset' else None) or (s.get('name') or s.get('id') if s is not None else ''))],
                        data=annotations(s) if s is not None else {})
    for g in all_(lay, 'generalGlyph'):  # SBML-qual's boxes (CaSQ, bioLQM): one general glyph per qualitative species
        q = qsp.get(attr(g, 'reference'))
        if q is not None and box(g) is not None:
            activity(g, q, box(g))
    if qsp:
        gone = [i for i in qsp if i not in acts]
        if gone:
            skipped.setdefault('qualitative species without a box', []).extend(gone)
        transitions(model, acts, arcs, skipped)
    if not any(n.kind != 'Compartment' for n in nodes.values()):
        raise ValueError('no species glyph in its layout: nothing to draw')
    cx = [n for n in nodes.values() if n.kind == 'Complex']
    for n in nodes.values():  # a glyph lying within a complex's box is its member (MINERVA draws members as species glyphs)
        x, y, w, h = n.box
        hold = [c for c in cx if c is not n and c.box[0] <= x and c.box[1] <= y and x + w <= c.box[0] + c.box[2]
                and y + h <= c.box[1] + c.box[3] and c.box[2] * c.box[3] > w * h]
        if n.kind != 'Compartment' and hold:
            n.parent = min(hold, key=lambda c: c.box[2] * c.box[3]).id
    drawn_as = {}  # a species' id -> its first glyph
    for n in nodes.values():
        if n.species:
            drawn_as.setdefault(n.species, n.id)
    for g in all_(lay, 'reactionGlyph'):
        i, r = attr(g, 'id'), rx.get(attr(g, 'reaction'))
        pts, b = points(g), box(g)
        ends = [nodes[t] for t in (attr(e, 'speciesGlyph') for e in all_(g, 'speciesReferenceGlyph')) if t in nodes]
        if pts:  # the reaction's own curve: the process at its middle
            x, y = (pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2
        elif b is not None and (b[2] or b[3]):
            x, y = b[0] + b[2] / 2, b[1] + b[3] / 2
        elif b is not None and (b[0] or b[1]):
            x, y = b[0], b[1]
        elif ends:  # no place in the file (a box of 0 by 0 at 0, 0): the middle of the glyphs it joins
            x = sum(n.box[0] + n.box[2] / 2 for n in ends) / len(ends)
            y = sum(n.box[1] + n.box[3] / 2 for n in ends) / len(ends)
            skipped.setdefault('reaction glyph without a place (drawn amid its species)', []).append(i)
        else:
            skipped.setdefault('reaction glyph without a place (its lines with it)', []).append(i); continue
        side = min(b[2], b[3]) if b is not None and 8 <= min(b[2], b[3]) <= 40 else PROCESS
        kind, cls = REACTION.get(sbo(r) if r is not None else '', ('Process', None))
        nodes[i] = Node(id=i, kind=kind, box=(x - side / 2, y - side / 2, side, side), labels=[''],
                        data=dict(annotations(r) if r is not None else {}, **({'SBGN class': cls} if cls else {})))
        used = []
        if not all_(g, 'speciesReferenceGlyph'):  # a reaction glyph with no lines (MonaLisa): its reaction's, drawn straight
            for k, (role, spc, term, _) in enumerate(refs.get(attr(g, 'reaction'), [])):
                t = drawn_as.get(spc)
                if t is None:
                    skipped.setdefault('line to a species with no glyph', []).append('%s.%d' % (i, k)); continue
                head = 'production' if role == 'product' else None if role == 'substrate' else \
                    MODIFIER.get(term) if term in MODIFIER and term != '0000019' else 'modulation'
                s_, t_ = (i, t) if role == 'product' else (t, i)
                arcs.append(Arc(id='%s.%d' % (i, k), source=s_, target=t_, head=head))
        for k, rg in enumerate(all_(g, 'speciesReferenceGlyph')):
            t, aid = attr(rg, 'speciesGlyph'), attr(rg, 'id') or '%s.%d' % (i, k)
            if not t:
                skipped.setdefault('line naming no species glyph', []).append(aid); continue
            if t not in nodes:
                skipped.setdefault('line to a glyph left out', []).append(aid); continue
            # its species reference: by id, else by the species its glyph draws
            # (a species in two roles of one reaction: its glyphs take the references in their order, each once)
            mine = refs.get(attr(g, 'reaction'), [])
            hit = [e for e in mine if e[3] and e[3] == attr(rg, 'speciesReference')] or \
                  [e for e in mine if e[1] == nodes[t].species and e not in used] or \
                  [e for e in mine if e[1] == nodes[t].species]
            ref = hit[0] if hit else None
            used.append(ref)
            role = (attr(rg, 'role') or (ref[0] if ref else '')).lower()
            line = points(rg)
            if len(line) > 1:  # the curve set to run from the species: the specification leaves its direction open
                (cx, cy), d = (nodes[t].box[0] + nodes[t].box[2] / 2, nodes[t].box[1] + nodes[t].box[3] / 2), lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2
                if d(line[-1]) < d(line[0]):
                    line = line[::-1]
            inner = line[1:-1]
            if role in ('substrate', 'sidesubstrate'):
                arcs.append(Arc(id=aid, source=t, target=i, points=inner))
            elif role in ('product', 'sideproduct'):
                arcs.append(Arc(id=aid, source=i, target=t, head='production', points=inner[::-1]))
            else:
                term = ref[2] if ref else ''
                head = MODIFIER.get(term) if term in MODIFIER and term != '0000019' else MODIFIER.get(role, 'modulation')
                arcs.append(Arc(id=aid, source=t, target=i, head=head, points=inner))
    defs, by_id, by_type = styles(model, lay)
    kinds = {'Compartment': 'COMPARTMENTGLYPH'}
    for n in nodes.values():
        st = by_id.get(n.id) or by_type.get(kinds.get(n.kind, 'REACTIONGLYPH' if n.kind.endswith('Process') else 'SPECIESGLYPH')) or by_type.get('ANY') or {}
        if n.kind not in ('Process', 'OmittedProcess', 'UncertainProcess', 'EmptySet'):
            n.fill = colour(st.get('fill'), defs)
        if n.kind == 'Compartment':
            c = colour(st.get('stroke'), defs)
            n.line = c if c not in (None, '#000000') else None
            n.weight = num(st.get('stroke-width'))
    for t in all_(lay, 'textGlyph'):  # a label's font size from its text glyph's style
        g, st = attr(t, 'graphicalObject'), by_id.get(attr(t, 'id')) or by_type.get('TEXTGLYPH') or {}
        if g in nodes and num(st.get('font-size')):
            nodes[g].font = num(st.get('font-size'))
    for a in arcs:
        st = by_id.get(a.id) or by_type.get('SPECIESREFERENCEGLYPH') or {}
        c = colour(st.get('stroke'), defs)
        a.line = c if c not in (None, '#000000') else None
    for g in all_(lay, 'generalGlyph'):
        if attr(g, 'id') not in nodes:
            skipped.setdefault('general glyph', []).append(attr(g, 'id'))
    drawn = {g for g in (attr(e, 'reaction') for e in all_(lay, 'reactionGlyph'))}
    gone = [r for r in rx if r not in drawn]
    if gone:
        skipped.setdefault('reaction without a glyph', []).extend(gone)
    for what, ids in skipped.items():
        report.say('left out', '%s: %d left out (%s)' % (what, len(ids), ', '.join(map(str, ids[:5])) + (' ...' if len(ids) > 5 else '')))
    return Map(name=re.sub(r'\.(sbml|xml)$', '', os.path.basename(path)), nodes=nodes, arcs=arcs)


# Writing: SBML Level 3 Version 1 core with Layout and Render, the map's drawing as its SBGN-ML has it (sbgnml.write:
# glyph boxes, process ports, arc ends and bends) and its meaning from the map's biology (biology.build): one species
# per entity (each source or sink its own), one reaction per process, modifiers by their SBO term. The rules in
# docs/SBML.md, Writing; the specifications in specifications/.
CORE = 'http://www.sbml.org/sbml/level3/version1/core'
LAYOUT = 'http://www.sbml.org/sbml/level3/version1/layout/version1'
RENDER_NS = 'http://www.sbml.org/sbml/level3/version1/render/version1'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
XHTML = 'http://www.w3.org/1999/xhtml'
BQ = 'http://biomodels.net/biology-qualifiers/'
# the map's glyph -> species SBO term (inverse of SPECIES: the term SPECIES reads back as the same glyph)
SBO_OF = {'Macromolecule': '0000245', 'Complex': '0000253', 'SimpleChemical': '0000247', 'NucleicAcidFeature': '0000354',
          'UnspecifiedEntity': '0000285', 'Phenotype': '0000358', 'EmptySet': '0000291', 'SourceAndSink': '0000291',
          'Submap': '0000358'}
UNIT_SBO = {'ct:gene': '0000243', 'ct:mRNA': '0000278'}
PROCESS_SBO = {'process': '0000375', 'omitted process': '0000397', 'uncertain process': '0000396',
               'association': '0000177', 'dissociation': '0000180'}
MODIFIER_SBO = {'catalysis': '0000013', 'inhibition': '0000020', 'stimulation': '0000459',
                'necessary stimulation': '0000461', 'modulation': '0000594'}
ROLE = {'catalysis': 'modifier', 'inhibition': 'inhibitor', 'stimulation': 'activator', 'necessary stimulation': 'activator',
        'modulation': 'modifier'}
SHAPE = {'macromolecule': 'rectangle', 'nucleic acid feature': 'rectangle', 'simple chemical': 'ellipse',
         'source and sink': 'ellipse', 'compartment': 'rectangle'}
RADIUS = {'macromolecule': '10', 'nucleic acid feature': '0', 'compartment': '10'}


def sid(s, used):
    # an SBML SId (letters, digits, underscores, not starting with a digit), unique among those used
    s = re.sub(r'\W', '_', s, flags=re.ASCII)
    s = s if re.match(r'[A-Za-z_]', s) else '_' + s
    k, out = 1, s
    while out in used:
        k += 1; out = '%s_%d' % (s, k)
    used.add(out)
    return out


def write(diagram):
    from .biology import label
    from . import sbgnml
    N, bio = diagram.nodes, diagram.biology
    G = '{%s}' % sbgnml.NS
    sb = etree.fromstring(sbgnml.write(diagram).encode('utf-8'))
    node_of = {sbgnml.xml_id(i): i for i in N}
    glyphs = {g.get('id'): g for g in sb.iter(G + 'glyph')}
    port_of = {p.get('id'): g.get('id') for g in glyphs.values() for p in g.findall(G + 'port')}
    port_at = {p.get('id'): (float(p.get('x')), float(p.get('y'))) for g in glyphs.values() for p in g.findall(G + 'port')}
    cls = lambda gid: glyphs[gid].get('class')
    ann = sbgnml.from_graphml(diagram)
    used = set()
    L, R = '{%s}' % LAYOUT, '{%s}' % RENDER_NS

    root = etree.Element('{%s}sbml' % CORE, nsmap={None: CORE, 'layout': LAYOUT, 'render': RENDER_NS, 'xsi': XSI},
                         level='3', version='1')
    root.set(L + 'required', 'false'); root.set(R + 'required', 'false')
    model = etree.SubElement(root, 'model', id=sid(diagram.name or 'map', used), name=diagram.name or 'map')
    E = lambda parent, tag, **a: etree.SubElement(parent, tag, {k: str(v) for k, v in a.items()})

    # compartments: one per compartment name (biology keys entities by it), 'default' for entities outside any
    comp_ids = {}
    for i, d in N.items():
        if d.kind == 'Compartment' and label(d) not in comp_ids:
            comp_ids[label(d)] = sid('c_' + (label(d) or i), used)
    names = {e.key[0] for e in bio.entities.values()}
    if 'default' in names and 'default' not in comp_ids:
        comp_ids['default'] = sid('default', used)
    lc = E(model, 'listOfCompartments')
    for name, c in comp_ids.items():
        E(lc, 'compartment', id=c, name=name, spatialDimensions='3', size='1', constant='true')

    # species: one per entity; a source or sink drawn several times is several species (SBGN never clones the empty set)
    species_of = {}  # glyph node id -> species id
    ls = E(model, 'listOfSpecies')
    lost = []
    for e in bio.entities.values():
        d = N[e.glyphs[0]]
        groups = [[g] for g in e.glyphs] if d.kind in ('EmptySet', 'SourceAndSink') else [e.glyphs]
        for gs in groups:
            s = sid('s_' + (label(d) or d.kind), used)
            sbo_t = next((UNIT_SBO[u] for u in d.units if u in UNIT_SBO), SBO_OF.get(d.kind, '0000285'))
            el = E(ls, 'species', id=s, name=label(d), compartment=comp_ids.get(e.key[0], comp_ids.get('default', '')),
                   hasOnlySubstanceUnits='false', boundaryCondition='true' if d.kind in ('EmptySet', 'SourceAndSink') else 'false',
                   constant='false', sboTerm='SBO:' + sbo_t)
            extra = ['state variable: %s' % (sv.value + ('@' + sv.variable if sv.variable else '')) for sv in e.state_variables if sv.value] + \
                    ['unit of information: %s' % (('%s:' % u.prefix if u.prefix else '') + u.value) for u in sorted(e.units, key=str)
                     if ('%s:%s' % (u.prefix, u.value)) not in UNIT_SBO] + \
                    (['multimer: %d units' % d.count] if d.count > 1 else []) + (['hypothetical'] if d.dashed else [])
            if extra:
                lost.append(label(d))
                body = etree.SubElement(etree.SubElement(el, 'notes'), '{%s}body' % XHTML, nsmap={None: XHTML})
                for line in extra:
                    etree.SubElement(body, '{%s}p' % XHTML).text = line
            family, urns = ann.get(label(d), (False, []))
            uris = ['http://identifiers.org/%s:%s' % (sbgnml.DB[db], x.replace('%3A', ':').replace('CHEBI:', ''))
                    for db, _, x in (u[len('urn:miriam:'):].rpartition(':') for u in urns) if db in sbgnml.DB]
            if uris:
                el.set('metaid', sid('meta_' + s, used))
                rdf = etree.SubElement(etree.SubElement(el, 'annotation'), '{%s}RDF' % RDF, nsmap={'rdf': RDF, 'bqbiol': BQ})
                desc = etree.SubElement(rdf, '{%s}Description' % RDF, {'{%s}about' % RDF: '#' + el.get('metaid')})
                bag = etree.SubElement(etree.SubElement(desc, '{%s}%s' % (BQ, 'hasVersion' if family else 'is')), '{%s}Bag' % RDF)
                for u in uris:
                    etree.SubElement(bag, '{%s}li' % RDF, {'{%s}resource' % RDF: u})
            for g in gs:
                species_of[g] = s
    if lost:
        report.say('changed', '%d species keep their state variables, units of information or multimer count only in their notes '
                   '(SBML core has no place for them): %s' % (len(lost), ', '.join(sorted(set(lost)))))

    # reactions, from the SBGN-ML arcs at each process glyph
    arcs = list(sb.iter(G + 'arc'))
    ends = lambda a: (port_of.get(a.get('source'), a.get('source')), port_of.get(a.get('target'), a.get('target')))
    ent = lambda gid: species_of.get(node_of.get(gid))
    gates = [g for g in glyphs if cls(g) in ('and', 'or', 'not')]  # in the file's order: the output is the same every run
    lr = E(model, 'listOfReactions') if any(cls(g) in PROCESS_SBO for g in glyphs) else None
    refs = {}  # SBGN-ML arc id -> (species reference id, role, process glyph, the gate's arc to the process or None)
    gate_refs = {}  # gate glyph -> [(species reference id)] of its inputs, as modifiers of the process
    left, reaction_of = [], {}
    for p in (g for g in glyphs if cls(g) in PROCESS_SBO):
        at = [a for a in arcs if p in ends(a)]
        consumed = [a for a in at if a.get('class') == 'consumption']
        rev = not consumed
        r = reaction_of[p] = sid('r_' + node_of.get(p, p), used)
        el = E(lr, 'reaction', id=r, reversible='true' if rev else 'false', fast='false', sboTerm='SBO:' + PROCESS_SBO[cls(p)])
        sides = {'listOfReactants': [], 'listOfProducts': [], 'listOfModifiers': []}
        for a in at:
            s, t = ends(a)
            c = a.get('class')
            if c == 'consumption' and ent(s):
                sides['listOfReactants'].append((a, ent(s), 'substrate', None, None))
            elif c == 'production' and ent(t):
                first = a.get('source', '').endswith('.1')
                side = 'listOfReactants' if rev and first else 'listOfProducts'
                sides[side].append((a, ent(t), 'substrate' if side == 'listOfReactants' else 'product', None, None))
            elif c in MODIFIER_SBO and t == p and ent(s):
                sides['listOfModifiers'].append((a, ent(s), ROLE[c], MODIFIER_SBO[c], None))
            elif c in MODIFIER_SBO and t == p and s in gates:  # each input a modifier, drawn through the gate
                for b in arcs:
                    if ends(b)[1] == s and b.get('class') == 'logic arc' and ent(ends(b)[0]):
                        sides['listOfModifiers'].append((b, ent(ends(b)[0]), ROLE[c], MODIFIER_SBO[c], a))
                left.append('%s gate on %s' % (cls(s).upper(), label(N[node_of[p]]) if node_of.get(p) else p))
        for lst, items in sides.items():
            if not items:
                continue
            le = E(el, lst)
            for a, s, role, term, out in items:
                ref = sid('sr_%s_%s' % (r, s), used)
                if lst == 'listOfModifiers':
                    E(le, 'modifierSpeciesReference', id=ref, species=s, sboTerm='SBO:' + term)
                else:
                    E(le, 'speciesReference', id=ref, species=s, stoichiometry='1', constant='true')
                refs[a.get('id')] = (ref, role, p, out)
    if left:
        report.say('changed', 'logic gates kept as drawings, their inputs as modifiers of the process, drawn through the gate '
                   '(SBML core has no logic gate): %s' % ', '.join(left))
    if lr is not None and not len(lr):
        model.remove(lr)

    # the layout: the SBGN-ML drawing glyph by glyph
    lay = etree.SubElement(etree.SubElement(model, L + 'listOfLayouts'), L + 'layout')
    lay.set(L + 'id', sid('layout', used))
    w = max([float(b.get('x')) + float(b.get('w')) for b in sb.iter(G + 'bbox')] or [0]) + 20
    h = max([float(b.get('y')) + float(b.get('h')) for b in sb.iter(G + 'bbox')] or [0]) + 20
    LE = lambda parent, tag, **a: etree.SubElement(parent, L + tag, {L + k: str(v) for k, v in a.items()})
    LE(lay, 'dimensions', width=repr(w), height=repr(h))

    def bbox(parent, g):
        b = g.find(G + 'bbox')
        bb = LE(parent, 'boundingBox')
        LE(bb, 'position', x=b.get('x'), y=b.get('y'))
        LE(bb, 'dimensions', width=b.get('w'), height=b.get('h'))

    def points_of(a):
        return [(float(e.get('x')), float(e.get('y'))) for e in a if etree.QName(e).localname in ('start', 'next', 'end')]

    def curve(parent, pts):
        segs = LE(LE(parent, 'curve'), 'listOfCurveSegments')
        for p0, p1 in zip(pts, pts[1:]):
            s = LE(segs, 'curveSegment'); s.set('{%s}type' % XSI, 'LineSegment')
            LE(s, 'start', x=repr(p0[0]), y=repr(p0[1])); LE(s, 'end', x=repr(p1[0]), y=repr(p1[1]))

    gid = {}  # SBGN-ML glyph id -> layout glyph id
    lines = {}  # SBGN-ML arc class -> the layout ids of its curves (Render's line styles); 'process': the reaction glyphs
    texts = []  # (layout glyph id, text, SBGN-ML glyph)
    comp_glyphs = [g for g in glyphs if cls(g) == 'compartment']
    if comp_glyphs:
        lcg = LE(lay, 'listOfCompartmentGlyphs')
        for g in comp_glyphs:
            d = N[node_of[g]]
            gid[g] = sid('cg_' + g, used)
            cg = LE(lcg, 'compartmentGlyph', id=gid[g], compartment=comp_ids[label(d)])
            bbox(cg, glyphs[g]); texts.append((gid[g], label(d), glyphs[g], True))
    sp = [g for g in glyphs if node_of.get(g) in species_of]
    if sp:
        lsg = LE(lay, 'listOfSpeciesGlyphs')
        for g in sp:
            gid[g] = sid('sg_' + g, used)
            sg = LE(lsg, 'speciesGlyph', id=gid[g], species=species_of[node_of[g]])
            bbox(sg, glyphs[g])
            if label(N[node_of[g]]):
                texts.append((gid[g], label(N[node_of[g]]), glyphs[g], False))
    procs = [g for g in glyphs if cls(g) in PROCESS_SBO]
    if procs:
        lrg = LE(lay, 'listOfReactionGlyphs')
        for p in procs:
            gid[p] = sid('rg_' + p, used)
            rg = LE(lrg, 'reactionGlyph', id=gid[p], reaction=reaction_of[p])
            ports = [port_at[q.get('id')] for q in glyphs[p].findall(G + 'port')]
            if len(ports) == 2:
                curve(rg, ports)
                lines.setdefault('process', []).append(gid[p])
            else:
                bbox(rg, glyphs[p])
            lsr = None
            for a in arcs:
                if a.get('id') not in refs or refs[a.get('id')][2] != p:
                    continue
                ref, role, _, out = refs[a.get('id')]
                s, t = ends(a)
                other = t if s == p else s
                pts = points_of(a)
                if a.get('class') == 'consumption':
                    pts = pts[::-1]  # from the process to the species (Layout 3.10.1)
                if out is not None:
                    pts = pts + points_of(out)  # a gate's input: on through the gate to the process
                    lines_cls = out.get('class')
                else:
                    lines_cls = a.get('class')
                if lsr is None:
                    lsr = LE(rg, 'listOfSpeciesReferenceGlyphs')
                srg = LE(lsr, 'speciesReferenceGlyph', id=sid('srg_' + a.get('id'), used), speciesReference=ref,
                         speciesGlyph=gid[other], role=role)
                curve(srg, pts)
                lines.setdefault(lines_cls, []).append(srg.get(L + 'id'))
    # logic gates (their box and name; their lines are the modifiers' above) and arcs between entities: general glyphs
    extra = []
    for g in gates:
        gid[g] = sid('gg_' + g, used)
        extra.append(g)
    loose = [a for a in arcs if a.get('id') not in refs and a.get('class') in MODIFIER_SBO
             and not set(ends(a)) & set(gates) and all(e in gid for e in ends(a))]
    if gates or loose:
        lag = LE(lay, 'listOfAdditionalGraphicalObjects')
        for g in gates:
            gg = LE(lag, 'generalGlyph', id=gid[g])
            bbox(gg, glyphs[g]); texts.append((gid[g], cls(g).upper(), glyphs[g], False))
        for a in loose:
            s, t = ends(a)
            pts = points_of(a)
            gg = LE(lag, 'generalGlyph', id=sid('gi_' + a.get('id'), used))
            curve(gg, pts[-1:] * 2)
            lrf = LE(gg, 'listOfReferenceGlyphs')
            rf = LE(lrf, 'referenceGlyph', id=sid('rf_' + a.get('id'), used), glyph=gid[t], role=ROLE.get(a.get('class'), 'modifier'))
            curve(rf, pts)
            lines.setdefault(a.get('class'), []).append(rf.get(L + 'id'))
        if not len(lag):
            lay.remove(lag)
        if loose:
            report.say('changed', '%d arcs between entities kept as drawings only (SBML core has no influence)' % len(loose))
    if texts:
        lt = LE(lay, 'listOfTextGlyphs')
        for g, text, sg, top in texts:
            t = LE(lt, 'textGlyph', id=sid('tg_' + g, used), graphicalObject=g, text=text)
            bbox(t, sg)
            if top:  # a compartment's name: a strip along its top
                t.find('.//' + L + 'dimensions').set(L + 'height', '24')
    order = ['dimensions', 'listOfCompartmentGlyphs', 'listOfSpeciesGlyphs', 'listOfReactionGlyphs', 'listOfTextGlyphs',
             'listOfAdditionalGraphicalObjects']  # the order libSBML writes
    lay[:] = sorted(lay, key=lambda c: order.index(etree.QName(c).localname))
    render(lay, glyphs, gid, {g: N[node_of[g]] for g in gid if g in node_of}, lines, used)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')


# SBGN's arc heads as Render line endings, placed on a curve's end point and turned along it (Render C.1): an
# ending's box from that point, its shapes in it (absolute units or percent of the box)
HEADS_R = {
    'production': ((-10, -5, 10, 10), [('polygon', '#000000', [(0, 0), (10, 5), (0, 10)])]),
    'stimulation': ((-12, -6, 12, 12), [('polygon', '#FFFFFF', [(0, 0), (12, 6), (0, 12)])]),
    'catalysis': ((-10, -5, 10, 10), [('ellipse', '#FFFFFF', None)]),
    'inhibition': ((-2, -8, 2, 16), [('rectangle', '#000000', None)]),
    'necessary stimulation': ((-16, -6, 16, 12), [('polygon', '#000000', [(0, 0), (2, 0), (2, 12), (0, 12)]),
                                                  ('polygon', '#FFFFFF', [(4, 0), (16, 6), (4, 12)])]),
    'modulation': ((-12, -6, 12, 12), [('polygon', '#FFFFFF', [(0, 6), (6, 0), (12, 6), (6, 12)])]),
}


def render(lay, glyphs, gid, nodes, lines, used):
    # Render: a style per glyph that has a colour of its own (a fill; a compartment's outline colour and width), its
    # shape by its SBGN class, every attribute written (Render fixes no defaults: specifications/bergmann-2018.md)
    R = '{%s}' % RENDER_NS
    groups = {}
    for g, lg in gid.items():
        d = nodes.get(g)
        if d is None:
            continue
        c = glyphs[g].get('class')
        key = (d.fill or '#FFFFFF', d.line or '#000000', d.weight or 1, SHAPE.get(c, 'rectangle'), RADIUS.get(c, '0'))
        groups.setdefault(key, []).append(lg)
    if not groups:
        return
    lri = etree.SubElement(lay, R + 'listOfRenderInformation')
    lri.set(R + 'versionMajor', '1'); lri.set(R + 'versionMinor', '0')
    ri = etree.SubElement(lri, R + 'renderInformation')
    ri.set(R + 'id', sid('render', used)); ri.set(R + 'programName', 'map-converter')
    L, X = '{%s}' % LAYOUT, '{%s}' % XSI
    heads = {c: v for c, v in HEADS_R.items() if c in lines}
    if heads:
        le = etree.SubElement(ri, R + 'listOfLineEndings')
        for c, ((x, y, w, h), shapes) in heads.items():
            e = etree.SubElement(le, R + 'lineEnding')
            e.set(R + 'id', 'head_' + c.replace(' ', '_')); e.set(R + 'enableRotationalMapping', 'true')
            bb = etree.SubElement(e, L + 'boundingBox')
            etree.SubElement(bb, L + 'position', {L + 'x': str(x), L + 'y': str(y)})
            etree.SubElement(bb, L + 'dimensions', {L + 'width': str(w), L + 'height': str(h)})
            g = etree.SubElement(e, R + 'g')
            for shape, fill, pts in shapes:
                el = etree.SubElement(g, R + shape, {R + 'stroke': '#000000', R + 'stroke-width': '1', R + 'fill': fill})
                if shape == 'polygon':
                    lo = etree.SubElement(el, R + 'listOfElements')
                    for px, py in pts:
                        etree.SubElement(lo, R + 'element', {X + 'type': 'RenderPoint', R + 'x': str(px), R + 'y': str(py)})
                elif shape == 'ellipse':
                    for a, v in (('cx', '50%'), ('cy', '50%'), ('rx', '50%'), ('ry', '50%')):
                        el.set(R + a, v)
                else:
                    for a, v in (('x', '0'), ('y', '0'), ('width', '100%'), ('height', '100%')):
                        el.set(R + a, v)
    ls = etree.SubElement(ri, R + 'listOfStyles')
    for c, ids in lines.items():  # every curve styled: a strict reader draws an unstyled curve as nothing
        st = etree.SubElement(ls, R + 'style')
        st.set(R + 'id', sid('line_' + c.replace(' ', '_'), used)); st.set(R + 'idList', ' '.join(ids))
        g = etree.SubElement(st, R + 'g', {R + 'stroke': '#000000', R + 'stroke-width': '1', R + 'fill': 'none'})
        if c in heads:
            g.set(R + 'endHead', 'head_' + c.replace(' ', '_'))
    for k, ((fill, stroke, width, shape, radius), ids) in enumerate(groups.items()):
        st = etree.SubElement(ls, R + 'style')
        st.set(R + 'id', sid('style_%d' % (k + 1), used)); st.set(R + 'idList', ' '.join(ids))
        g = etree.SubElement(st, R + 'g')
        for a, v in (('stroke', stroke), ('stroke-width', '%g' % width), ('fill', fill), ('font-family', 'sans-serif'),
                     ('font-size', '10'), ('text-anchor', 'middle'), ('vtext-anchor', 'middle')):
            g.set(R + a, v)
        el = etree.SubElement(g, R + shape)
        if shape == 'ellipse':
            for a, v in (('cx', '50%'), ('cy', '50%'), ('rx', '50%'), ('ry', '50%')):
                el.set(R + a, v)
        else:
            for a, v in (('x', '0'), ('y', '0'), ('width', '100%'), ('height', '100%'), ('rx', radius), ('ry', radius)):
                el.set(R + a, v)
