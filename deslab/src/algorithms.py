"""Mathematical functions for the automata objects"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    MIT license (see LICENSE).

import networkx as nx
from .def_const import *
from .exceptions import *
from .structure import *
from .utilities import _sorted, _tostr


class compCount:
    """ This class is a counter for dump states created in some
    operations (for instance, complement). When we instantiate
    a new automaton and call a new counter, that counter is
    incremented by 1.
    """
    counter = -1  # static variable, counts no of instances

    def __init__(self):
        compCount.counter += 1


def _newstate(X, base):
    """returns a state name based on base that is not in X"""
    name, i = base, 0
    while name in X:
        i += 1
        name = base + str(i)
    return name


def _label(G, x):
    """latex label of state x in automaton G"""
    return G.symDict[x] if x in G.symDict else _tostr(x)


def _succ(G, x, e):
    """set of states reached from x through e (empty if e is not defined)"""
    return G.deltaDict.get(x, {}).get(e, EMPTYSET)


def dfs(G, source=None):
    """Produce edges in a depth-first-search starting at source.
    it is the base of many algorithms used in accesibility"""
    nodes = list(source)
    visited = set()
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, iter(G[start]))]
        while stack:
            parent, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    visited.add(child)
                    stack.append((child, iter(G[child])))
            except StopIteration:
                stack.pop()
    visited = frozenset(visited)
    return visited


def ac(automaton):
    """ This function calculates the accessible part
    of an automaton object. """
    from .automatadefs import fsa
    if automaton.empty or (automaton.X0 == EMPTYSET):
        return fsa()
    auto = automaton.copy()
    Xac = dfs(auto.Graph, auto.X0)  # calculating accesibility
    if Xac == EMPTYSET:
        return fsa()
    auto.Graph.remove_nodes_from(auto.X - Xac)
    auto.X = Xac
    auto.Xm = auto.Xm & Xac
    auto._rebuild()
    return auto


def coac(automaton):
    """ This function calculates the coaccessible part
    of an automaton object. """
    from .automatadefs import fsa
    if automaton.empty or (automaton.Xm == EMPTYSET):
        return fsa()
    auto = automaton.copy()
    Xcoac = dfs(auto.Graph.reverse(copy=False), auto.Xm)
    if (auto.X0 & Xcoac) == EMPTYSET:
        # if initial state isn't in Xcoac result is empty
        return fsa()
    auto.Graph.remove_nodes_from(auto.X - Xcoac)  # we left coaccesible part
    auto.X = Xcoac
    auto.X0 = auto.X0 & Xcoac
    auto._rebuild()
    return auto


def trim(automaton):
    """ This function calculates a trimmed
    version of an automaton object G passed to it. """
    trimmed = coac(automaton)
    trimmed = ac(trimmed)
    trimmed.name = 'untitled'
    trimmed.style = 'normal'
    return trimmed


def invproj(self, sigma=[]):
    """ This function calculates  the inverse projection
    of the automaton object G over the alphabet Sigma | sigma.
    A selfloop of each new event is added at every state."""
    # case the observed set is tha same
    if not sigma:
        return self
    auto = self.copy()
    new_events = frozenset(sigma) - auto.Sigma
    for state in auto.X:
        for event in new_events:
            auto.Graph.add_edge(state, state, key=event, label=event)  # adding transitions
    auto.Sigma = auto.Sigma | new_events
    auto.Sigobs = auto.Sigobs | (new_events - EMPTYSTRINGSET)
    auto.Sigcon = auto.Sigcon | new_events
    auto.name = 'untitled'
    auto.type = 'normal'
    auto._rebuild()
    return auto


def pclosure(self):
    """ This function calculates the prefix closed automaton
    which marks the prefix closure of the language marked
    by automaton G """
    auto = self.copy()  # copy of automaton
    auto = trim(auto)
    auto = auto.setpar(Xm=auto.X)
    return auto


def ispfclosed(auto):
    """ This function checks if Lm(G) is prefix closed,
    i.e. if Lm(G) = pre(Lm(G))"""
    from .comparison import are_langequiv
    return are_langequiv(auto, pclosure(auto))


def langquotient(G1, G2):
    """ This function calculates the right quotient between
    the languages marked by the automata G1 and G2.
    It returns the automaton D such that Lm(D) = Lm(G1)/Lm(G2),
    i.e. the set of strings s for which there is a string t
    in Lm(G2) such that st belongs to Lm(G1).

    Example
    -------

    syms('q1 q2 q3 a1 b1 e f')
    simtab=[(q1,'q_1'),(q2,'q_2'),(q3,'q_3'),
            (a1,'a_1'),(b1,'b_1')]
    X = [q1,q2,q3]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q2]
    Xm2 = [q2,q3]
    T =[(q1,a1,q2),(q2,b1,q3)]
    T2 = [(q1,a1,q2),(q2,b1,q3)]
    G1 = fsa(X,Sigma,T,X0,Xm,simtab,name='$G_1$')
    G2 = fsa(X,Sigma,T2,X0,Xm2,simtab,name='$G_2$')
    D=langquotient(G2,G1)
    draw(G1,G2,D)
    """
    from .automatadefs import fsa
    from .comparison import isitempty
    if G1.empty or isitempty(G2):
        return fsa()
    # a state x of G1 is marked in the quotient if some string
    # of Lm(G2) leads from x to a marked state of G1
    Xm_result = set()
    for state in G1.X:
        G1_mod = G1.setpar(X0=[state])
        if not isitempty(G1_mod & G2):
            Xm_result.add(state)
    Result = G1.setpar(Xm=Xm_result)
    return trim(Result)


def langdiff(self, other):
    """ This function calculates the set difference between
    the languages marked by the automata G1 and G2.
    It returns the automaton D such that Lm(D) = Lm(G1)\\Lm(G2)

    Example
    -------

    syms('q1 q2 q3 a1 b1 e f')
    simtab=[(q1,'q_1'),(q2,'q_2'),(q3,'q_3'),
            (a1,'a_1'),(b1,'b_1')]
    X = [q1,q2,q3]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q2]
    Xm2 = [q2,q3]
    T =[(q1,a1,q2),(q2,b1,q3)]
    T2 = [(q1,a1,q2),(q2,b1,q3)]
    G1 = fsa(X,Sigma,T,X0,Xm,simtab,name='$G_1$')
    G2 = fsa(X,Sigma,T2,X0,Xm2,simtab,name='$G_2$')
    D=langdiff(G2,G1)
    draw(G1,G2,D)
    """
    # imports from modules
    from .automatadefs import fsa

    if self.empty:  # case first automaton is empty
        return fsa()
    elif other.empty:  # case 2nd automaton is empty
        return self
    # the complement is taken over the union of both alphabets
    other_ext = other.addevents((self.Sigma - other.Sigma) - EMPTYSTRINGSET)
    lang_diff = self & complement(other_ext)
    lang_diff = trim(lang_diff)
    return lang_diff


def complement(self):
    """ This function calculates the complement of
    the language marked by the automaton G. It returns
    the automaton C such that Lm(C) = Lm(G)^C
    Non deterministic automata are determinized first.

    Example
    -------
    syms('q1 q2 q3 a1 b1 e f')
    table = [(a1,'a'),(b1,'b_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
    X = [q1,q2,q3]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q2]
    T =[(q1,a1,q2),(q2,b1,q3)]
    G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
    Gc=complement(G1)
    draw(G1,Gc)
    """
    if self.empty:
        # the complement of the empty language is Sigma^*
        return sigmakleeneclos(self.Sigma - EMPTYSTRINGSET)
    if self.is_dfa():
        auto = self.copy()
    else:
        auto = epsilonobserver(self)
    # we create a unique label for dump_state
    countInstance = compCount()
    dump = _newstate(auto.X, '_XD_' + str(countInstance.counter))  # dump state
    dump_latex = 'X_D'  # latex string of dump state
    X, Gamma = auto.X, auto.Gamma
    Sigma = auto.Sigma - EMPTYSTRINGSET

    auto.Graph.add_node(dump)
    for event in Sigma:
        auto.Graph.add_edge(dump, dump, key=event, label=event)
    for state in X:
        validSet = Sigma - Gamma(state)
        for event in validSet:
            auto.Graph.add_edge(state, dump, key=event, label=event)
    auto.X = X | frozenset([dump])  # new state set
    auto._rebuild()
    auto.name = 'untitled'
    auto.type = 'Normal'
    auto = auto.setpar(Xm=auto.X - auto.Xm)
    auto.symDict[dump] = dump_latex
    auto = trim(auto)
    return auto


def complete(self):
    """ This function calculates the complete automaton
    that generates Sigma^*, where Sigma is the input
    alphabet. The output automaton marks the same language
    as  automaton G passed as input argument.
    """
    auto = self.copy()
    X, Gamma = auto.X, auto.Gamma
    Sigma = auto.Sigma - EMPTYSTRINGSET
    dump = _newstate(X, 'D')  # dump state
    dump_latex = 'X_D'  # latex string of dump state

    auto.Graph.add_node(dump)
    for event in Sigma:
        auto.Graph.add_edge(dump, dump, key=event, label=event)
    for state in X:
        validSet = Sigma - Gamma(state)
        for event in validSet:
            auto.Graph.add_edge(state, dump, key=event, label=event)
    auto.X = X | frozenset([dump])  # new state set
    auto._rebuild()
    auto.name = 'untitled'
    auto.type = 'Normal'
    auto.symDict[dump] = dump_latex
    return auto


def proj(self, Sigma_o=[]):
    """ This function calculates the nondeterministic
    automaton that represents the projection of the
    languages generated and marked by the automaton
    G over the observable alphabet Sigma_o. Assume Gp is the
    obtained automaton, then Gp is such that:
    L(Gp) = P(L(G),Sigma_o), and
    Lm(Gp) = P(Lm(G),Sigma_o)
    """
    from .automatadefs import fsa
    if Sigma_o == []:
        sigma_obs = self.Sigobs
    elif isinstance(Sigma_o, (list, set, frozenset)):
        sigma_obs = frozenset(Sigma_o)
    else:
        raise invalidArgument('Observed set must be of type set or list')
    sigma_obs = sigma_obs - EMPTYSTRINGSET
    if self.empty:
        return fsa()
    auto = self.copy()
    Graph = self.Graph

    def unobsreachstates(state):
        # this subfunction returns the unobservable reach of the state
        # of argument
        Stack = [state]  # initial stack
        Xreachable = {state}
        while Stack != []:
            xcurrent = Stack.pop()
            for _, next_xcurrent, event in Graph.out_edges(xcurrent, keys=True):
                if (event not in sigma_obs) and (next_xcurrent not in Xreachable):
                    Xreachable.add(next_xcurrent)
                    Stack.append(next_xcurrent)
        return Xreachable

    # each state x of the projection has an observable transition
    # (x, e, y) for every observable transition (x', e, y) of G
    # leaving a state x' in the unobservable reach of x
    Xwaiting = _sorted(auto.X0)
    Xdone = set(Xwaiting)
    Xm_p = set()
    transition = []
    while Xwaiting != []:
        xcurrent = Xwaiting.pop()
        Xuobsreach = unobsreachstates(xcurrent)
        if Xuobsreach & self.Xm:
            Xm_p.add(xcurrent)
        for xreach in Xuobsreach:
            for _, next_xreach, event in Graph.out_edges(xreach, keys=True):
                if event in sigma_obs:
                    transition.append((xcurrent, next_xreach, event))
                    if next_xreach not in Xdone:
                        Xdone.add(next_xreach)
                        Xwaiting.append(next_xreach)

    auto.Graph = nx.MultiDiGraph()
    auto.Graph.add_nodes_from(_sorted(Xdone))
    for x, y, event in transition:
        if not auto.Graph.has_edge(x, y, key=event):
            auto.Graph.add_edge(x, y, key=event, label=event)
    auto.X = frozenset(Xdone)
    auto.Sigma = sigma_obs
    auto.Xm = frozenset(Xm_p)
    auto.Sigobs = sigma_obs
    auto.Sigcon = auto.Sigcon & sigma_obs
    auto._rebuild()
    return auto


def sigmakleeneclos(sigma, x0='s0', label='s_0'):
    """ This function calculates a single state automaton
    that marks and generates the language Sigma^*, where
    Sigma is the set (list) of events passed as argument.
    The name of the single state can be set with the argument
    x0.
    """
    from .automatadefs import fsa
    if isinstance(sigma, (list, set, frozenset)):
        Sigma = frozenset(sigma)
    else:
        raise invalidArgument('Sigma must be defined using set, frozenset or list')
    X0 = frozenset([x0])
    X, Xm = X0, X0
    transition = []
    for event in Sigma:
        transition.append([x0, event, x0])
    label = [(x0, label)]
    auto = fsa(X, Sigma, transition, X0, Xm, table=label)
    return auto


def kleeneclos(self, dfa=True):
    """ This function calculates an automaton that marks
    the language Lm(G)^*, where Lm(G) is the language
    marked by the automaton G. If dfa is True the
    result is a deterministic automaton.
    """
    auto = self.copy()
    X, Sigma = auto.X, auto.Sigma
    X0, Xm = auto.X0, auto.Xm

    X0_kleene = _newstate(X, 'I_S')  # initial state added
    Xend_kleene = _newstate(X, 'F_S')  # final state added

    auto.Graph.add_node(X0_kleene)
    auto.Graph.add_node(Xend_kleene)
    auto.Graph.add_edge(X0_kleene, Xend_kleene, key=epsilon, label=epsilon)
    auto.Graph.add_edge(Xend_kleene, X0_kleene, key=epsilon, label=epsilon)
    # adding transitions from X0_kleene  to initial states
    for x_0 in X0:
        auto.Graph.add_edge(X0_kleene, x_0, key=epsilon, label=epsilon)
    # adding transitions from final states to Xend_kleene
    for x_m in Xm:
        auto.Graph.add_edge(x_m, Xend_kleene, key=epsilon, label=epsilon)

    auto.X = X | frozenset([X0_kleene, Xend_kleene])
    auto.Sigma = Sigma | EMPTYSTRINGSET
    auto.Xm = frozenset([Xend_kleene])
    auto.X0 = frozenset([X0_kleene])
    auto.empty = False
    # creating structure
    auto._rebuild()
    auto.symDict[epsilon] = '\\varepsilon'
    auto.name = 'untitled'
    auto.type = 'normal'
    if dfa:
        auto = epsilonobserver(auto)
        mapping, tab = buildmapping(auto, 'number')
        auto = auto.renamestates(mapping)
        auto = auto.setpar(style='normal', direction='LR')
    return auto


def union(self, other, dfa=True):
    """
    union(G1,G2,dfa)
    This function calculates an automaton that marks
    the language Lm(G1)+Lm(G2), where G1 and G2 are the input
    automata. The resulting automaton is a deterministic automaton
    that marks the union of the languages marked by the input
    automata.

    Example
    -------

    syms('s1 s2 s3 s4 a b c d e f')
    X1=[s1,s2,s3,s4]
    E1=[a,b,c]
    Transition1=[(s1,a,s2),(s2,b,s3),(s3,c,s4)]
    X0=[s1]
    Xm=[s2,s3,s4]
    G1=fsa(X1,E1,Transition1,X0,Xm,name='$G_1$')
    X2=[s1,s2,s3,s4]
    E2=[d,e,f]
    Transition2=[(s1,d,s2),(s2,e,s3),(s3,f,s4),(s1,e,s3),(s1,f,s4),(s2,f,s4)]
    X0,Xm=[s1],[s1,s2]
    G2=fsa(X2,E2,Transition2,X0,Xm, name='$G_2$')
    U=union(G1,G2)
    draw(G1,G2,U)
    """
    # imports from modules
    from .automatadefs import fsa
    from .comparison import isitempty

    # inner functions used in union operation
    def rename(state_set, name):
        """This is a simple function for renaming the states
        of automaton to minimize name conflicts"""
        renamed = [(state, name) for state in state_set]
        return renamed

    def generate_table():
        table = {}
        for event in Sigma_u:
            if event in self.symDict:
                table.update({event: self.symDict[event]})
            if event in other.symDict:
                table.update({event: other.symDict[event]})
        return table

    # G1 marks an empty language and G2 does not
    if isitempty(self) and not isitempty(other):
        return other
    # G1 and G2 marks empty languages
    elif isitempty(self) and isitempty(other):
        return fsa()
    # G1 marks a nonempty language and G2 do.
    elif not isitempty(self) and isitempty(other):
        return self

    # easy simbol renaming
    Graph1, Graph2 = self.Graph, other.Graph
    X01, X02 = self.X0, other.X0
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    X1, X2 = self.X, other.X
    Xm1, Xm2 = self.Xm, other.Xm
    # initial values of parameters
    transition = []
    countInstance = compCount()
    new_name1 = countInstance.counter
    countInstance = compCount()
    new_name2 = countInstance.counter
    # creating the transitions of the composed automaton
    # with respect to  G1
    for edge in Graph1.edges(keys=True):
        x_a = (edge[0], new_name1)
        x_b = (edge[1], new_name1)
        transition.append([x_a, edge[2], x_b])
    # creating the transitions of the composed automaton
    # with respect to  G2
    for edge in Graph2.edges(keys=True):
        x_a = (edge[0], new_name2)
        x_b = (edge[1], new_name2)
        transition.append([x_a, edge[2], x_b])
    # adding new initial state
    X0_u = 'I_S'
    # adding transitions of new initial state X_0u
    # with initial states of G1
    for state in X01:
        transition.append([X0_u, epsilon, (state, new_name1)])
    # adding transitions of new initial state X_0u
    # with initial states of G2
    for state in X02:
        transition.append([X0_u, epsilon, (state, new_name2)])
    # renaming and building state set X_u of union automaton
    X1_ren, X2_ren = rename(X1, new_name1), rename(X2, new_name2)
    X_u = X1_ren + X2_ren + [X0_u]
    # renaming and building state set X_u of union automaton
    Xm1_ren, Xm2_ren = rename(Xm1, new_name1), rename(Xm2, new_name2)
    Xm_u = Xm1_ren + Xm2_ren
    # building the new event set
    Sigma_u = Sigma1 | Sigma2 | EMPTYSTRINGSET
    # constructing symbolic table for composed system
    table_u = generate_table()
    unionaut = fsa(X_u, Sigma_u, transition, [X0_u], Xm_u,
                   table=table_u, name='untitled', type='Normal')
    if dfa:
        unionaut = epsilonobserver(unionaut)
        mapping, tab = buildmapping(unionaut, 'number')
        unionaut = unionaut.renamestates(mapping)
        unionaut = unionaut.setpar(style='normal', direction='LR')
    return unionaut


def concatenation(self, other, dfa=True):
    """ This function calculates an automaton that marks
    the language Lm(G1)Lm(G2), where G1 and G2 are the input
    automata. The resulting automaton is a deterministic automaton
    that marks the concatenation of the languages marked by the input
    automata.

    Example
    -------
    syms('q1 q2 q3 a1 b1 e f')
    table = [(a1,'a_1'),(b1,'b_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
    X = [q1,q2,q3]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q1,q2]
    T =[(q1,a1,q2),(q2,b1,q3)]
    G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$')
    Xm2 = [q2,q3]
    T2 = [(q1,a1,q2),(q2,b1,q3)]
    G2 = fsa(X,Sigma,T2,X0,Xm2,table,name='$G_2$')
    C= concatenation(G1,G2)
    draw(G1,G2,C)
    """
    from .automatadefs import fsa

    # inner functions used in union operation
    def rename(state_set, name):
        """This is a simple function for renaming the states
        of automaton to minimize name conflicts"""
        renamed = [(state, name) for state in state_set]
        return renamed

    def generate_table():
        """this function updates the symbolic dictionary
        of the automata resulting of concatenation in order
        to preserve the labels of events of the input
        automata"""
        table = {}
        for event in Sigma_c:
            if event in self.symDict:
                table.update({event: self.symDict[event]})
            if event in other.symDict:
                table.update({event: other.symDict[event]})
        return table

    # starting main program
    if self.empty or other.empty:
        # the concatenation with the empty language is empty
        return fsa()

    Graph1, Graph2 = self.Graph, other.Graph
    X01, X02 = self.X0, other.X0
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    X1, X2 = self.X, other.X
    Xm1, Xm2 = self.Xm, other.Xm
    # initializing parameters
    transition = []
    countInstance2 = compCount()
    new_name1 = countInstance2.counter
    countInstance2 = compCount()
    new_name2 = countInstance2.counter
    # adding transitions of G1
    for edge in Graph1.edges(keys=True):
        x_a = (edge[0], new_name1)
        x_b = (edge[1], new_name1)
        transition.append([x_a, edge[2], x_b])
    # adding transition of G2
    for edge in Graph2.edges(keys=True):
        x_a = (edge[0], new_name2)
        x_b = (edge[1], new_name2)
        transition.append([x_a, edge[2], x_b])
    # connecting final states of G1 with initial states of G2
    for xm_1 in Xm1:
        for x0_2 in X02:
            transition.append([(xm_1, new_name1), epsilon, (x0_2, new_name2)])
    # renaming initial states
    X0_c = frozenset(rename(X01, new_name1))
    # renaming states
    X1_ren, X2_ren = rename(X1, new_name1), rename(X2, new_name2)
    X_c = X1_ren + X2_ren
    # renaming marked states
    Xm_c = rename(Xm2, new_name2)
    # building alphabet of the concatenation automaton
    Sigma_c = Sigma1 | Sigma2 | EMPTYSTRINGSET
    table_c = generate_table()
    concat = fsa(X_c, Sigma_c, transition, X0_c, Xm_c,
                 table=table_c, name='untitled', type='Normal')
    if dfa:
        concat = epsilonobserver(concat)
        mapping, tab = buildmapping(concat, 'number')
        concat = concat.renamestates(mapping)
        concat = concat.setpar(style='normal', direction='LR')
    return concat


def observer(self, Sigma_o=[]):
    """ This function calculates a deterministic automaton
    which marks and generates the projection of the marked and
    generated languages of the input automaton G over the alphabet
    of observable events Sigma_o, defined by the user. If a list (or set)
    of observable events is not provided, the function observer takes
    the set Sigobs of the input automaton as the set of observable
    events"""
    from .automatadefs import fsa

    # inner functions
    def Gamma_obs(set):  # Gamma observer calcularion
        active_events = EMPTYSET
        for q in set:
            active_events = active_events | self.Gamma(q)
        active_events = active_events & Sigma_obs
        return active_events

    def latexname(Xnew):
        """This function takes a frozenset of the observer
        automaton and generate a latex label, based
        on the dictionaries of the input automaton"""
        name_state = ','.join(_label(self, xn) for xn in _sorted(Xnew))
        return r'\{' + name_state + r'\}'

    # Main program
    if self.empty:
        return fsa()
    # easy name for parameters
    X0, X = self.X0, self.X
    Sigma, Xm, Sigobs = self.Sigma, self.Xm, self.Sigobs
    # determinig the set of observable events
    if Sigma_o == []:  # Sigma_o was not defined
        Sigma_obs = Sigobs
    elif isinstance(Sigma_o, (list, set, frozenset)):
        Sigma_obs = frozenset(Sigma_o)
    else:
        raise invalidArgument('Observed set must be of type set, frozenset or list')
    Sigma_obs = Sigma_obs - EMPTYSTRINGSET
    # in the case of not unobservable events
    # we return the input automaton
    if self.is_dfa() and (Sigma_obs == self.Sigma):
        return self
    # initial values of parameters
    X0_obs = self.unobsreach(X0, Sigma_obs)
    X_obs = [X0_obs]
    X_found = {X0_obs}
    S = [X0_obs]  # unobs. reach of X0 as initial value of stack
    transition = []
    Xm_obs = []
    # updating X0_p label
    table_obs = {X0_obs: latexname(X0_obs)}
    # testing of X0obs is marked
    if X0_obs & Xm != EMPTYSET:
        Xm_obs.append(X0_obs)
    # main stack cycle
    while S != []:  # beginning of subset construction
        Q = S.pop()
        for sigma in _sorted(Gamma_obs(Q)):
            Q_next = self.deltaobs(Q, sigma, Sigma_obs)  # reached set
            if Q_next not in X_found:  # new state found
                X_found.add(Q_next)
                X_obs.append(Q_next)
                S.append(Q_next)
                if Q_next & Xm != EMPTYSET:  # marking that state
                    Xm_obs.append(Q_next)
                table_obs.update({Q_next: latexname(Q_next)})  # creating the latex table
            transition.append([Q, sigma, Q_next])
            if sigma in self.symDict:
                table_obs.update({sigma: self.symDict[sigma]})
    # defining the observer DFA
    observer = fsa(X_obs, Sigma_obs, transition, [X0_obs],
                   Xm_obs, Sigobs=Sigma_obs, table=table_obs, Sigcon=self.Sigcon & Sigma_obs)
    observer.style = 'observer'  # graphic property for square states
    observer.direction = 'UD'  # graphic property for top-down rendering of automaton
    return observer


def parallelnondet(self, other):
    """This function builds the automaton corresponding
    to the parallel composition of the input automata.
    Specifically, parallelnondet assumes that the input
    automata (one or both of them) are non deterministic.
    The epsilon event is never synchronized."""
    from .automatadefs import fsa

    # events that synchronize both automata
    Sigma_s = (self.Sigma & other.Sigma) - EMPTYSTRINGSET

    def Gamma_p(p):
        """definition of the Gamma function of parallel
        composition of the input automata for the tuple
        p = (x1,x2)"""
        x1, x2 = p  # defined for the tuple p
        # these are the active events
        G1, G2 = Gamma1(x1), Gamma2(x2)
        active_events = (G1 & G2 & Sigma_s) | (G1 - Sigma_s) | (G2 - Sigma_s)
        return active_events

    def delta_p(p, sigma):
        """definition of the delta transition  function
         of parallel composition of the input automata. It is
         defined for the tuple p = (x1,x2) and event sigma
         the output is the set of states that can be reached
         from p"""
        x1, x2 = p
        if sigma in Sigma_s:
            return frozenset((q1, q2) for q1 in _succ(self, x1, sigma)
                             for q2 in _succ(other, x2, sigma))
        # private events (and epsilon) move a single automaton
        Q = frozenset((q1, x2) for q1 in _succ(self, x1, sigma))
        return Q | frozenset((x1, q2) for q2 in _succ(other, x2, sigma))

    def latexname(p):
        """This function takes a tuple of the composite
        automaton and generate a latex pretty name, based
        on the dictionaries of each input automaton"""
        x1, x2 = p
        # pretty tuple print as, for instance, (\pi,\Gamma)
        return '(' + _label(self, x1) + ',' + _label(other, x2) + ')'

    # Main program
    # easy names for inner variables
    X01, X02 = self.X0, other.X0
    Xm1, Xm2 = self.Xm, other.Xm
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    Gamma1, Gamma2 = self.Gamma, other.Gamma
    Sigobs1, Sigobs2 = self.Sigobs, other.Sigobs
    Sigcon1, Sigcon2 = self.Sigcon, other.Sigcon

    # initial values for the composite automaton
    X0_p = [(x01, x02) for x01 in _sorted(X01) for x02 in _sorted(X02)]
    S = list(X0_p)
    X_p = set(X0_p)
    Xm_p = set()
    Sigobs_p = Sigobs1 | Sigobs2
    Sigcon_p = Sigcon1 | Sigcon2
    Sigma_p = Sigma1 | Sigma2
    transition = []
    # generating labeling table for initial states
    table_p = {}
    for p in X0_p:  # labeling initial states
        table_p.update({p: latexname(p)})
        p1, p2 = p
        if (p1 in Xm1) & (p2 in Xm2):
            Xm_p.add(p)
    # main stack cycle
    while S != []:
        p = S.pop()  # taking a tuple
        # evaluating in tha active event set
        for sigma in _sorted(Gamma_p(p)):
            Q = delta_p(p, sigma)
            # Q contains the tuples fo reached states
            for q in Q:
                if q not in X_p:
                    # updating states of composite automaton and stack
                    X_p.add(q)
                    S.append(q)
                    q1, q2 = q
                    # updating marked states
                    if (q1 in Xm1) & (q2 in Xm2):
                        Xm_p.add(q)
                    # updating latex dictionary
                    table_p.update({q: latexname(q)})
                transition.append([p, sigma, q])
            if sigma in self.symDict:
                table_p.update({sigma: self.symDict[sigma]})
            elif sigma in other.symDict:
                table_p.update({sigma: other.symDict[sigma]})
    # finally, we build the composite automaton
    parnondet = fsa(X_p, Sigma_p, transition, X0_p, Xm_p, table=table_p,
                    Sigobs=Sigobs_p, Sigcon=Sigcon_p, name='untitled')
    return parnondet


def paralleldet(self, other):
    """This function builds the automaton corresponding
    to the parallel composition of the input automata.
    Specifically, paralleldet is optimized for deterministic
    automata and it produces an error if the user tries to
    use it with nondeterministic automata"""
    from .automatadefs import fsa

    def Gamma_p(p):
        """ definition of the Gamma function of parallel
        composition of the input automata for the tuple
        p = (x1,x2)"""
        x1, x2 = p
        active_events = (Gamma1(x1) & Gamma2(x2)) | (Gamma1(x1) - Sigma2)
        active_events = active_events | (Gamma2(x2) - Sigma1)
        return active_events

    def delta_p(p, sigma):
        """ definition of the delta transition  function
        of parallel composition of the input automata. It is
        defined for the tuple p = (x1,x2) and event sigma
        the output is the single state that can be reached
        from p
        """
        x1, x2 = p
        if sigma in Gamma1(x1) & Gamma2(x2):
            x1_n, x2_n = delta1(x1, sigma), delta2(x2, sigma)
        elif sigma in Gamma1(x1) - Sigma2:
            x1_n, x2_n = delta1(x1, sigma), x2
        elif sigma in Gamma2(x2) - Sigma1:
            x1_n, x2_n = x1, delta2(x2, sigma)
        else:
            x1_n, x2_n = EMPTYSET, EMPTYSET
        return x1_n, x2_n

    def latexname(p):
        """This function takes a tuple of the composite
        automaton and generate a latex pretty name, based
        on the dictionaries of each input automaton"""
        x1, x2 = p
        return '(' + _label(self, x1) + ',' + _label(other, x2) + ')'

    # Main program
    # easy names for inner variables
    X01, X02 = self.X0, other.X0
    Xm1, Xm2 = self.Xm, other.Xm
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    Gamma1, Gamma2 = self.Gamma, other.Gamma
    delta1, delta2 = self.delta, other.delta
    Sigobs1, Sigobs2 = self.Sigobs, other.Sigobs
    Sigcon1, Sigcon2 = self.Sigcon, other.Sigcon
    # initial values for composite automaton
    p0 = (list(X01)[0], list(X02)[0])
    X0_p = [p0]
    S = [p0]
    X_p = {p0}
    Xm_p = set()
    Sigobs_p = Sigobs1 | Sigobs2
    Sigcon_p = Sigcon1 | Sigcon2
    Sigma_p = Sigma1 | Sigma2
    transition = []
    table_p = {}
    table_p.update({p0: latexname(p0)})
    p01, p02 = p0
    # is initial state marked ?
    if (p01 in Xm1) & (p02 in Xm2):
        Xm_p.add(p0)
    # main stack cycle
    while S != []:
        p = S.pop()  # taking a tuple
        for sigma in _sorted(Gamma_p(p)):
            q = delta_p(p, sigma)  # reached state
            if q not in X_p:
                # updating state and stack
                X_p.add(q)
                S.append(q)
                q1, q2 = q
                if (q1 in Xm1) & (q2 in Xm2):
                    # updating marked states
                    Xm_p.add(q)
                # updating labeling table
                table_p.update({q: latexname(q)})
            transition.append([p, sigma, q])
            if sigma in self.symDict:
                table_p.update({sigma: self.symDict[sigma]})
            elif sigma in other.symDict:
                table_p.update({sigma: other.symDict[sigma]})
    # building the composite automaton
    pardet = fsa(X_p, Sigma_p, transition, X0_p, Xm_p, table=table_p,
                 Sigobs=Sigobs_p, Sigcon=Sigcon_p, name='untitled')
    return pardet


def productnondet(self, other):
    """This function builds the automaton corresponding
    to the product composition (intersection) of the input automata.
    Specifically, productnondet assumes that the input
    automata (one or both of them) are not deterministic.
    The epsilon transitions of each automaton are executed
    independently."""
    from .automatadefs import fsa

    def Gamma_prod(p):
        """definition of the Gamma function of product
        composition of the input automata for the tuple
        p = (x1,x2)"""
        x1, x2 = p  # defined for the tuple p
        # these are the active events
        G1, G2 = Gamma1(x1), Gamma2(x2)
        active_events = ((G1 & G2) - EMPTYSTRINGSET) | ((G1 | G2) & EMPTYSTRINGSET)
        return active_events

    def delta_prod(p, sigma):
        x1, x2 = p
        if sigma == epsilon:
            Q = frozenset((q1, x2) for q1 in _succ(self, x1, sigma))
            return Q | frozenset((x1, q2) for q2 in _succ(other, x2, sigma))
        return frozenset((q1, q2) for q1 in _succ(self, x1, sigma)
                         for q2 in _succ(other, x2, sigma))

    def latexname(p):
        """This function takes a tuple of the composite
        automaton and generate a latex pretty name, based
        on the dictionaries of each input automaton"""
        x1, x2 = p
        # pretty tuple print as, for instance, (\pi,\Gamma)
        return '(' + _label(self, x1) + ',' + _label(other, x2) + ')'

    # Main program
    if self.empty or other.empty:
        return fsa()
    # easy names for inner variables
    X01, X02 = self.X0, other.X0
    Xm1, Xm2 = self.Xm, other.Xm
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    Gamma1, Gamma2 = self.Gamma, other.Gamma
    Sigobs1, Sigobs2 = self.Sigobs, other.Sigobs
    Sigcon1, Sigcon2 = self.Sigcon, other.Sigcon
    # initial values for the composite automaton
    X0_p = [(x01, x02) for x01 in _sorted(X01) for x02 in _sorted(X02)]
    S = list(X0_p)
    X_p = set(X0_p)
    Xm_p = set()
    Sigobs_p = Sigobs1 | Sigobs2
    Sigcon_p = Sigcon1 | Sigcon2
    Sigma_p = Sigma1 | Sigma2
    transition = []
    # generating labeling table for initial states
    table_p = {}
    for p in X0_p:  # labeling initial states
        table_p.update({p: latexname(p)})
        p1, p2 = p
        if (p1 in Xm1) & (p2 in Xm2):
            Xm_p.add(p)
    # main stack cycle
    while S != []:
        p = S.pop()  # taking a tuple from stack
        # evaluating in tha active event set
        for sigma in _sorted(Gamma_prod(p)):
            Q = delta_prod(p, sigma)
            # Q contains the tuples fo reached states
            for q in Q:
                if q not in X_p:
                    # updating states of composite automaton and stack
                    X_p.add(q)
                    S.append(q)
                    q1, q2 = q
                    # updating marked states
                    if (q1 in Xm1) & (q2 in Xm2):
                        Xm_p.add(q)
                    # updating latex dictionary
                    table_p.update({q: latexname(q)})
                transition.append([p, sigma, q])
            if sigma in self.symDict:
                table_p.update({sigma: self.symDict[sigma]})
            elif sigma in other.symDict:
                table_p.update({sigma: other.symDict[sigma]})
    # finally, we build the composite automaton
    prodnondet = fsa(X_p, Sigma_p, transition, X0_p, Xm_p, table=table_p,
                     Sigobs=Sigobs_p, Sigcon=Sigcon_p, name='untitled')
    return prodnondet


def productdet(self, other):
    """This function builds an automaton corresponding
    to the product of the input automata.
    Specifically, productdet is optimized for deterministic
    automata and it generates an error if the user tries to
    use it with nondeterministic automata"""
    from .automatadefs import fsa

    def Gamma_prod(p):
        """ definition of the Gamma function of parallel
        composition of the input automata for the tuple
        p = (x1,x2)"""
        x1, x2 = p
        active_events = Gamma1(x1) & Gamma2(x2)
        return active_events

    def latexname(p):
        """This function takes a tuple of the composite
        automaton and generate a latex pretty name, based
        on the dictionaries of each input automaton"""
        x1, x2 = p
        return '(' + _label(self, x1) + ',' + _label(other, x2) + ')'

    # Main program
    if self.empty or other.empty:
        return fsa()
    # easy names for inner variables
    X01, X02 = self.X0, other.X0
    Xm1, Xm2 = self.Xm, other.Xm
    Sigma1, Sigma2 = self.Sigma, other.Sigma
    Gamma1, Gamma2 = self.Gamma, other.Gamma
    delta1, delta2 = self.delta, other.delta
    Sigobs1, Sigobs2 = self.Sigobs, other.Sigobs
    Sigcon1, Sigcon2 = self.Sigcon, other.Sigcon
    # initial values for composite automaton
    p0 = (list(X01)[0], list(X02)[0])
    X0_p = [p0]
    S = [p0]
    X_p = {p0}
    Xm_p = set()
    Sigobs_p = Sigobs1 | Sigobs2
    Sigcon_p = Sigcon1 | Sigcon2
    Sigma_p = Sigma1 | Sigma2
    transition = []
    table_p = {}
    table_p.update({p0: latexname(p0)})
    p01, p02 = p0
    # is initial state marked ?
    if (p01 in Xm1) & (p02 in Xm2):
        Xm_p.add(p0)
    # main stack cycle
    while S != []:
        p = S.pop()  # taking a tuple
        p1, p2 = p
        for sigma in _sorted(Gamma_prod(p)):
            q = delta1(p1, sigma), delta2(p2, sigma)  # reached state
            if q not in X_p:
                # updating state and stack
                X_p.add(q)
                S.append(q)
                q1, q2 = q
                if (q1 in Xm1) & (q2 in Xm2):
                    # updating marked states
                    Xm_p.add(q)
                # updating labeling table
                table_p.update({q: latexname(q)})
            transition.append([p, sigma, q])
            if sigma in self.symDict:
                table_p.update({sigma: self.symDict[sigma]})
            elif sigma in other.symDict:
                table_p.update({sigma: other.symDict[sigma]})
    # building the composite automaton
    proddet = fsa(X_p, Sigma_p, transition, X0_p, Xm_p, table=table_p,
                  Sigobs=Sigobs_p, Sigcon=Sigcon_p, name='untitled')
    return proddet


def parallel(self, other):
    """This function builds an automaton corresponding
    to the parallel composition  of the input automata.
    It selects the adequate function to build the parallel
    composition  automaton depending if the input automata
    are deterministic. If they are, it uses paralleltdet,
    otherwise uses parallelnondet
    """
    from .automatadefs import fsa
    # if one of the automata is empty the result is empty
    if self.empty or other.empty:
        return fsa()
    # case deterministic, method is_dfa is used
    if self.is_dfa() and other.is_dfa():
        return paralleldet(self, other)
    else:  # case non deterministic
        return parallelnondet(self, other)


def product(self, other):
    """This function builds an automaton corresponding
    to the product of the input automata. It selects
    the adequate function to build the product automaton
    depending if the input automata are deterministic. If
    they are, it uses productdet, otherwise uses
    productnondet

    Example
    -------
    syms('a b c d e f s1 s2 s3 s4')
    table=[(a,'\\alpha'),(b,'\\beta'),(c,'c_c'),(s1,'x_1'),(s2,'x_2'),(s3,'x_3'),(s4,'y_4')]
    X1=[s1,s2,s3,s4]
    E1=[a,b,c]
    Transition1=[(s1,a,s2),(s2,b,s3),(s3,c,s4),(s1,b,s4)]
    X0=[s1]
    Xm=[s2,s3,s4]
    H1=fsa(X1,E1,Transition1,X0,Xm,table,name='$G_1$')
    X2=[s1,s2,s3,s4]
    E2=[a,b,c,d,e,f]
    Transition2=[(s1,a,s2),(s2,e,s3),(s3,f,s4),(s1,b,s3),(s1,f,s4),(s2,f,s4)]
    X0,Xm=[s1],[s1,s2]
    H2=fsa(X2,E2,Transition2,X0,Xm,table,name='$G_2$')
    P = product(H1,H2)
    draw(P)
    """
    from .automatadefs import fsa
    # if one of the automata is empty the result is empty
    if self.empty or other.empty:
        return fsa()
    # case deterministic, method is_dfa is used
    if self.is_dfa() and other.is_dfa():
        return productdet(self, other)
    else:  # case non deterministic
        return productnondet(self, other)


def epsilonobserver(self):
    """ This function calculates a deterministic automaton
    which marks and generates the projection of the marked and
    generated languages of the input automaton G over the alphabet
    Sigma - set([epsilon]). It returns the determinized automaton
    with the same languages as the input automaton"""
    # drawing epsilon event from Sigma
    events_noneps = self.Sigma - EMPTYSTRINGSET
    # calculating observer
    epsobserver = observer(self, events_noneps)
    return epsobserver
