import pytest
from deslab import *
from helpers import languages, random_fsa, rngs


def test_diagnoser():
    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    X = [x1, x2, x3, x4, x5, x6, x7]
    T = [(x1, c, x2), (x1, a, x5), (x2, sf, x3), (x3, e, x4), (x4, d, x4),
         (x5, b, x6), (x6, d, x6), (x7, e, x7), (x3, a, x7)]
    G = fsa(X, [a, b, c, d, e, sf], T, [x1], [], Sigobs=[a, b, c, d, e], name='$G$')
    D = diagnoser(G, sf)
    assert D.is_dfa()
    assert D.X0 == {frozenset({(x1, 'N')})}
    after_c = D.delta(list(D.X0)[0], c)
    assert after_c == frozenset({(x2, 'N'), (x3, 'Y')})
    assert D.delta(D.delta(after_c, e), d) == frozenset({(x4, 'Y')})
    assert D.symDict[after_c] == r'\{x2N,x3Y\}'
    assert diagnoser(G, [sf], [a, b, c, d, e]) == D
    with pytest.raises(invalidArgument):
        diagnoser(G)


def test_labelfailaut():
    A = labelfailaut('f')
    assert A.X == {'Y', 'N'} and A.X0 == {'N'} and A.Sigobs == frozenset()
    assert A.delta('N', 'f') == 'Y' and A.delta('Y', 'f') == 'Y'


def test_observerdelta():
    G = fsa(['x0', 'x1', 'x2'], ['a', 'u'],
            [('x0', 'a', 'x1'), ('x1', 'u', 'x2'), ('x2', 'u', 'x1')], ['x0'], [], Sigobs=['a'])
    O = observerdelta(G)
    assert len(O) == 2 and '\\Delta' in O.Sigma
    loops = [s for s in O.X if '\\Delta' in O.Gamma(s)]
    assert loops == [r'\{x1,x2\}']


def simple_plant():
    # a: controllable, u: uncontrollable
    G = fsa(['x0', 'x1', 'x2'], ['a', 'u'], [('x0', 'a', 'x1'), ('x1', 'u', 'x2')],
            ['x0'], ['x0', 'x1', 'x2'], Sigcon=['a'], name='G')
    H = fsa(['y0', 'y1'], ['a', 'u'], [('y0', 'a', 'y1')], ['y0'], ['y0', 'y1'], name='H')
    return G, H


def test_allevents():
    G, H = simple_plant()
    G = G.setpar(table=[('a', '\\alpha')])
    E = allevents(G)
    assert len(E.X) == 1 and E.X0 == E.Xm == E.X
    s = list(E.X)[0]
    assert E.Sigma == G.Sigma and E.Gamma(s) == G.Sigma
    assert all(E.delta(s, e) == s for e in G.Sigma)
    assert E.Sigcon == {'a'} and E.Sigobs == G.Sigobs
    assert E.symDict['a'] == '\\alpha'
    assert G <= E  # L(G) is contained in Sigma^*
    # no controllable or observable events in G
    F = allevents(G.setpar(Sigcon=[], Sigobs=[]))
    assert F.Sigcon == frozenset() and F.Sigobs == frozenset()
    assert allevents(fsa()).Sigma == frozenset()


def test_supcontrollable_simple():
    G, H = simple_plant()
    assert not iscontrollable(H, G)
    assert not is2controllable(H, G)
    for K in (supcontrollable(H, G), supcontrollablegeneral(H, G), supcontrollablepfclosed(H, G)):
        assert languages(K, 4)[1] == {()}
    Hok = fsa(['y0', 'y1', 'y2'], ['a', 'u'], [('y0', 'a', 'y1'), ('y1', 'u', 'y2')], ['y0'],
              ['y0', 'y1', 'y2'])
    assert iscontrollable(Hok, G) and is2controllable(Hok, G)


@pytest.mark.parametrize('rng', rngs(40))
def test_supcontrollable_algorithms_agree(rng):
    # prefix closed specification and plant: both algorithms must give the same language
    G = random_fsa(rng, nstates=4, events=('a', 'b', 'u'), pm=1.0, Sigcon=['a', 'b'])
    # specification contained in L(G), as required by the prefix closed formula
    H = pclosure(random_fsa(rng, nstates=3, events=('a', 'b', 'u')) & G)
    if H.empty:
        return
    Kg = supcontrollablegeneral(H, G)
    Kp = supcontrollablepfclosed(H, G)
    assert are_langequiv(Kg, Kp)
    if not Kg.empty:
        assert iscontrollable(Kg, G)
        assert Kg <= H


def test_supcontrollable_violation_after_trim():
    """ two machines and an AGV: trim deletes the blocking states 6
    and 7, and then state 5 violates controllability (its
    uncontrollable event b1 goes to 6), so another iteration is needed """
    syms('I B E m1 m2 a1 b1 a2 b2 c')
    M1 = fsa([I, B], [a1, b1], [(I, a1, B), (B, b1, I)], [I], [I], Sigcon=[a1])
    M2 = fsa([I, B], [a2, b2], [(I, a2, B), (B, b2, I)], [I], [I], Sigcon=[a2])
    AGV = fsa([E, m1, m2], [b1, a2, b2, c], [(E, b1, m1), (m1, a2, E), (E, b2, m2), (m2, c, E)],
              [E], [E], Sigcon=[a2])
    G = M1 // M2 // AGV
    K = supcontrollable(G, G)
    assert iscontrollable(K, G)
    assert K == trim(K)
    assert len(K) == 6
    assert supcontrollablegeneral(G, G).X == trim(supcontrollablegeneral(G, G)).X


def test_factory_example():
    """ example_supervisorio.py of the original DESlab """
    syms('x0 x1 y0 y1 z0 z1 z2 z3 xh10 xh11 xh20 xh21 e1 e2 e3 e4 e5 e60 e80 e62 e82')
    G1 = fsa([x0, x1], [e1, e2], [(x0, e1, x1), (x1, e2, x0)], [x0], [x0], name='$G_{M1}$')
    G2 = fsa([y0, y1], [e3, e4], [(y0, e3, y1), (y1, e4, y0)], [y0], [y0], name='$G_{M2}$')
    G3 = fsa([z0, z1, z2, z3], [e5, e62, e82, e80, e60],
             [(z0, e5, z1), (z1, e60, z2), (z2, e62, z0), (z1, e80, z3), (z3, e82, z0)],
             [z0], [z0], name='$G_{ut}$')
    G = (G1 // G2 // G3).setpar(Sigcon=set([e1, e3, e5]))
    H1 = fsa([xh10, xh11], [e2, e82, e3], [(xh10, e2, xh11), (xh10, e82, xh11), (xh11, e3, xh10)],
             [xh10], [xh10, xh11])
    H2 = fsa([xh20, xh21], [e4, e5], [(xh20, e4, xh21), (xh21, e5, xh20)], [xh20], [xh20, xh21])
    R = (G // H1 // H2).renamestates('number')
    G = G.renamestates('number')
    K = supcontrollable(R, G)
    assert not K.empty
    assert iscontrollable(K, G)
    assert K <= R
    assert K.name == r'$K^{\uparrow C}$'


def test_nonconflict_examples():
    syms('x0 x1 x2 a b')
    G1 = fsa([x0, x1, x2], [a, b], [(x0, a, x1), (x1, b, x2)], [x0], [x2])
    G2 = fsa([x0, x1, x2], [a, b], [(x0, b, x1), (x1, a, x2)], [x0], [x2])
    assert not nonconflict(G1, G2)          # G1 marks ab and G2 marks ba
    assert nonconflict(G1, G1) and nonconflict(G1, allevents(G1))
    blocking = G1.addtransition([x0, b, x0]).addtransition([x1, a, x0]).deletetransition((x1, b, x2))
    assert not nonconflict(blocking, allevents(blocking))
    assert nonconflict(fsa(), G1)


def test_nonconflict_transfer_line():
    """ modular control of the transfer line (TCT example): the modular
    supervisors are conflicting and the coordinator removes the conflict """
    syms('D O B0 B1 e1 t1 e2 t2 e3 t3 r')
    M1 = fsa([D, O], [e1, t1], [(D, e1, O), (O, t1, D)], [D], [D], Sigcon=[e1])
    M2 = fsa([D, O], [e2, t2], [(D, e2, O), (O, t2, D)], [D], [D], Sigcon=[e2])
    TU = fsa([D, O], [e3, t3, r], [(D, e3, O), (O, t3, D), (O, r, D)], [D], [D], Sigcon=[e3])
    E1 = fsa([B0, B1], [t1, r, e2], [(B0, t1, B1), (B0, r, B1), (B1, e2, B0)], [B0], [B0], Sigcon=[e2])
    E2 = fsa([B0, B1], [t2, e3], [(B0, t2, B1), (B1, e3, B0)], [B0], [B0], Sigcon=[e3])
    G = M1 // M2 // TU
    ALL = allevents(G)
    SUP1, SUP2 = supcontrollable(G // E1, G), supcontrollable(G // E2, G)
    assert nonconflict(SUP1, ALL) and nonconflict(SUP2, ALL)
    assert not nonconflict(SUP1, SUP2)
    P = SUP1 // SUP2
    CO = supcontrollable(P, P)
    assert nonconflict(CO // SUP1 // SUP2, ALL)
    assert are_isomorphic(CO // SUP1 // SUP2, supcontrollable(G // E1 // E2, G))


@pytest.mark.parametrize('rng', rngs(100))
def test_nonconflict_languages(rng):
    # for trim automata with the same events: pre(Lm1) & pre(Lm2) == pre(Lm1 & Lm2)
    G1 = trim(random_fsa(rng, nstates=4, events=('a', 'b'), pm=0.5))
    G2 = trim(random_fsa(rng, nstates=4, events=('a', 'b'), pm=0.5))
    if G1.empty or G2.empty or G1.Sigma != G2.Sigma:
        return
    meet = G1 & G2
    left = pclosure(G1) & pclosure(G2)
    right = pclosure(trim(meet)) if not trim(meet).empty else fsa()
    same = (left.empty and right.empty) or (not left.empty and not right.empty
                                              and are_langequiv(left, right))
    assert nonconflict(G1, G2) == same
