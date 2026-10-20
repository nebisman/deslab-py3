"""
DESlab
========

    DESlab a scientific computing program written in python
    for the development of algorithms for analysis and synthesis
    of discrete event systems (DES) modeled as automata.
    The main objective of DESlab is to provide a unified tool
    that integrates automata, graph algorithms, and numerical
    calculations. DESlab also allows the definition of symbolic
    variables of type automaton and incorporates concise
    instructions to manipulate, operate, analyze and visualize
    these variables, with a syntax and an abstraction level close
    to the notation used in DES theory

    This version runs on Python 3 with current versions of
    networkx and graphviz. In Jupyter and Google Colab notebooks
    the automata are drawn inline.

    http://www.dee.ufrj.br/controle_automatico/

Using
-----

    Just write in Python

    >>> from deslab import *
    >>> syms('q1 q2 q3 a1 b1 e')
    >>> table = [(a1,'\\alpha_1'),(b1,'\\beta_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
    >>> X = [q1,q2,q3]
    >>> Sigma = [a1,b1,e]
    >>> X0 = [q1]
    >>> Xm = [q1,q3]
    >>> T =[(q1,b1,q2),(q2,b1,q3),(q2,e,q3),(q3,a1,q1),(q2,a1,q2)]
    >>> G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
    >>> draw(G1)
"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    MIT license (see LICENSE).

from .version import __version__, __author__

# adding source code
from . import src
from .src.automatadefs import *
from .src.utilities import *
from .src.exceptions import *
from .src.algorithms import *
from .src.structure import *
from .src.comparison import *
from .src.graphs import *

# adding graphics
from . import graphics
from .graphics.drawing import *
from .graphics.tikz import automaton2tikz, drawlatex

# adding toolboxes
from . import toolboxes
from .toolboxes.diagnosis import *
from .toolboxes.supervisory import *

# adding readwrite
from . import readwrite
from .readwrite.inputoutput import *
