"""Networkx common operations."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    MIT license (see LICENSE).

import networkx as nx
from .automatadefs import fsa


def _graph(G):
    """returns the networkx graph of an automaton or graph G"""
    if isinstance(G, fsa):
        return G.Graph
    return G


def strconncomps(G):
    """This function returns the list of strongly connected components
    (sets of states) in the graph of automaton G"""
    return [set(c) for c in nx.strongly_connected_components(_graph(G))]


def selfloopnodes(G):
    """ This function looks for nodes with self loops in the graph of
    automaton G """
    return list(nx.nodes_with_selfloops(_graph(G)))
