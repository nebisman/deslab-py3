"""
Automaton structure manipulation functions for the automata objects.
The purpose of these methods is to provide low lovel access to an
automaton object.
"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

import networkx as nx
from .def_const import *
from .exceptions import *
from .utilities import _sorted


def addtransition(self, trans):
    """
    This method provides low level access to the transition
    structure of the input automaton. By using this method, user
    can add a new transition (x,e,y) to the automaton G.
    The states x, y, and the event e are automatically added
    if they are not already present in the automaton G.
    The output is directed to a different object than G.

    Example
    --------

    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    S = [a,b,c,d,e,sf]
    X=[x1,x2,x3,x4,x5,x6,x7]
    X0=[x1]
    Xm=[x2,x4]
    T=[(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),(x4,d,x4),
       (x1,a,x5),(x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7)]
    tab=[(x1,'x_1'),(x2,'x_2'),(sf,'\\sigma_f')]
    G=fsa(X,S,T,X0,Xm,tab)

    # call it as follows
    G1=G.addtransition([x1,b,x2])

    # or alternatively
    G1=addtransition(G,[x1,b,x2])
    """
    try:
        x, e, y = trans
    except (TypeError, ValueError):
        raise invalidArgument('transition must be a list of the form [x,e,y] or (x,e,y)')
    if self.empty:
        raise invalidAutomaton('transitions can not be added to the empty automaton')
    # making a local copy of the input automaton
    auto = self.copy()
    # Case states x or y of transition are not already in X
    for state in (x, y):
        if state not in auto.X:
            auto.X = auto.X | frozenset([state])
            auto.Graph.add_node(state)
    # Case event e of transition is not already in Sigma
    if e not in auto.Sigma:
        auto.Sigma = auto.Sigma | frozenset([e])
        auto.Sigobs = auto.Sigobs | (frozenset([e]) - EMPTYSTRINGSET)
        auto.Sigcon = auto.Sigcon | frozenset([e])
    # it could be an existing transition
    if not auto.Graph.has_edge(x, y, key=e):
        auto.Graph.add_edge(x, y, key=e, label=e)
    auto._rebuild()
    return auto


def deletetransition(self, trans):
    """
    This method provides low level access to the transition
    structure of input automaton. By using this method, user
    can delete an existing transition in the automaton G. If
    the transition does not exist in G, the method raises an
    exception.

    Example
    -------
    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    S = [a,b,c,d,e,sf]
    X = [x1,x2,x3,x4,x5,x6,x7]
    X0 = [x1]
    Xm = [x2,x4]
    T= [(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),(x4,d,x4),
        (x1,a,x5),(x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7)]
    tab = [(x1,'x_1'),(x2,'x_2'),(sf,'\\sigma_f')]
    G = fsa(X,S,T,X0,Xm,tab)

    # call it as follows:
    G1 = G.deletetransition([x1,c,x2])
    G1 = G.deletetransition((x1,c,x2))

    # or alternatively:
    G1 = deletetransition(G,[x1,c,x2])
    """
    try:
        # only is valid a triple in list or tuple form
        x, e, y = trans
    except (TypeError, ValueError):
        raise invalidArgument('transition must be a list of the form [x,e,y] or (x,e,y)')
    if not self.Graph.has_edge(x, y, key=e):
        # case it does not exist
        raise invalidTransition('transition %s does not exist in G' % (str(trans)))
    # local copy of input automaton
    auto = self.copy()
    auto.Graph.remove_edge(x, y, key=e)
    auto._rebuild()
    return auto


def renamevents(self, mapping):
    """
    This function renames the events of the input automaton
    according to the input mapping.
    The input mapping is a list or tuples as follows:
    mapping = [(old_e1, new_ e1),(old_e2,new_e2),...]

    or it can be used a dictionary as follows
    mapping = {old_e1: new_e1, old_e2: new_e2,...}.

    The renamed events keep their observability and
    controllability properties.

    Example
    --------
    syms('x1 x12 x123 x0 xnot1 x0new a b')
    e1,e2,e3 ='1','2','3'
    X1=[x0,x1,x12,x123,xnot1]
    S=[e1,e2,e3]
    T = [(x0,e1,x1),(x0,e2,xnot1),(x0,e3,xnot1),(x1,e1,x1),(x1,e2,x12),(x1,e3,xnot1),
         (x12,e1,x1),(x12,e2,xnot1),(x12,e3,x123),(x123,e1,x1),(x123,e2,xnot1),
         (x123,e3,xnot1),(xnot1,e1,x1),(xnot1,e2,xnot1),(xnot1,e3,xnot1)]
    X0=[x0]
    Xm=[x123]
    G1=fsa(X1,S,T,X0,Xm,name='$G_1$')
    map=[(e1,a),(e2,b)]

    # call it as follows
    G2=G1.renamevents(map)

    # or alternatively
    G2=renamevents(G1, map)
    """
    # only dictionaries or lists are allowed
    if isinstance(mapping, list):
        mapping = dict(mapping)
    if not isinstance(mapping, dict):
        raise invalidArgument('Mapping must be a list of relations or dictionary')
    # we make a copy of input automaton
    auto = self.copy()
    ren = lambda e: mapping.get(e, e)
    # we rebuild the graph with the renamed transitions
    Graph = nx.MultiDiGraph()
    Graph.add_nodes_from(auto.Graph.nodes(data=True))
    for x, y, e in auto.Graph.edges(keys=True):
        if not Graph.has_edge(x, y, key=ren(e)):
            Graph.add_edge(x, y, key=ren(e), label=ren(e))
    auto.Graph = Graph
    # updating the symbolic dictionary
    for e in mapping:
        if e in auto.symDict:
            del auto.symDict[e]
    # updating Sigma, observable and controllable events
    auto.Sigma = frozenset(ren(e) for e in auto.Sigma)
    auto.Sigobs = frozenset(ren(e) for e in auto.Sigobs) - EMPTYSTRINGSET
    auto.Sigcon = frozenset(ren(e) for e in auto.Sigcon)
    if epsilon in auto.Sigma:
        auto.symDict[epsilon] = '\\varepsilon'
    auto._rebuild()
    return auto


def renamestates(self, mapping):
    """
    This function renames the states of the input automaton
    according to the input mapping.
    The input mapping is a list or tuples as follows:
    mapping = [(old_x1, new_ x1),(old_x2,new_x2),...]

    or it can be used a dictionary as follows
    mapping = {old_x1: new_x1, old_x2: new_x2,...}.

    The strings 'number' and 'letter' generate automatic
    mappings (see buildmapping).

    Example
    -------

    syms('x1 x12 x123 x0 xnot1 x0new  y1 y3 y12 y123 y0')
    e1,e2,e3 = 1,2,3
    X1=[x0,x1,x12,x123,xnot1]
    S=[e1,e2,e3]
    T = [(x0,e1,x1),(x0,e2,xnot1),(x0,e3,xnot1),(x1,e1,x1),(x1,e2,x12),(x1,e3,xnot1),
         (x12,e1,x1),(x12,e2,xnot1),(x12,e3,x123),(x123,e1,x1),(x123,e2,xnot1),
         (x123,e3,xnot1),(xnot1,e1,x1),(xnot1,e2,xnot1),(xnot1,e3,xnot1)]
    X0=[x0]
    Xm=[x123]
    G1=fsa(X1,S,T,X0,Xm,name='$G_1$')
    map=[(x1,y1),(x12,y12),(x123,y123),(xnot1,x0new),(x0,y0)]

    # call it as follows
    G2 = G1.renamestates(map)

    # or alternatively
    G2 = renamestates(G1, map)
    """
    # local copy of automaton G
    auto = self.copy()
    # we revise correctness of input parameters
    if isinstance(mapping, list):
        mapping = dict(mapping)
    elif isinstance(mapping, str):
        mapping, tab = buildmapping(auto, mapping)
    if not isinstance(mapping, dict):
        raise invalidArgument('Mapping must be a list of relations, string or dictionary')
    ren = lambda x: mapping.get(x, x)
    # updating the names in the  graph structure
    auto.Graph = nx.relabel_nodes(auto.Graph, mapping, copy=True)
    # updating the symbolic dictionary
    for x in mapping:
        if x in self.X and x in auto.symDict:
            del auto.symDict[x]
    # updating set of states X, marked states Xm and initial states X0
    auto.X = frozenset(ren(x) for x in auto.X)
    auto.Xm = frozenset(ren(x) for x in auto.Xm)
    auto.X0 = frozenset(ren(x) for x in auto.X0)
    auto._rebuild()
    return auto


def buildmapping(self, maptype, prefix=''):
    """This function allows to build different useful mappings
    to be used with the renamestates function"""

    def numbermapping():
        """ This subfunction generates a preordered mapping
            of states whose order is determined as follows:
            1. The lowest order is for initial states
            2. The Higher order is for final states
        """
        numbers = list(range(1, len(self) + 1))
        numbers.reverse()
        mapping = {}
        table = {}
        for state in _sorted(self.X0):
            order = numbers.pop()
            mapping.update({state: order})
        numbers.reverse()
        for state in _sorted(self.Xm - self.X0):
            order = numbers.pop()
            mapping.update({state: order})
        numbers.reverse()
        for state in _sorted(self.X - self.X0 - self.Xm):
            order = numbers.pop()
            mapping.update({state: order})
        return mapping, table

    def lettermapping():
        """ This subfunction generates a preordered mapping
            of states whose order is determined as follows:
            1. The lowest order is for initial states
               (Letters A,B,C,D)
            2. The Higher order is for final states
               (Letters W,X,Y,Z)
        """
        numbermap, table = numbermapping()
        mapping = dict((state, chr(order + 64)) for state, order in numbermap.items())
        return mapping, {}

    def xrefine():
        mapping = {}
        for state in self:
            x, y = state
            mapping.update({state: x})
        return mapping, {}

    def yrefine():
        mapping = {}
        for state in self:
            x, y = state
            mapping.update({state: y})
        return mapping, {}

    # selection of renaming
    if maptype == 'number':
        mapping, table = numbermapping()
    elif maptype == 'letter':
        mapping, table = lettermapping()
    elif maptype == 'xrefine':
        mapping, table = xrefine()
    elif maptype == 'yrefine':
        mapping, table = yrefine()
    else:
        raise invalidArgument("mapping type %s is not defined, use 'number', 'letter', 'xrefine' or 'yrefine'" % maptype)
    return mapping, table


def addevent(self, sigma):
    """
    This method extends the input alphabet of the automaton G1 without
    modification of the transition structure of G1. It is used for
    standarsizing the alphabets in common operations of two input
    automata. The new events added are defined both controllable and
    observable. Use the method setpar to change the definition of
    these sets. sigma can be a single event or a list (set) of events


    Example:
    -------

    syms('q1 q2 q3 q4 a1 b1 e f')
    table = [(a1,'a_1'),(b1,'b_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3'),(q4,'t_1')]
    X = [q1,q2,q3,q4]
    Sigma = [a1,b1]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3),(q3,b1,q4)]
    G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
    Gext= G1.addevents([e,f])
    print(Gext.Sigma)
    """
    # we make a inner copy of the input automaton
    auto = self.copy()
    # we check for validity of the data type of set passed
    try:
        if isinstance(sigma, (list, set, frozenset)):
            newset = frozenset(sigma) - auto.Sigma
        else:
            newset = frozenset([sigma]) - auto.Sigma
    except TypeError:
        raise invalidArgument('event sigma is not valid')
    auto.Sigma = auto.Sigma | newset
    # ... the new evens are considered observable by default
    auto.Sigobs = auto.Sigobs | (newset - EMPTYSTRINGSET)
    # ... and also controllable
    auto.Sigcon = auto.Sigcon | newset
    return auto


addevents = addevent


def deletevent(self, sigma):
    """
    This method provides low level access to the transition
    structure of input automaton. By using this method, user
    can delete the sigma event in the alphabet of automaton G.
    All transitions labelled by sigma will be deleted

    Example
    -------
    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    S = [a,b,c,d,e,sf]
    X = [x1,x2,x3,x4,x5,x6,x7]
    X0, Xm  = [x1], [x1]
    T = [(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),(x4,d,x4),(x1,a,x5),
         (x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7),(x1,a,x2)]
    G = fsa(X,S,T,X0,Xm)
    G1=G.deletevent(a)
    draw(G,G1)
    """
    # it raises an exception if is not possible to delete sigma
    if sigma not in self.Sigma:
        raise invalidArgument('event  %s is not in the input alphabet of G' % (str(sigma)))
    # we make a local copy of input automaton
    auto = self.copy()
    # drawing sigma of the input alphabet
    auto.Sigma = auto.Sigma - frozenset([sigma])
    auto.Sigobs = auto.Sigobs - frozenset([sigma])
    auto.Sigcon = auto.Sigcon - frozenset([sigma])
    # we find the transitions labelled by sigma and delete them
    for x, y, e in list(auto.Graph.edges(keys=True)):
        if e == sigma:
            auto.Graph.remove_edge(x, y, key=e)
    auto._rebuild()
    return auto


def addstate(self, x, marked=False):
    """
    This function adds the state x to the set of states of
    automaton G. If the parameter marked is set to True, the new
    state added is marked, otherwise it will be a nonmarking
    state. By default the parameter marked is False.

    Example

    from  deslab import *

    syms('q1 q2 q3 q4 x1 y1 a1 b1 e f')
    X = [q1,q2,q3]
    Sigma = [a1,b1]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3)]
    G1 = fsa(X,Sigma,T,X0,Xm)
    G2 = G1.addstate(q4)
    draw(G1,G2)
    """
    if self.empty:
        raise invalidAutomaton('states can not be added to the empty automaton')
    # we make a local copy of input automaton
    auto = self.copy()
    try:
        newstate = frozenset([x])
        auto.Graph.add_node(x)
        auto.X = auto.X | newstate
    except TypeError:
        raise deslabError('state  %s is not a  valid expression' % (str(x)))
    if marked:
        auto.Xm = auto.Xm | newstate
    return auto


def deletestate(self, x):
    """
    This function deletes the state x of automaton G and all
    the transitions that leave or arrive to x.
    """
    from .automatadefs import fsa
    if x not in self.X:
        # we raises an error for weird state
        raise deslabError('state  %s does not belong to the set of states in input automaton' % (str(x)))
    if len(self) == 1:
        # a one state automata becomes empty
        return fsa()
    # we make a local copy of input automaton
    auto = self.copy()
    # deleting the state and its edges
    auto.Graph.remove_node(x)
    # updating sets
    auto.X = auto.X - frozenset([x])
    auto.Xm = auto.Xm - frozenset([x])
    auto.X0 = auto.X0 - frozenset([x])
    auto._rebuild()
    return auto


def renametransition(G, rentrans):
    """This method changes the event that labels a specific
    transition. Suppose that automaton G possess a transition
    (x, e_old, y), by using this method the user can set a new
    event labeling this transition

    Example
    -------

    syms('q1 q2 q3 q4 x1 y1 a1 b1 e f')
    X = [q1,q2,q3,q4]
    Sigma = [a1,b1]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3),(q3,b1,q4)]
    G1 = fsa(X,Sigma,T,X0,Xm)
    Gr=G1.renametransition([q1,(a1,f),q2])
    draw(G1,Gr)
    """
    self = G
    try:
        x, pair, y = rentrans
        oldname, newname = pair
    except (TypeError, ValueError):
        raise invalidArgument('trans must be a list of the form [x, (old_e, new_e), y]')
    auto = self.deletetransition((x, oldname, y))
    auto = auto.addtransition((x, newname, y))
    return auto


def addselfloop(self, x, e):
    """
    This method adds a selfloop to the state x which
    is labelled by the event e.
    Example
    -------

    syms('q1 q2 q3 q4 x1 y1 a1 b1 e f')
    X = [q1,q2,q3,q4]
    Sigma = [a1,b1]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3),(q3,b1,q4)]
    G1 = fsa(X,Sigma,T,X0,Xm)
    Gsl=G1.addselfloop(q1,a1)
    draw(G1,Gsl)
    """
    auto = self.addtransition([x, e, x])
    return auto
