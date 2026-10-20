"""Comparison functions for the automata objects"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    MIT license (see LICENSE).

import warnings
from .def_const import *
from .exceptions import *
from .algorithms import ac, trim, complement, union


def isitempty(self):
    """This function determines whether or not the language marked by automaton
    G is empty. It uses a DFS for searching marked states that are reachable
    from the initial state.

    Example
    -------
    syms('a b c x1 x2 x3 x4')
    X1=[x1,x2,x3,x4]
    Sigma=[a,b,c]
    T=[(x1,a,x2),(x2,b,x3),(x3,c,x4)]
    X0,Xm=[x1],[x2]
    H1=fsa(X1,Sigma,T,X0,Xm,name='$G_1$')
    print(isitempty(H1)) # returns the booleans value of the emptiness test
    """
    if self.empty:
        return True
    else:
        auto = ac(self)
        return auto.Xm == EMPTYSET


def _standardize(self, other):
    """ returns copies of the input automata defined over the
    union of their alphabets (epsilon is not added)"""
    A = self.addevents((other.Sigma - self.Sigma) - EMPTYSTRINGSET)
    B = other.addevents((self.Sigma - other.Sigma) - EMPTYSTRINGSET)
    return A, B


def issublanguage(self, other):
    """ This funtion determines whether or not the language marked by
    automaton G1 is contained in the language marked by
    automaton G2, i.e. if Lm(G1) <= Lm(G2). It implements the <= and
    >= comparison operators.

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
    print(issublanguage(G1,G2), G1<=G2)
    draw(G1,G2)
    """
    # G1 represents an empty language
    if isitempty(self):
        return True
    # G1 represents a nonempty language and G2 do.
    elif isitempty(other):
        return False
    # G1 and G2 represent nonempty languages
    if (self.Sigma - EMPTYSTRINGSET) != (other.Sigma - EMPTYSTRINGSET):
        # it is necessary to standarsize the alphabets
        # in the case of  G1.Sigma <> G2.Sigma
        # a warning will be generated
        warnings.warn('input automata have different alphabets. They have been standarsized to compare')
        A, B = _standardize(self, other)
    else:
        # in this case the input automata have
        # the same alphabet
        A, B = self, other
    B_complement = ~B
    I = A & B_complement
    inclusion_test = isitempty(I)
    return inclusion_test


def are_automataequal(self, other):
    """ This function implements the equality test
    for comparison between automata. The test returns
    True only if all the components of both automata
    are equal (the state set, event set, initial state
    and delta functions). If any component of G1  differs
    from the equivalent component in  automaton G2 the test
    returns false

    Example
    -------
    syms('q1 q2 q3 q4 a1 b1 e f')
    table = [(a1,'a_1'),(b1,'b_1'),(q1,'q_1'),(q2,'q_2'),(q3,'q_3'),(q4,'t_1')]
    X = [q1,q2,q3,q4]
    Sigma = [a1,b1,e]
    X0 = [q1]
    Xm = [q1,q3]
    T =[(q1,a1,q2),(q1,b1,q3),(q2,b1,q3),(q3,b1,q4)]
    G1 = fsa(X,Sigma,T,X0,Xm,table,name='$G_1$ -- example 1')
    G2 = fsa(X,Sigma,T,X0,Xm,table,name='$G_2$')
    G3 = G2.addtransition([q1,e,q2])
    print(are_automataequal(G1, G2))
    """
    # G1 represents an empty language and G2 does not
    if self.empty and not other.empty:
        return False
    # G1 and G2 represents empty languages
    elif self.empty and other.empty:
        return True
    # G1 represents a nonempty language and G2 do.
    elif not self.empty and other.empty:
        return False
    # the comparison is made between states, events
    # and delta transition function
    X1, Sigma1, delta1 = self.X, self.Sigma, self.deltaDict
    X01, Xm1 = self.X0, self.Xm
    X2, Sigma2, delta2 = other.X, other.Sigma, other.deltaDict,
    X02, Xm2 = other.X0, other.Xm
    test_equal = (X1 == X2) and (Sigma1 == Sigma2) and (delta1 == delta2)
    test_equal = test_equal and (X01 == X02) and (Xm1 == Xm2)
    return test_equal


def are_langequiv(self, other):
    """
    This function implements the language equivalence
    test between automata G1 and G2.  The test returns
    True if the input automatata mark the same
    language and False otherwise.

    Example (Example 2.23 Cassandras and Lafortune)
    -------

    syms('x1 x12 x123 x0 xnot1 x0new ')
    e1='1'
    e2='2'
    e3='3'
    X1=[x0,x1,x12,x123,xnot1]
    S=[e1,e2,e3]
    T = [(x0,e1,x1),(x0,e2,xnot1),(x0,e3,xnot1),(x1,e1,x1),(x1,e2,x12),(x1,e3,xnot1),
         (x12,e1,x1),(x12,e2,xnot1),(x12,e3,x123),(x123,e1,x1),(x123,e2,xnot1),
         (x123,e3,xnot1),(xnot1,e1,x1),(xnot1,e2,xnot1),(xnot1,e3,xnot1)]

    X0=[x0]
    Xm=[x123]
    G1=fsa(X1,S,T,X0,Xm,name='$G_1$')

    X02=[x0new]
    X2=[x0new,x1,x12,x123]
    T2 = [(x0new,e1,x1),(x0new,e2,x0new),(x0new,e3,x0new),(x1,e1,x1),(x1,e2,x12),(x1,e3,x0new),
         (x12,e1,x1),(x12,e2,x0new),(x12,e3,x123),(x123,e1,x1),(x123,e2,x0new),(x123,e3,x0new)]
    G2=fsa(X2,S,T2,X02,Xm,name='$G_2$')
    print(are_langequiv(G1,G2))
    """
    # G1 represents an empty language
    if isitempty(self) and not isitempty(other):
        return False
    # G1 and G2 represents empty languages
    elif isitempty(self) and isitempty(other):
        return True
    # G1 represents a nonempty language and G2 do.
    elif not isitempty(self) and isitempty(other):
        return False
    # if both automata are not empty we make
    # the equivalence test over the union of the alphabets
    A, B = _standardize(self, other)
    L1 = A & ~B
    L2 = B & ~A
    return isitempty(L1) and isitempty(L2)


arelangequiv = are_langequiv


def isitcomplete(self):
    """
    This function determines if the automaton G
    is complete, i.e. if any string of Sigma*
    is generated by automaton G.

    Example
    --------

    syms('x1 x12 x123 x0 xnot1 x0new ')
    e1='1'
    e2='2'
    e3='3'
    X1=[x0,x1,x12,x123,xnot1]
    S=[e1,e2,e3]
    T = [(x0,e1,x1),(x0,e2,xnot1),(x0,e3,xnot1),(x1,e1,x1),(x1,e2,x12),(x1,e3,xnot1),
         (x12,e1,x1),(x12,e2,xnot1),(x12,e3,x123),(x123,e1,x1),(x123,e2,xnot1),
         (x123,e3,xnot1),(xnot1,e1,x1),(xnot1,e2,xnot1),(xnot1,e3,xnot1)]

    X0=[x0]
    Xm=[x123]
    G1=fsa(X1,S,T,X0,Xm,name='$G_1$')
    print(isitcomplete(G1))
    """
    if not self.is_dfa():
        raise invalidArgument('automaton G is not deterministic and  completeness test is for deterministic finite automata')
    Sigma = self.Sigma - EMPTYSTRINGSET
    for state in self:
        if self.Gamma(state) != Sigma:
            return False
    return True
