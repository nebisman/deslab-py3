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
