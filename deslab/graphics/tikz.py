"""
Export of automata to LaTeX (TikZ). The layout is computed by
graphviz and the figures use the TikZ automata library, as the
figures produced by the original DESlab. This is optional: the
draw() function displays the automata inline in notebooks and
does not need LaTeX.
"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

import json
import os
import shutil
import subprocess
from ..src.exceptions import *
from .drawing import _build_graph, _state_label, _event_label

TEXFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texfiles')
BEAMERPREAMBLE = 'BeamerPreamble.tex'
FIGUREPREAMBLE = 'FigurePreamble.tex'

# shapes of the states for each style of automaton (original DESlab)
SHAPES = {'normal': ('circle', ''),
          'rectangle': ('minimum height=0mm,inner sep=2mm,rectangle', ''),
          'normal3d': ('ball color={fill},circle', ''),
          'rectangle3d': ('ball color={fill},rectangle', ''),
          'crectangle': ('chamfered rectangle', ''),
          'verifier': ('minimum height = 7.5mm,rectangle', 'initial where=above'),
          'diagnoser': ('inner xsep=2pt,inner ysep=0pt,rectangle', 'initial where=above'),
          'observer': ('minimum height=0mm,inner sep=2.0mm,rectangle', 'initial where=above'),
          'vertical': ('circle', 'initial where=above')}

# macro that reduces the figures that do not fit in a beamer frame
FITMACRO = r"""\newsavebox{\deslabbox}
\newcommand{\deslabfit}[1]{%
  \savebox{\deslabbox}{#1}%
  \ifdim\wd\deslabbox>\linewidth\savebox{\deslabbox}{\resizebox{\linewidth}{!}{\usebox{\deslabbox}}}\fi
  \ifdim\ht\deslabbox>0.75\textheight\savebox{\deslabbox}{\resizebox{!}{0.75\textheight}{\usebox{\deslabbox}}}\fi
  \usebox{\deslabbox}}
"""


def _xcolor(color, style):
    if style == 'figure':
        return None
    name, intensity = color
    return '%s!%s' % (name, intensity)


def _point(p):
    x, y = p.split(',')[:2]
    return '(%sbp,%sbp)' % (x, y)


def _bezier(pos, tail, head):
    """ TikZ path of a graphviz spline 'e,x,y p1 p2 ... pn'. As in
    dot2tex the first and last points are replaced by the nodes"""
    points = [p for p in pos.split() if not p.startswith(('e,', 's,'))]
    path = '(%s)' % tail
    segments = points[1:]
    for k in range(0, len(segments) - 2, 3):
        c1, c2, end = segments[k:k + 3]
        last = k + 3 >= len(segments) - 2
        path += ' ..controls %s and %s .. %s' % (_point(c1), _point(c2),
                                                  '(%s)' % head if last else _point(end))
    return path


def automaton2tikz(automaton, style='figurecolor'):
    """ This function returns the TikZ code (a tikzpicture
    environment) of the input automaton. It needs the LaTeX
    packages tikz and xcolor and the tikz library automata
    (see the preambles in deslab/graphics/texfiles).
    style: 'figurecolor' or 'figure' (black and white)"""
    if automaton.empty:
        return ('\\begin{tikzpicture}\n\\node[draw,rectangle,rounded corners] '
                '{$\\emptyset$ \\textsc{Empty Automaton}};\n\\end{tikzpicture}\n')
    g, ids, edges = _build_graph(automaton, 'figurecolor')
    layout = json.loads(g.pipe(format='json0', encoding='utf-8'))
    objects = dict((o['_gvid'], o) for o in layout.get('objects', []))
    states = dict((v, k) for k, v in ids.items())
    line = _xcolor(automaton.LineColor, style) or 'black!100'
    fill = _xcolor(automaton.FillColor, style) or 'white!100'
    shape, initpos = SHAPES.get(automaton.style, ('circle', ''))
    if automaton.direction == 'UD':
        initpos = 'initial where=above'
    options = ["scale=%s" % automaton.scale, ">=stealth'", 'line join=bevel',
               'line width=0.75pt', 'initial text=']
    if initpos:
        options.append(initpos)
    options.append('every state/.style={%s,draw=%s,very thick,fill=%s}'
                   % (shape.format(fill=fill), line, fill))
    code = ['\\begin{tikzpicture}[%s]' % ',\n  '.join(options)]
    for obj in objects.values():
        x = states.get(obj['name'])
        if x is None:
            continue
        keys = ['state']
        if x in automaton.X0:
            keys.append('initial')
        if x in automaton.Xm:
            keys.append('accepting')
        code.append('  \\node[%s] (%s) at %s {$%s$};' % (
            ','.join(keys), obj['name'], _point(obj['pos']), _state_label(automaton, x)))
    uobs = None if style == 'figure' else 'uobsg'
    for edge in layout.get('edges', []):
        eid = edge.get('id', '')
        if not eid.startswith('e'):
            continue
        x, y, events, observable = edges[int(eid[1:])]
        tail, head = objects[edge['tail']]['name'], objects[edge['head']]['name']
        attrs = '->' if observable else '->,densely dashed' + (',' + uobs if uobs else '')
        code.append('  \\draw [%s] %s;' % (attrs, _bezier(edge['pos'], tail, head)))
        label = ','.join(_event_label(automaton, e) for e in events)
        if 'lp' in edge:
            color = '' if (observable or not uobs) else '[text=%s]' % uobs
            code.append('  \\draw %s node%s {$%s$};' % (_point(edge['lp']), color, label))
    code.append('\\end{tikzpicture}')
    return '\n'.join(code) + '\n'


def _preamble(name):
    with open(os.path.join(TEXFILES, name), encoding='utf-8') as fileobj:
        return fileobj.read()


def drawlatex(*automatavars, **options):
    """
    This function writes a LaTeX document with the figures of the
    automata (TikZ) and, if pdflatex is installed, compiles it.
    It reproduces the PDF output of the original DESlab.

    drawlatex(G1, G2, style='beamer', filename='deslab_figures', compile=True)

    style : 'beamer' (one frame per automaton with its name as title),
            'figurecolor' or 'figure' (one page per figure, tight)
    It returns the name of the pdf file (or of the tex file if it
    was not compiled).
    """
    from .drawing import _parse_draw_args
    filename = options.pop('filename', 'deslab_figures')
    compile_tex = options.pop('compile', True)
    automata, style = _parse_draw_args(automatavars, options.pop('style', None))
    if style == 'page':
        style = 'beamer'
    texname = os.path.splitext(filename)[0] + '.tex'
    if style == 'beamer':
        preamble = _preamble(BEAMERPREAMBLE).replace('\\begin{document}', FITMACRO + '\\begin{document}')
        body = []
        for automaton in automata:
            body.append('\\begin{frame}\n\\frametitle{%s}\n\\begin{center}\n\\deslabfit{%%\n%s}\n'
                        '\\end{center}\n\\end{frame}\n' % (automaton.name, automaton2tikz(automaton, 'figurecolor')))
    else:
        preamble = _preamble(FIGUREPREAMBLE)
        body = [automaton2tikz(automaton, style) + '\\newpage\n' for automaton in automata]
    with open(texname, 'w', encoding='utf-8') as fileobj:
        fileobj.write(preamble + '\n' + ''.join(body) + '\\end{document}\n')
    if not compile_tex:
        return texname
    if shutil.which('pdflatex') is None:
        raise deslabError('pdflatex was not found, the file %s was written but not compiled' % texname)
    outdir = os.path.dirname(os.path.abspath(texname))
    subprocess.run(['pdflatex', '-interaction=batchmode', '-no-shell-escape',
                    os.path.basename(texname)], cwd=outdir, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    pdfname = os.path.splitext(texname)[0] + '.pdf'
    if not os.path.exists(pdfname):
        raise deslabError('pdflatex could not compile %s, see the .log file' % texname)
    return pdfname
