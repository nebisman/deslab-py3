"""
DESlab graphics: inline drawing of automata (graphviz) and
optional export to LaTeX/TikZ.
"""
#    DESLab v2 Copyright (C) 2026 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Mateo Rodríguez <atarodriguezper@unal.edu.co>
#    Edgar Sepulveda <ehsepulvedao@unal.edu.co>
#    MIT license (see LICENSE).

from .drawing import *
from .tikz import automaton2tikz, drawlatex
from .texlabels import latex2html, latex2text
