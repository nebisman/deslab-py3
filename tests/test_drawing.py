import os
import shutil
import pytest
from deslab import *
from deslab.graphics import drawing
from deslab.graphics.texlabels import latex2html, latex2text

needs_dot = pytest.mark.skipif(shutil.which('dot') is None, reason='graphviz is not installed')


def example():
    syms('q1 q2 q3 a1 b1 e')
    table = [(a1, '\\alpha_1'), (b1, '\\beta_1'), (q1, 'q_1'), (q2, 'q_2'), (q3, 'q_3')]
    T = [(q1, b1, q2), (q2, b1, q3), (q2, e, q3), (q3, a1, q1), (q2, a1, q2)]
    return fsa([q1, q2, q3], [a1, b1, e], T, [q1], [q1, q3], table, Sigobs=[a1, b1],
               name='$G_1$ -- example 1')


def test_texlabels():
    assert latex2html('q_1') == 'q<SUB>1</SUB>'
    assert latex2html('\\alpha_{12}') == 'α<SUB>12</SUB>'
    assert latex2html(r'\{x_1,x_2\}') == '{x<SUB>1</SUB>,x<SUB>2</SUB>}'
    assert latex2html('$G_1$ -- example 1', math=False) == 'G<SUB>1</SUB> – example 1'
    assert latex2html('K^{\\uparrow C}') == 'K<SUP>↑C</SUP>'
    assert latex2html('a<b & c') == 'a&lt;b&amp;c'
    assert latex2html('$G_1 \\| G_2$', math=False) == 'G<SUB>1</SUB>‖G<SUB>2</SUB>'
    assert latex2text('\\sigma_f') == 'σ_f'
    assert latex2text('x_1') == 'x₁'
    assert latex2text('\\varepsilon') == 'ε'


def test_dot_source():
    src = automaton2dot(example())
    assert 'q<SUB>1</SUB>' in src and 'peripheries=2' in src
    assert 'style=dashed' in src  # unobservable event e
    assert 'G<SUB>1</SUB>' in src  # title
    assert 'label=' not in automaton2dot(example(), 'figure').split('\n')[1]


@needs_dot
def test_svg_and_repr():
    G = example()
    svg = automaton2svg(G)
    assert svg.lstrip().startswith('<?xml') and '<svg' in svg
    assert G._repr_svg_() is not None
    assert '<svg' in automaton2svg(fsa())


@needs_dot
def test_draw_inline_in_notebook(monkeypatch):
    shown = []
    import IPython.display
    monkeypatch.setattr(drawing, '_in_notebook', lambda: True)
    monkeypatch.setattr(IPython.display, 'display', lambda obj: shown.append(obj))
    G = example()
    assert draw(G, observer(G), ~G) is None
    assert len(shown) == 3
    assert all(isinstance(obj, IPython.display.SVG) for obj in shown)
    draw([G, G], 'figure')
    assert len(shown) == 5


@needs_dot
def test_draw_outside_notebook(monkeypatch):
    opened = []
    monkeypatch.setattr(drawing.webbrowser, 'open', lambda url: opened.append(url))
    G = example()
    filename = draw(G, observer(G), style='figurecolor')
    assert os.path.exists(filename) and opened == ['file://' + filename]
    with open(filename, encoding='utf-8') as fileobj:
        assert fileobj.read().count('<svg') == 2
    with pytest.raises(invalidArgument):
        draw(G, style='nostyle')


@needs_dot
@pytest.mark.parametrize('ext', ['svg', 'png', 'pdf', 'dot', 'tex'])
def test_savefig(tmp_path, ext):
    fn = str(tmp_path / ('G.' + ext))
    savefig(example(), fn)
    assert os.path.getsize(fn) > 0


@needs_dot
def test_tikz():
    code = automaton2tikz(example())
    assert code.startswith('\\begin{tikzpicture}')
    assert '\\node[state,initial,accepting] (s0)' in code
    assert 'densely dashed,uobsg' in code and '{$\\alpha_1$}' in code


@needs_dot
@pytest.mark.skipif(shutil.which('pdflatex') is None, reason='pdflatex is not installed')
@pytest.mark.parametrize('style', ['beamer', 'figure'])
def test_drawlatex(tmp_path, style):
    G = example()
    pdf = drawlatex(G, observer(G), fsa(), style=style, filename=str(tmp_path / 'figs'))
    assert pdf.endswith('.pdf') and os.path.exists(pdf)


def test_matplotlib_fallback(monkeypatch):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    monkeypatch.setattr(drawing, '_in_notebook', lambda: False)
    G = example()
    drawing._draw_matplotlib([G, observer(G), fsa()], 'beamer')
    assert len(plt.get_fignums()) == 3
    plt.close('all')


@needs_dot
def test_drawgraph(monkeypatch):
    shown = []
    import IPython.display
    monkeypatch.setattr(drawing, '_in_notebook', lambda: True)
    monkeypatch.setattr(IPython.display, 'display', lambda obj: shown.append(obj))
    import networkx as nx
    graph = nx.DiGraph([((), ('a',)), (('a',), ('a', 'b'))])
    drawgraph(graph, type='lex')
    assert len(shown) == 1
