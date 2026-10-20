"""drawing methods

Automata are rendered with graphviz. Inside Jupyter or Google Colab
notebooks every automaton passed to draw() is displayed inline (SVG)
in the output of the cell. Outside notebooks the figures are written
to an HTML page that is opened in the web browser. If the graphviz
programs are not installed, matplotlib is used as fallback.
"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

import html
import os
import re
import sys
import tempfile
import webbrowser
import warnings
from functools import reduce
import networkx as nx
from ..src.automatadefs import fsa
from ..src.def_const import *
from ..src.exceptions import *
from ..src.utilities import _sorted, _sortkey, _tostr
from .texlabels import latex2html, latex2text

try:
    import graphviz
except ImportError:  # pragma: no cover
    graphviz = None


# colors defined in the LaTeX preambles of the original DESlab
COLORS = {'plantfill': (0.960784, 0.850980, 0.039216),
          'plantline': (0.77647, 0.53725, 0.00000),
          'superfill': (0.54510, 0.88235, 0.15686),
          'superline': (0.227451, 0.486275, 0.054902),
          'specfill': (0.42353, 0.43922, 0.72157),
          'specline': (0.00000, 0.05098, 0.36471),
          'uobsb': (0.10980, 0.30196, 0.94510),
          'uobsg': (0.035294, 0.533333, 0.458824),
          'black': (0, 0, 0), 'white': (1, 1, 1), 'gray': (0.5, 0.5, 0.5),
          'red': (1, 0, 0), 'green': (0, 1, 0), 'blue': (0, 0, 1),
          'cyan': (0, 1, 1), 'magenta': (1, 0, 1), 'yellow': (1, 1, 0),
          'orange': (1, 0.5, 0), 'violet': (0.5, 0, 0.5), 'brown': (0.75, 0.5, 0.25)}
UOBS_COLOR = ['uobsg', 100]
# styles of automata drawn with rectangular states
BOXSTYLES = {'rectangle', 'rectangle3d', 'crectangle', 'verifier', 'diagnoser', 'observer'}
BALLSTYLES = {'normal3d', 'rectangle3d'}
ENGINES = {'dot', 'neato', 'fdp', 'sfdp', 'circo', 'twopi', 'osage', 'patchwork'}
DRAWSTYLES = {'beamer', 'page', 'figure', 'figurecolor'}
FONTNAME = 'Times-Roman'


def xcolor2hex(color):
    """ Converts a color in the xcolor notation of the original
    DESlab, ['plantfill', 76] (76% of plantfill and 24% of white),
    to an hexadecimal string '#rrggbb' """
    if isinstance(color, str):
        if color.startswith('#'):
            return color
        color = [color, 100]
    name, intensity = color
    r, g, b = COLORS.get(name, COLORS['blue'])
    f = max(0.0, min(1.0, float(intensity) / 100.0))
    mix = [f * c + (1.0 - f) for c in (r, g, b)]
    return '#%02x%02x%02x' % tuple(int(round(255 * c)) for c in mix)


def _colors(automaton, style):
    """ line and fill colors used for drawing the automaton"""
    if style == 'figure':
        return '#000000', '#ffffff'
    return xcolor2hex(automaton.LineColor), xcolor2hex(automaton.FillColor)


def _state_label(automaton, x):
    """ latex label of state x """
    if x in automaton.symDict:
        return str(automaton.symDict[x])
    return _tostr(x)


def _event_label(automaton, e):
    """ latex label of event e """
    if e in automaton.symDict:
        return str(automaton.symDict[e])
    return str(e)


def _hlabel(latex, math=True):
    """ graphviz HTML-like label of a LaTeX string """
    body = latex2html(latex, math)
    return '<%s>' % (body if body else ' ')


def _edge_groups(automaton):
    """ The transitions between each pair of states are joined
    in two edges: one for the observable events and other for
    the unobservable ones (drawn dashed)."""
    groups = {}
    for x, y, e in automaton.Graph.edges(keys=True):
        groups.setdefault((x, y), set()).add(e)
    edges = []
    for (x, y) in sorted(groups, key=lambda p: (_sortkey(p[0]), _sortkey(p[1]))):
        events = groups[(x, y)]
        obs = _sorted(events & automaton.Sigobs)
        uobs = _sorted(events - automaton.Sigobs)
        if obs:
            edges.append((x, y, obs, True))
        if uobs:
            edges.append((x, y, uobs, False))
    return edges


def _rankdir(direction):
    return {'UD': 'TB', 'DU': 'BT'}.get(direction, direction if direction in ('LR', 'RL', 'TB', 'BT') else 'LR')


def _check_graphviz():
    if graphviz is None:
        raise deslabError('the python package graphviz is not installed (pip install graphviz)')


def _build_graph(automaton, style='beamer', **options):
    """ Builds the graphviz Digraph of an automaton. It returns the
    graph, the dictionary of node ids of states, and the list of
    edges (x, y, events, observable) indexed by the edge id."""
    _check_graphviz()
    engine = automaton.render if automaton.render in ENGINES else 'dot'
    g = graphviz.Digraph(engine=engine)
    g.attr(rankdir=_rankdir(automaton.direction), nodesep=str(automaton.nodesep),
           ranksep=str(automaton.ranksep), bgcolor='white', pad='0.2',
           fontname=FONTNAME, newrank='true')
    for key in ('size', 'dpi', 'ratio'):
        if key in options:
            g.attr(**{key: str(options[key])})
    if style in ('beamer', 'page') and automaton.name not in ('', 'untitled'):
        g.attr(label=_hlabel(str(automaton.name), math=False), labelloc='t',
               labeljust='c', fontsize='18')
    g.attr('node', fontname=FONTNAME, fontsize='14')
    g.attr('edge', fontname=FONTNAME, fontsize='13', arrowsize='0.7')
    line, fill = _colors(automaton, style)
    if automaton.empty:
        g.node('empty', label='<∅<BR/><FONT POINT-SIZE="11">Empty Automaton</FONT>>',
               shape='box', style='rounded,filled', fillcolor=fill, color=line, penwidth='1.6')
        return g, {}, []
    ids = dict((x, 's%d' % i) for i, x in enumerate(_sorted(automaton.X)))
    box = automaton.style in BOXSTYLES
    for x in _sorted(automaton.X):
        attrs = {'label': _hlabel(_state_label(automaton, x)), 'color': line,
                 'penwidth': '1.6', 'style': 'filled', 'fillcolor': fill}
        if box:
            attrs.update(shape='box', margin='0.1,0.05', height='0.35', width='0.35')
        else:
            attrs.update(shape='circle', margin='0.03', width='0.42', height='0.42')
        if automaton.style in BALLSTYLES:
            attrs.update(style='radial', fillcolor='white:' + fill)
        if x in automaton.Xm:
            attrs.update(peripheries='2')
        g.node(ids[x], **attrs)
        if x in automaton.X0:
            g.node('init_' + ids[x], label='', shape='none', width='0', height='0')
            g.edge('init_' + ids[x], ids[x], penwidth='1.2')
    edges = _edge_groups(automaton)
    uobs_color = xcolor2hex(UOBS_COLOR) if style != 'figure' else '#000000'
    for k, (x, y, events, observable) in enumerate(edges):
        label = ','.join(latex2html(_event_label(automaton, e)) for e in events)
        attrs = {'label': '<%s>' % (label if label else ' '), 'id': 'e%d' % k}
        if not observable:
            attrs.update(style='dashed', color=uobs_color, fontcolor=uobs_color)
        g.edge(ids[x], ids[y], **attrs)
    return g, ids, edges


def automaton2graphviz(automaton, style='beamer', **options):
    """ This function returns the graphviz.Digraph object that
    represents the input automaton. It can be used for customizing
    the figure or saving it with the methods of graphviz.
    style: 'beamer' (colors and title), 'figurecolor' (colors),
    'figure' (black and white)"""
    g, ids, edges = _build_graph(automaton, style, **options)
    return g


def automaton2dot(automaton, style='beamer', **options):
    """ This function creates a dot description
    of the input automaton """
    return automaton2graphviz(automaton, style, **options).source


_SHIFTED_TEXT = re.compile(r'<text([^>]*?) baseline-shift="(sub|super)"([^>]*)>')


def _fix_subscripts(svg):
    """ graphviz writes subscripts and superscripts with the attribute
    baseline-shift, which is not supported by all browsers (Firefox).
    We replace it by an explicit displacement and a smaller font."""
    def replace(match):
        attrs = match.group(1) + match.group(3)
        y = re.search(r' y="(-?[\d.]+)"', attrs)
        size = re.search(r' font-size="([\d.]+)"', attrs)
        if not (y and size):
            return match.group(0)
        fs = float(size.group(1))
        dy = 0.3 * fs if match.group(2) == 'sub' else -0.4 * fs
        attrs = attrs.replace(y.group(0), ' y="%.2f"' % (float(y.group(1)) + dy))
        attrs = attrs.replace(size.group(0), ' font-size="%.2f"' % (0.75 * fs))
        return '<text%s>' % attrs
    return _SHIFTED_TEXT.sub(replace, svg)


def automaton2svg(automaton, style='beamer', **options):
    """ This function returns the SVG image (string) of
    the input automaton """
    g = automaton2graphviz(automaton, style, **options)
    return _fix_subscripts(g.pipe(format='svg', encoding='utf-8'))


def _in_notebook():
    """ True if the code is running inside a Jupyter/Colab notebook"""
    if 'google.colab' in sys.modules:
        return True
    try:
        from IPython import get_ipython
        shell = get_ipython()
    except Exception:
        return False
    if shell is None:
        return False
    if shell.__class__.__name__ in ('ZMQInteractiveShell', 'Shell'):
        return True
    return 'IPKernelApp' in getattr(shell, 'config', {})


def _parse_draw_args(automatavars, style):
    """ draw accepts automata, lists of automata and, as in the
    original version, the style as last string argument"""
    automata = []
    for var in automatavars:
        if isinstance(var, fsa):
            automata.append(var)
        elif isinstance(var, (list, tuple)):
            automata.extend(a for a in var if isinstance(a, fsa))
        elif isinstance(var, str):
            style = var
        else:
            raise invalidArgument('draw only accepts automata, lists of automata and a style string')
    if style is None:
        style = 'beamer'
    if style not in DRAWSTYLES:
        raise invalidArgument('style %s is not defined, use one of %s' % (style, sorted(DRAWSTYLES)))
    return automata, style


def _html_page(svgs, title='DESlab'):
    body = '\n'.join('<div class="fig">%s</div>' % svg for svg in svgs)
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>%s</title>'
            '<style>body{font-family:sans-serif;background:#fff;margin:16px}'
            '.fig{margin:12px 0;padding:8px;border-bottom:1px solid #ddd;overflow-x:auto}'
            '</style></head><body>\n%s\n</body></html>' % (html.escape(title), body))


_fig_counter = [0]


def draw(*automatavars, **options):
    """
    This function draws one or several automata.

    In Jupyter or Google Colab notebooks each automaton is displayed
    inline, below the cell, as an SVG image. Outside notebooks all the
    figures are written to an HTML page that is opened in the web
    browser (use view=False to only create the file).

    draw(G1, G2, ..., style='beamer')

    style : 'beamer'      colors according to the type of automaton
                          and the name as title (default)
            'figurecolor' colors without title
            'figure'      black and white without title
    As in the original version the style can be passed as the last
    argument: draw(G1, G2, 'figure')

    Other options: size='8,5' (maximum size in inches), view=True.

    Example
    -------
    syms('q1 q2 q3 a1 b1 e')
    table = [(a1,'\\alpha_1'),(b1,'\\beta_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
    T =[(q1,b1,q2),(q2,b1,q3),(q2,e,q3),(q3,a1,q1),(q2,a1,q2)]
    G1 = fsa([q1,q2,q3],[a1,b1,e],T,[q1],[q1,q3],table,name='$G_1$ -- example 1')
    draw(G1)
    """
    view = options.pop('view', True)
    automata, style = _parse_draw_args(automatavars, options.pop('style', None))
    if not automata:
        return None
    try:
        svgs = [automaton2svg(automaton, style, **options) for automaton in automata]
    except Exception as error:
        if graphviz is not None and not isinstance(error, graphviz.ExecutableNotFound):
            raise
        warnings.warn('graphviz programs were not found (install them with '
                      '"apt install graphviz" or from graphviz.org), matplotlib is used instead')
        return _draw_matplotlib(automata, style)
    if _in_notebook():
        from IPython.display import display, SVG
        for svg in svgs:
            display(SVG(data=svg))
        return None
    # outside notebooks we create an html page with all figures
    _fig_counter[0] += 1
    outdir = os.path.join(tempfile.gettempdir(), 'deslab')
    os.makedirs(outdir, exist_ok=True)
    filename = os.path.join(outdir, 'Figure-%d.html' % _fig_counter[0])
    with open(filename, 'w', encoding='utf-8') as fileobj:
        fileobj.write(_html_page(svgs))
    if view:
        webbrowser.open('file://' + filename)
    return filename


def savefig(automaton, filename, style='figurecolor', **options):
    """
    This function saves the figure of the automaton in a file.
    The format is given by the extension of filename: pdf, png,
    svg, jpg, gif, dot (graphviz source) or tex (TikZ code).

    Example
    -------
    savefig(G1, 'G1.pdf')
    savefig(G1, 'G1.png', style='figure', dpi=200)
    """
    ext = os.path.splitext(filename)[1].lstrip('.').lower()
    if ext == 'tex':
        from .tikz import automaton2tikz
        with open(filename, 'w', encoding='utf-8') as fileobj:
            fileobj.write(automaton2tikz(automaton, style))
        return filename
    g = automaton2graphviz(automaton, style, **options)
    if ext in ('dot', 'gv', 'svg'):
        with open(filename, 'w', encoding='utf-8') as fileobj:
            fileobj.write(g.source if ext != 'svg' else automaton2svg(automaton, style, **options))
        return filename
    if ext not in ('pdf', 'png', 'svg', 'jpg', 'jpeg', 'gif', 'eps', 'ps'):
        raise invalidArgument('format %s is not supported' % ext)
    return g.render(outfile=filename, format=ext, cleanup=True)


def _layers(automaton):
    """ distance of each state from the initial states (used
    for the matplotlib layout)"""
    dist = nx.multi_source_dijkstra_path_length(automaton.Graph, list(automaton.X0)) \
        if automaton.X0 else {}
    last = max(dist.values()) + 1 if dist else 0
    return dict((x, dist.get(x, last)) for x in automaton.X)


def _draw_matplotlib(automata, style):
    """ simple drawing of automata with matplotlib, used when
    the graphviz programs are not available"""
    import matplotlib.pyplot as plt
    figures = []
    for automaton in automata:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.set_axis_off()
        if style in ('beamer', 'page'):
            ax.set_title(latex2text(str(automaton.name), math=False))
        figures.append(fig)
        if automaton.empty:
            ax.text(0.5, 0.5, '∅  Empty Automaton', ha='center', va='center')
            continue
        line, fill = _colors(automaton, style)
        graph = nx.DiGraph()
        layer = _layers(automaton)
        for x in _sorted(automaton.X):
            graph.add_node(x, layer=layer[x])
        labels = {}
        for x, y, events, observable in _edge_groups(automaton):
            text = ','.join(latex2text(_event_label(automaton, e)) for e in events)
            if graph.has_edge(x, y):
                text = labels[(x, y)] + ' | ' + text
            graph.add_edge(x, y)
            labels[(x, y)] = text
        pos = nx.multipartite_layout(graph, subset_key='layer')
        if automaton.direction == 'UD':
            pos = dict((x, (p[1], -p[0])) for x, p in pos.items())
        xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 0.4, max(xs) + 0.3)
        ax.set_ylim(min(ys) - 0.5, max(ys) + 0.5)
        marked = [x for x in graph if x in automaton.Xm]
        nx.draw_networkx_nodes(graph, pos, nodelist=marked, node_size=1100, node_color='white',
                               edgecolors=line, linewidths=1.5, ax=ax)
        nx.draw_networkx_nodes(graph, pos, node_size=700, node_color=fill,
                               edgecolors=line, linewidths=1.5, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax, labels=dict(
            (x, latex2text(_state_label(automaton, x))) for x in graph))
        nx.draw_networkx_edges(graph, pos, ax=ax, node_size=900, arrows=True,
                               connectionstyle='arc3,rad=0.15')
        try:
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, ax=ax,
                                         connectionstyle='arc3,rad=0.15')
        except TypeError:  # old networkx versions
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, ax=ax)
        for x0 in automaton.X0:
            px, py = pos[x0]
            ax.annotate('', xy=(px, py), xytext=(px - 0.25, py),
                        arrowprops=dict(arrowstyle='->', shrinkB=14, color='black'))
    import matplotlib
    if _in_notebook() or 'agg' not in matplotlib.get_backend().lower():
        plt.show()
    return None


""" The following functions draw networkx graphs whose nodes are
 labelled with the structures used in the diagnosis algorithms"""


def label_digraph(graph, type):

    def latex_D(xd):
        xd_tex = []
        for x, l in xd:
            xd_tex.append(str(x) + l)
        xd_tex = reduce(lambda i, j: i + ',' + j, (t for t in xd_tex))
        xd_tex = r'\{' + xd_tex + r'\}'
        return xd_tex

    def latex(n):
        if type == 'lex':
            if len(n) == 0:
                name = '\\epsilon'
            else:
                name = reduce(lambda x, y: x + y, (i for i in n))
                name = name.replace(epsilon, '')
            return name

        elif type == 'lex-label':
            if n[0] == ():
                name = '(\\epsilon,' + n[1] + ')'
            else:
                name = '(' + reduce(lambda x, y: x + y, (i for i in n[0])) + ',' + n[1] + ')'
            return name

        elif type == 'lex-cycle':
            if graph.in_degree(n) == 0:
                return '(' + str(n[0]) + ',' + '\\epsilon' + ')'
            if len(n) == 2:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + str(n[0]) + ',' + pref + ')'
            elif len(n) == 3:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                if pref == epsilon:
                    pref = pref.replace(epsilon, '\\epsilon ')
                else:
                    pref = pref.replace(epsilon, '')
                name = '(' + str(n[0]) + ',' + pref + ',' + reduce(lambda x, y: x + y, (i for i in n[2])) + ')'
            return name

        elif type == 'FPES' or type == 'XDS':
            if graph.in_degree(n) == 0:
                return '(' + latex_D(n[0]) + ',' + '\\epsilon' + ')'
            if len(n) == 2:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0]) + ',' + pref + ')'
            elif len(n) == 3:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0]) + ',' + pref + ',' + reduce(lambda x, y: x + y, (i for i in n[2])) + ')'
            return name

        elif type == 'lex-Gd-G':
            if graph.in_degree(n) == 0:
                return '(' + latex_D(n[0][0]) + ',' + str(n[0][1]) + ',' + '\\epsilon' + ')'
            if len(n) == 2:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0][0]) + ',' + str(n[0][1]) + ',' + pref + ')'
            elif len(n) == 3:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0][0]) + ',' + str(n[0][1]) + ',' + pref + ',' + reduce(lambda x, y: x + y, (i for i in n[2])) + ')'
            return name

        elif type == 'XST':
            if graph.in_degree(n) == 0:
                return '(' + latex_D(n[0][0]) + ',' + latex_D(n[0][1]) + ',' + '\\epsilon' + ')'
            if len(n) == 2:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0][0]) + ',' + latex_D(n[0][1]) + ',' + pref + ')'
            elif len(n) == 3:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0][0]) + ',' + latex_D(n[0][1]) + ',' + pref + ',' + reduce(lambda x, y: x + y, (i for i in n[2])) + ')'
            elif len(n) == 4:
                pref = reduce(lambda x, y: x + y, (i for i in n[1]))
                pref = pref.replace(epsilon, '')
                name = '(' + latex_D(n[0][0]) + ',' + latex_D(n[0][1]) + ',' + pref + ',' + reduce(lambda x, y: x + y, (i for i in n[2])) + ',' + str(n[3]) + ')'
            return name

        # any other graph: the label is the string of the node
        return _tostr(n)

    s = iter(range(len(graph)))
    ren = dict([(n, 's' + str(next(s))) for n in graph])
    graph_label = nx.DiGraph()
    for n in graph.nodes():
        if graph.out_degree(n) == 0:
            style_n = 'leaf'
        elif n == ():
            style_n = 'circle'
        else:
            style_n = 'rectangle'
        graph_label.add_node(ren[n], label=latex(n), style=style_n)
    for n1, n2 in graph.edges():
        graph_label.add_edge(ren[n1], ren[n2])
    return graph_label


def drawgraph(graph, type='lex', nodesep=0.25, ranksep=0.2, direction='LR',
              LineColor=['blue', 60], FillColor=['blue', 15]):
    """ This function draws a networkx graph. The labels of the nodes
    are built according to type ('lex', 'lex-label', 'lex-cycle', 'FPES',
    'XDS', 'lex-Gd-G', 'XST' or None for the string of each node)"""
    _check_graphviz()
    graph_label = label_digraph(graph, type)
    g = graphviz.Digraph()
    g.attr(rankdir=_rankdir(direction), nodesep=str(nodesep), ranksep=str(ranksep),
           bgcolor='white', fontname=FONTNAME)
    g.attr('node', fontname=FONTNAME, fontsize='14', color=xcolor2hex(LineColor),
           penwidth='1.4', style='filled', fillcolor=xcolor2hex(FillColor))
    g.attr('edge', arrowsize='0.7')
    for n, data in graph_label.nodes(data=True):
        shape = {'circle': 'circle', 'leaf': 'ellipse'}.get(data['style'], 'box')
        attrs = {'label': _hlabel(data['label']), 'shape': shape}
        if data['style'] == 'leaf':
            attrs['fillcolor'] = xcolor2hex(['plantfill', 50])
        g.node(n, **attrs)
    for n1, n2 in graph_label.edges():
        g.edge(n1, n2)
    svg = _fix_subscripts(g.pipe(format='svg', encoding='utf-8'))
    if _in_notebook():
        from IPython.display import display, SVG
        display(SVG(data=svg))
        return None
    _fig_counter[0] += 1
    outdir = os.path.join(tempfile.gettempdir(), 'deslab')
    os.makedirs(outdir, exist_ok=True)
    filename = os.path.join(outdir, 'Graph-%d.html' % _fig_counter[0])
    with open(filename, 'w', encoding='utf-8') as fileobj:
        fileobj.write(_html_page([svg]))
    webbrowser.open('file://' + filename)
    return filename
