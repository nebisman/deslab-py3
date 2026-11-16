"""Networkx common operations."""
#    DESLab v2 Copyright (C) 2026 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Mateo Rodríguez <atarodriguezper@unal.edu.co>
#    Edgar Sepulveda <ehsepulvedao@unal.edu.co>
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
