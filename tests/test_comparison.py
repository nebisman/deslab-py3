import warnings
import pytest
from deslab import *
from helpers import languages, random_fsa, rngs

N = 6


def test_cassandras_example_2_23():
    syms('x1 x12 x123 x0 xnot1 x0new')
    e1, e2, e3 = '1', '2', '3'
    T = [(x0, e1, x1), (x0, e2, xnot1), (x0, e3, xnot1), (x1, e1, x1), (x1, e2, x12), (x1, e3, xnot1),
         (x12, e1, x1), (x12, e2, xnot1), (x12, e3, x123), (x123, e1, x1), (x123, e2, xnot1),
         (x123, e3, xnot1), (xnot1, e1, x1), (xnot1, e2, xnot1), (xnot1, e3, xnot1)]
    G1 = fsa([x0, x1, x12, x123, xnot1], [e1, e2, e3], T, [x0], [x123], name='$G_1$')
    T2 = [(x0new, e1, x1), (x0new, e2, x0new), (x0new, e3, x0new), (x1, e1, x1), (x1, e2, x12),
          (x1, e3, x0new), (x12, e1, x1), (x12, e2, x0new), (x12, e3, x123), (x123, e1, x1),
          (x123, e2, x0new), (x123, e3, x0new)]
    G2 = fsa([x0new, x1, x12, x123], [e1, e2, e3], T2, [x0new], [x123], name='$G_2$')
    assert are_langequiv(G1, G2)
    assert G1 <= G2 and G2 <= G1 and G1 >= G2
    assert G1 != G2
    assert isitcomplete(G1) and isitcomplete(G2)
    G3 = G2.deletetransition((x12, e3, x123))
    assert not are_langequiv(G1, G3)
    assert G3 <= G1 and not (G1 <= G3)


@pytest.mark.parametrize('rng', rngs(40))
def test_comparisons_are_consistent_with_bounded_languages(rng):
    G1 = random_fsa(rng, nstates=3, events=('a', 'b'))
    G2 = random_fsa(rng, nstates=3, events=('a', 'b'), det=False)
    Lm1, Lm2 = languages(G1, N)[1], languages(G2, N)[1]
    sub = issublanguage(G1, G2)
    if sub:
        assert Lm1 <= Lm2
    if not Lm1 <= Lm2:
        assert not sub
    eq = are_langequiv(G1, G2)
    if eq:
        assert Lm1 == Lm2
    if Lm1 != Lm2:
        assert not eq
    assert are_langequiv(G1, G1.renamestates('number'))
    assert are_langequiv(G2, epsilonobserver(G2))
    # a nonempty language of a 3 state automaton has a string of length <= 2
    assert isitempty(G1) == (Lm1 == set())
    assert isitempty(G2) == (Lm2 == set())


def test_different_alphabets_warning():
    G1 = fsa(['x'], ['a'], [('x', 'a', 'x')], ['x'], ['x'])
    G2 = fsa(['y'], ['a', 'b'], [('y', 'a', 'y'), ('y', 'b', 'y')], ['y'], ['y'])
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        assert G1 <= G2
        assert not (G2 <= G1)
        assert any('different alphabets' in str(x.message) for x in w)


def test_ispfclosed():
    G = fsa(['x', 'y'], ['a'], [('x', 'a', 'y')], ['x'], ['x', 'y'])
    assert ispfclosed(G)
    assert not ispfclosed(G.setpar(Xm=['y']))
    assert ispfclosed(pclosure(G.setpar(Xm=['y'])))
