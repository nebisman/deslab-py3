"""Fault diagnosis toolbox."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

import networkx as nx
from ..src.automatadefs import fsa
from ..src.algorithms import observer
from ..src.def_const import *
from ..src.exceptions import *
from ..src.utilities import _sorted, _tostr


def _failure_event(sf):
    """ the failure event can be passed alone or in a list (set)"""
    if isinstance(sf, list) and sf:
        sf = sf[0]
    elif isinstance(sf, (set, frozenset)) and sf:
        sf = _sorted(sf)[0]
    if sf == epsilon or isinstance(sf, (list, set, frozenset)):
        raise invalidArgument('failure event must be a string or list')
    return sf


def labelfailaut(sf):
    """
    This function creates a label failure automaton
    """
    sf = _failure_event(sf)
    Y, N = 'Y', 'N'
    sigmaA = [sf]
    XA = [Y, N]
    X0A = [N]
    XmA = []
    transitions = [(N, sf, Y), (Y, sf, Y)]
    Al = fsa(XA, sigmaA, transitions, X0A, XmA, Sigobs=EMPTYSET, name='Al')
    return Al


def diagnoser(G, sf=epsilon, Sigma_o=EMPTYSET):
    """
    This function calculates the diagnoser automaton of G for
    the failure event sf. The diagnoser is the observer of G||Al,
    where Al is the label failure automaton, over the observable
    events Sigma_o (by default the observable events of G).

    Example
    -------
    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    X=[x1,x2,x3,x4,x5,x6,x7]
    Sigma=[a,b,c,d,e,sf]
    T=[(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),(x4,d,x4),
       (x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7)]
    G=fsa(X,Sigma,T,[x1],[],Sigobs=[a,b,c,d,e],name='$G$')
    D=diagnoser(G,sf)
    draw(G,D)
    """
    if (Sigma_o == EMPTYSET):  # Sigma_o was not defined
        Sigma_obs = G.Sigobs
    elif isinstance(Sigma_o, (list, set, frozenset)):
        Sigma_obs = frozenset(Sigma_o)
    else:
        raise invalidArgument('Observed set must be of type set, frozenset or list')
    sf = _failure_event(sf)

    def latex(D):
        tex_tab = []
        for xd in D:
            xd_tex = ','.join((G.symDict[x] if x in G.symDict else _tostr(x)) + l
                              for x, l in _sorted(xd))
            xd_tex = r'\{' + xd_tex + r'\}'
            tex_tab.append((xd, xd_tex))
        return dict(tex_tab)

    A = labelfailaut(sf)
    D = observer(G // A, Sigma_obs)
    D = D.setpar(name='Diagnoser', type='diag-normal', table=latex(D))
    return D


def observerdelta(self, Eo=EMPTYSET):
    """
    This function calculates the observer of a deterministic automaton
    G with respect to the observable events Eo (by default the
    observable events of G). The states of the observer whose
    unobservable reach contains a cycle of unobservable events
    receive a selfloop labelled by the event '\\Delta'.
    """
    if Eo != EMPTYSET:
        if isinstance(Eo, (list, set, frozenset)):
            Eobs = frozenset(Eo) & self.Sigma
        else:
            raise invalidArgument('Observable event set must be of type set or list')
    else:
        Eobs = self.Sigobs
    Eunobs = self.Sigma - Eobs

    if self.is_dfa() and (Eobs == self.Sigma):
        return self
    elif not self.is_dfa():
        raise invalidArgument('Automaton passed to this function must be a DFA')

    def convertname(stateObserved):
        nameState = ','.join(str(atomicState) for atomicState in _sorted(stateObserved))
        return r'\{' + nameState + r'\}'

    def unobscycle(stateSet):
        """True if the unobservable transitions between the
        states of stateSet contain a cycle"""
        graph = nx.DiGraph()
        graph.add_nodes_from(stateSet)
        for x in stateSet:
            for _, y, e in self.Graph.out_edges(x, keys=True):
                if e in Eunobs and y in stateSet:
                    graph.add_edge(x, y)
        return not nx.is_directed_acyclic_graph(graph)

    def extended_gamma(setState):
        activeEvents = EMPTYSET
        for state in setState:
            activeEvents = activeEvents | self.Gamma(state)
        return activeEvents & Eobs

    delta = '\\Delta'
    X0obs = self.unobsreach(self.X0, Eobs)
    Xobs = [X0obs]
    Xwaiting = [X0obs]
    transition = []
    existunobsCycle = False
    while Xwaiting != []:
        stateSet = Xwaiting.pop()
        if unobscycle(stateSet):
            transition.append([convertname(stateSet), delta, convertname(stateSet)])
            existunobsCycle = True
        for sigma in _sorted(extended_gamma(stateSet)):
            nextState = self.deltaobs(stateSet, sigma, Eobs)
            if nextState not in Xobs:
                Xobs.append(nextState)
                Xwaiting.append(nextState)
            transition.append([convertname(stateSet), sigma, convertname(nextState)])
    Xobsname = [convertname(observedState) for observedState in Xobs]
    Xmobs = [convertname(observedState) for observedState in Xobs
             if (observedState & self.Xm) != EMPTYSET]

    nameobs = 'Observer of ' + str(self.name)
    if existunobsCycle:
        sigmaD = Eobs | frozenset([delta])
    else:
        sigmaD = Eobs
    auto = fsa(Xobsname, sigmaD, transition, convertname(X0obs), Xmobs, Sigobs=Eobs,
               Sigcon=self.Sigcon, name=nameobs, type='observer')
    auto.style = 'observer'
    auto.direction = 'UD'
    return auto
