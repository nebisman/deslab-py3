"""Base class for automata."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    MIT license (see LICENSE).

import copy
import networkx as nx
from .exceptions import *
from .def_const import *
from .utilities import _sorted


__author__ = """\n""".join(['Leonardo Bermeo (lbermeoc@unal.edu.co)',
                            'Joao Carlos Basilio (basilio@poli.ufrj.br)'])


# graphic properties (fill color, line color, style) used by default
# for each type of automaton. Colors are xcolor names defined in the
# LaTeX preambles, the number is the intensity (percentage of color)
GRAPHIC_TYPES = {'plant':         (['blue', 15], ['blue', 60], 'normal'),
                 'result':        (['plantfill', 76], ['plantline', 85], 'normal'),
                 'supervisor':    (['superfill', 80], ['superline', 60], 'normal'),
                 'specification': (['specfill', 50], ['specline', 60], 'normal'),
                 'observer':      (['plantfill', 80], ['plantline', 60], 'rectangle')}
GRAPHIC_DEFAULT = (['blue', 15], ['blue', 60], 'circle')


def _isdefault(arg):
    """True if a parameter was not given (None or the empty list)"""
    return arg is None or (isinstance(arg, list) and arg == [])


class fsa:
    """
    This instruction defines an automaton object inside DESlab.

    Parameters
    ----------

    X :  list containing the symbols corresponding to states
    Sigma : list of symbols of the input alphabet
    T : list of transitions ordered as tuples.
    X0 : list of initial states
    Xm : list of marked states
    table : list of association tuples between symbols and
            latex labels.
    Sigobs : list of observable events
    Sigcon : list of controllable events
    name : a string that represents the name of the system
    type : a string that represents the type of the system

    Example
    -------

    syms('q1 q2 q3 a1 b1 e')
    table = [(a1,'\\alpha_1'),(b1,'\\beta_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
    X = [q1,q2,q3]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,b1,q2),(q2,b1,q3),(q2,e,q3),(q3,a1,q1),(q2,a1,q2)]
    G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
    draw(G1)
    """

    def __init__(self, X=[], Sigma=[], transition=[], X0=[], Xm=[],
                 table=[], Sigobs=[], Sigcon=[], name='untitled', type='plant'):
        """
        this is the constructor of the automaton class"""
        if _isdefault(X) or _isdefault(X0):  # in the case of empty automaton
            self._init_empty()
            return
        X = frozenset(X)  # we use frozensets instead of sets
        X0 = verify_fsa_definition(X, frozenset(Sigma), frozenset(Xm), X0)
        if (X == EMPTYSET) or (X0 == EMPTYSET):  # in the case of empty automaton
            self._init_empty()
            return
        # in the case of nonempty automaton
        self.X = X
        self.Sigma = frozenset(Sigma)
        self.Xm = frozenset(Xm)
        self.X0 = X0  # verification of parameters passed
        self.name = name  # external properties
        self.empty = False
        self.type = type
        # observable and controllable events
        if _isdefault(Sigobs):
            self.Sigobs = self.Sigma  # default observable events is Sigma
        else:
            self.Sigobs = frozenset(Sigobs) & self.Sigma
        self.Sigobs = self.Sigobs - EMPTYSTRINGSET
        if _isdefault(Sigcon):
            self.Sigcon = self.Sigma  # default controllable events is Sigma
        else:
            self.Sigcon = frozenset(Sigcon) & self.Sigma
        # constructors of Graph class and
        self.Graph = create_graph(transition, self.X, self.Sigma)
        # delta and Gamma data structures
        self._rebuild()
        # symbolic latex labels
        self.symDict = create_table(self.X, self.Sigma, table)  # symbol dictionary
        # Basic graphic properties
        self._init_graphics()
        return

    def _init_empty(self):
        """ Data of the empty automaton, the one that does not
        generate any string."""
        self.X0 = EMPTYSET
        self.empty = True
        self.Sigma = EMPTYSET
        self.Xm = EMPTYSET
        self.X = EMPTYSET
        self.Sigobs = EMPTYSET
        self.Sigcon = EMPTYSET
        self.name = 'Empty Automaton'
        self.type = EMPTY
        self.Graph = nx.MultiDiGraph()
        self.gammaDict, self.deltaDict = {}, {}
        self.infoDict = {'nonDetTrans': False, 'isDFA': True, 'hasEpsilon': False}
        self.symDict = {}
        self._init_graphics()

    def _init_graphics(self):
        """ Basic graphic properties used by the draw functions"""
        self.render = 'dot'
        self.ranksep = 0.25
        self.nodesep = 0.25
        self.direction = 'LR'
        self.scale = 1
        self.FillColor, self.LineColor, self.style = copy.deepcopy(
            GRAPHIC_TYPES.get(self.type, GRAPHIC_DEFAULT))

    def _rebuild(self):
        """ Recomputes the Gamma and delta dictionaries from the
        graph of the automaton. It is called after any modification
        of the transition structure."""
        self.gammaDict, self.deltaDict, self.infoDict = create_FSA_transdicts(
            self.Graph, self.X, self.Sigma, self.X0)

    def _X0(self):
        if self.is_dfa():
            return list(self.X0)[0]
        else:
            return self.X0

    def _X(self):
        return self.X

    def _Xm(self):
        return self.Xm

    def _Sigma(self):
        return self.Sigma

    def _Sigobs(self):
        return self.Sigobs

    def _Sigcon(self):
        return self.Sigcon

    def __iter__(self):
        """Iterate over the states. Use the expression 'for n in G'.

        Returns
        -------
        niter : iterator
            An iterator over all states in the automaton.
        """
        return iter(self.X)

    def __len__(self):
        """Return the number of states of automaton G.
           Use the expression 'len(G)'.
        """
        return len(self.X)

    def info(self):
        isDFA, hasEpsilon, nonDetTrans = self.infoDict['isDFA'], self.infoDict['hasEpsilon'], self.infoDict['nonDetTrans']
        return isDFA, hasEpsilon, nonDetTrans

    def deletetransition(self, trans):
        """
        This method provides low level access to the transition
        structure of input automaton. By using this method, user
        can delete an existent transition in the automaton G. If
        the transition does not exist in G, the method raises an
        exception.

        Example
        -------

        syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
        sigma=[a,b,c,d,e,sf]
        X=[x1,x2,x3,x4,x5,x6,x7]
        X0=[x1]
        Xm=[x2,x4]
        T=[(x1,c,x2),(x1,a,x5),(x2,sf,x3),(x3,e,x4),
           (x4,d,x4),(x1,a,x5),(x5,b,x6),(x6,d,x6),(x7,e,x7),(x3,a,x7)]
        table=[(x1,'x_1'),(x2,'x_2'),(sf,'\\sigma_f')]
        G=fsa(X,sigma,T,X0,Xm,table)
        G2=G.deletetransition([x7,e,x7])
        draw(G,G2)
        """
        from .structure import deletetransition
        return deletetransition(self, trans)

    def addtransition(self, trans):
        """
        This method provides low level access to the transition
        structure of input automaton. By using this method, user
        can add a new transition (x,e,y) to the automaton G. The
        states x, y and the event e are added if they are not
        already in G.

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
        G1 = G.addtransition([x1,b,x2])

        # or alternatively:
        G1 = addtransition(G,[x1,b,x2])
        """
        from .structure import addtransition
        return addtransition(self, trans)

    def addevent(self, sigma):
        """
        This method extends the input alphabet of the automaton G1
        without modification of the transition structure of G1. It is used
        for standarsizing the alphabets in common operations of two input
        automata. The new events added are defined both controllable and
        observable. Use the method setpar to change the definition of
        these sets. sigma can be a single event or a list (set) of events.


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
        G11= G1.addevents([e,f])
        print(G11.Sigma)
        """
        from .structure import addevent
        return addevent(self, sigma)

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
        from .structure import deletevent
        return deletevent(self, sigma)

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
        from .structure import addstate
        return addstate(self, x, marked)

    def deletestate(self, x):
        """ This function deletes the state x and all the
        transitions incident on it"""
        from .structure import deletestate
        return deletestate(self, x)

    def renametransition(self, trans):
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
        from .structure import renametransition
        return renametransition(self, trans)

    def addselfloop(self, x, e):
        from .structure import addselfloop
        return addselfloop(self, x, e)

    def setpar(self, **param):
        """ This method returns a copy of the automaton with some
        parameters changed, for instance
        G2 = G.setpar(Xm=[x1], name='$G_2$', Sigobs=[a,b])
        Valid keys: Xm, X0, name, Sigcon, Sigobs, style, direction,
        table, type, scale, nodesep, ranksep, render"""
        auto = self.copy()
        for key in param.keys():
            if key == 'Xm':
                Xm = frozenset(param[key])
                if not Xm <= auto.X:
                    raise markedSetError("States %s of Xm do not belong to the state set X" % (set(Xm - auto.X)))
                auto.Xm = Xm
            elif key == 'X0':
                auto.X0 = verify_fsa_definition(auto.X, auto.Sigma, auto.Xm, param[key])
                auto._rebuild()
            elif key == 'name':
                auto.name = param[key]
            elif key == 'Sigcon':
                auto.Sigcon = frozenset(param[key])
            elif key == 'Sigobs':
                auto.Sigobs = frozenset(param[key]) - EMPTYSTRINGSET
            elif key == 'style':
                auto.style = param[key]
            elif key == 'direction':
                auto.direction = param[key]
            elif key == 'table':
                auto.symDict.update(dict(param[key]))
            elif key == 'type':
                auto.type = param[key]
                if param[key] in GRAPHIC_TYPES:
                    auto.FillColor, auto.LineColor, _ = copy.deepcopy(GRAPHIC_TYPES[param[key]])
            elif key in ('scale', 'nodesep', 'ranksep', 'render'):
                setattr(auto, key, param[key])
            else:
                raise invalidArgument('key %s does not exist' % key)
        return auto

    def __str__(self):
        lines = [str(self.name),
                 '    finite state machine',
                 '    number of states: %s' % (len(self.X)),
                 '    number of events: %s' % (len(self.Sigma)),
                 '    number of transitions: %s' % (self.Graph.size())]
        return '\n'.join(lines)

    def __repr__(self):
        if self.empty:
            return '<fsa: Empty Automaton>'
        return "<fsa %r: %d states, %d events, %d transitions>" % (
            self.name, len(self.X), len(self.Sigma), self.Graph.size())

    def _repr_svg_(self):
        """ Rich representation used by Jupyter/Colab: an automaton
        in the last line of a cell is drawn automatically."""
        try:
            from ..graphics.drawing import automaton2svg
            return automaton2svg(self)
        except Exception:
            return None

    def __delta__(self, state, event):
        """This is a special transition function  used in several methods. It keeps
         regularity on data types, and the output state is always a set"""
        if event in self.Sigma:  # valid event
            if event in self.Gamma(state):  # factible event
                x_next = self.deltaDict[state][event]
                return x_next
            else:
                return EMPTYSET  # unfactible event
        else:  # event undefined for the automaton
            raise eventMembershipError('Event %s does not belong to Sigma' % (event,))

    def unobsreach(self, Q, Sigma_o=[]):
        """ This function calculates the unobservable reach set of the set Q
        of states, Sigma_o is the set of observable events """
        if isinstance(Q, (list, set)):
            Q = frozenset(Q)
        elif not isinstance(Q, frozenset):  # a single state
            Q = frozenset([Q])
        # initial parameters
        S = list(Q)  # Stack
        UR = Q  # initial reached set
        Sigma, Sigobs = self.Sigma, self.Sigobs
        # determinig unobservable events
        if _isdefault(Sigma_o):
            Sigma_uobs = Sigma - Sigobs
        elif isinstance(Sigma_o, (list, set, frozenset)):
            Sigma_uobs = Sigma - frozenset(Sigma_o)
        else:
            raise invalidArgument('Observed set must be of type set, frozenset or list')
        # main cycle of the search algorithm
        while S != []:
            x_reached = S.pop()
            Q_next = EMPTYSET
            act_events = self.Gamma(x_reached) & Sigma_uobs
            for sigma in act_events:
                # it uses the __delta__ function which uses sets for every automaton
                Q_next = Q_next | self.__delta__(x_reached, sigma)
            for q in Q_next:
                if q not in UR:
                    UR = UR | frozenset([q])
                    S.append(q)  # stack update
        return UR

    def deltaobs(self, x, e, Sigma_o=[]):
        """ This function calculates the observable delta function of
        the state of states, Sigma_o is the set of observable events """

        Q_reached = self.unobsreach(x, Sigma_o)
        Q_next = EMPTYSET
        for q_r in Q_reached:
            if e in self.Gamma(q_r):
                Q_next = Q_next | self.__delta__(q_r, e)
        UR = self.unobsreach(Q_next, Sigma_o)
        return UR

    def delta(self, state, event):
        """ This is de definition of the delta transition function
        for deterministic and non deterministic automata.
        """
        if self.is_dfa():
            # in the case of DFA we return a symbol or None
            if event in self.Sigma:  # the event is valid
                if event in self.Gamma(state):  # the event is factible
                    x_next = self.deltaDict[state][event]
                    x_next = list(x_next)[0]
                    return x_next
                else:
                    return None  # the event is unfactible
            else:
                raise eventMembershipError('Event %s does not belong to Sigma' % (event,))
        else:
            # in the case of NDFA we return set or emptyset
            if event in self.Sigma:  # the event is valid
                if event in self.Gamma(state):
                    x_next = self.deltaDict[state][event]
                    return x_next
                else:
                    return EMPTYSET  # the event is unfactible
            else:
                raise eventMembershipError('Event %s does not belong to Sigma' % (event,))

    def Gamma(self, state):
        """ This is the active event function"""
        if not (state in self.X):
            raise stateError('State %s is not defined for this automaton' % str(state))
        return self.gammaDict.get(state, EMPTYSET)

    def renamevents(self, mapping):
        """
        This function renames the events of the input automaton
        according to the input mapping.
        The input mapping is a list or tuples as follows:
        mapping = [(old_e1, new_ e1),(old_e2,new_e2),...]
        or a dictionary {old_e1: new_e1, old_e2: new_e2,...}
        """
        from .structure import renamevents
        return renamevents(self, mapping)

    def renamestates(self, mapping):
        """
        This function allows renaming of states of the input automaton.
        The input mapping is a list of pair of the form
        mapping = [(oldstate1,newstate1),(oldstate2,newstate2)...],
        a dictionary, or one of the strings 'number' or 'letter'
        """
        from .structure import renamestates
        return renamestates(self, mapping)

    """
    ====================================================================
                       Overloaded functions of automata class
    ===================================================================

    """

    def copy(self):
        auto = copy.deepcopy(self)
        return auto

    def __and__(self, other):
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
        T1=[(s1,a,s2),(s2,b,s3),(s3,c,s4),(s1,b,s4)]
        X0=[s1]
        Xm=[s2,s3,s4]
        H1=fsa(X1,E1,T1,X0,Xm,table,name='$G_1$')
        X2=[s1,s2,s3,s4]
        E2=[a,b,c,d,e,f]
        T2=[(s1,a,s2),(s2,e,s3),(s3,f,s4),(s1,b,s3),(s1,f,s4),(s2,f,s4)]
        X0,Xm=[s1],[s1,s2]
        H2=fsa(X2,E2,T2,X0,Xm,table,name='$G_2$')
        P = H2&H1
        draw(P)
        """
        from .algorithms import product
        return product(self, other)

    def __add__(self, other):
        """
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
        U= G1+G2
        draw(G1,G2,U)
        """
        from .algorithms import union
        return union(self, other)

    __or__ = __add__

    def __floordiv__(self, other):
        """This function builds an automaton corresponding
        to the parallel composition  of the input automata.
        It selects the adequate function to build the parallel
        composition  automaton depending if the input automata
        are deterministic. If they are, it uses paralleltdet,
        otherwise uses parallelnondet

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
        P = H1//H2
        draw(P)
        """
        from .algorithms import parallel
        return parallel(self, other)

    def __mul__(self, other):
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
        Xm2 = [q3]
        T2 = [(q1,a1,q2),(q2,b1,q3)]
        G2 = fsa(X,Sigma,T2,X0,Xm2,table,name='$G_2$')
        C = G1*G2
        draw(G1,G2,C)
        """
        from .algorithms import concatenation
        return concatenation(self, other)

    def __truediv__(self, other):
        """ This function calculates an automaton that marks
        the language Lm(G1)/Lm(G2), where G1 and G2 are the input
        automata, i.e. the set of strings s such that st belongs
        to Lm(G1) for some string t in Lm(G2).

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
        Xm2 = [q3]
        T2 = [(q1,a1,q2),(q2,b1,q3)]
        G2 = fsa(X,Sigma,T2,X0,Xm2,table,name='$G_2$')
        C = G1/G2
        draw(G1,G2,C)
        """
        from .algorithms import langquotient
        return langquotient(self, other)

    __div__ = __truediv__

    def __invert__(self):
        """ This function calculates the complement of
        the language marked by the automaton G. It returns
        the automaton C such that Lm(C) = Lm(G)^C

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
        Gc= ~G1
        draw(G1,Gc)
        """
        from .algorithms import complement
        return complement(self)

    def __sub__(self, other):
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
        D= G2-G1
        draw(G1,G2,D)
        """
        from .algorithms import langdiff
        return langdiff(self, other)

    def __le__(self, other):
        """
        This funtion determines whether or not the language marked by
        automaton G1 is contained in the language marked by
        automaton G2, i.e. if Lm(G1) <= Lm(G2).

        Example
        -------

        syms('q1 q2 q3 q4 a1 b1 e f')
        table = [(a1,'a_1'),(b1,'b_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3')]
        X = [q1,q2,q3,q4]
        Sigma = [a1,b1,e]
        X0 = [q1]
        Xm = [q1,q3]
        T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3),(q3,b1,q4)]
        G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
        Xm2 = [q1,q2,q3]
        Sigma2= [a1,b1, f]
        T2 = [(q1,a1,q2),(q1,b1,q2),(q2,b1,q3),(q3,b1,q4)]
        G2 = fsa(X,Sigma2,T2,X0,Xm2,table,name='$G_2$')
        print(G1<=G2)
        draw(G1,G2)
        """
        from .comparison import issublanguage
        return issublanguage(self, other)

    def __ge__(self, other):
        """ This funtion determines whether or not the language marked by
        automaton G2 is contained in the language marked by
        automaton G1, i.e. if Lm(G1) >= Lm(G2).
        """
        from .comparison import issublanguage
        return issublanguage(other, self)

    def __eq__(self, other):
        if not isinstance(other, fsa):
            return NotImplemented
        from .comparison import are_automataequal
        return are_automataequal(self, other)

    def __ne__(self, other):
        if not isinstance(other, fsa):
            return NotImplemented
        from .comparison import are_automataequal
        return not are_automataequal(self, other)

    # automata are mutable objects compared by structure, but they
    # are hashed by identity (as in the original python 2 version)
    __hash__ = object.__hash__

    def is_dfa(self):
        return self.infoDict['isDFA']

    def has_epsilon(self):
        return self.infoDict['hasEpsilon']

    def has_nondetrans(self):
        return self.infoDict['nonDetTrans']


""" The following function are the constructors of many data structures"""


def create_graph(T, X, Sigma):
    """ This function creates a graph containing,
    the names provided by user for events, states
    """
    # we use a multidigraph for supporting the
    # transition structure of G
    Graph = nx.MultiDiGraph()
    Graph.add_nodes_from(_sorted(X))
    # we add the transitions to the graph
    for edge in T:
        try:
            x, e, y = edge
        except (TypeError, ValueError):
            raise invalidTransition('transition %s must be of the form (x,e,y)' % (edge,))
        # we revise correctnesss of T passed
        if x not in X:  # invalid state
            raise stateMembershipError("State %s in transition %s does not belong to the state set X" % (x, edge))
        if y not in X:  # invalid state
            raise stateMembershipError("State %s in transition %s does not belong to the state set X" % (y, edge))
        if e not in Sigma:
            raise eventMembershipError("Event %s in transition %s does not belong to the event set Sigma" % (e, edge))
        # we add to the graph
        if not Graph.has_edge(x, y, e):
            Graph.add_edge(x, y, key=e, label=e)
    return Graph


def create_FSA_transdicts(Graph, X, Sigma, X0):
    """ This is the constructor for Gamma function of automaton.
        It creates a dictionary for the gamma and delta functions of the automaton
    """
    infoDict = {'nonDetTrans': False, 'isDFA': True, 'hasEpsilon': False}
    if len(X0) > 1:
        infoDict['isDFA'] = False
        infoDict['nonDetTrans'] = True
    gammaDict = {}
    deltaDict = {}
    for state in Graph.nodes():
        nodeDict = {}
        for _, nextState, event in Graph.out_edges(state, keys=True):
            if event == epsilon:
                infoDict['isDFA'] = False
                infoDict['hasEpsilon'] = True
            if event in nodeDict:
                nodeDict[event] = nodeDict[event] | frozenset([nextState])
                infoDict['isDFA'] = False
                infoDict['nonDetTrans'] = True
            else:
                nodeDict[event] = frozenset([nextState])
        if nodeDict != {}:
            gammaDict[state] = frozenset(nodeDict)
            deltaDict[state] = nodeDict
    return gammaDict, deltaDict, infoDict


def verify_fsa_definition(X, Sigma, Xm, X0):
    # verifying marked states
    Xm_wrong = Xm - X
    if Xm_wrong != EMPTYSET:
        raise markedSetError("States %s of Xm do not belong to the state set X" % (set(Xm_wrong)))
    # verifying initial states
    if isinstance(X0, (list, set, frozenset)):  # a set of states
        X0 = frozenset(X0)
    else:  # a single state (string, number, tuple, ...)
        X0 = frozenset([X0])
    if not (X0 <= X):  # testing for inclusion
        raise initialStateError('Initial state set %s is not contained in state set X' % (set(X0)))
    return X0


def create_table(X, Sigma, table):
    """
    this function cleans the current table of automata.
    It deletes all the symbols that does not belong to
    Sigma or X components of the current automata
    """
    if _isdefault(table):  # no table was provided
        sym_dict = {}
    elif isinstance(table, (list, tuple)):  # a list was provided by the user
        sym_dict = dict(table)
    elif isinstance(table, dict):  # a dictionary was provided by the user or program call
        sym_dict = table.copy()
    else:  # no more options
        raise invalidArgument('table must be a list of tuples or a dictionary')
    for key in list(sym_dict.keys()):
        if key not in (X | Sigma):
            del sym_dict[key]
    if epsilon in Sigma:  # if we have a epsilon-automaton
        sym_dict.update({epsilon: '\\varepsilon'})
    return sym_dict
