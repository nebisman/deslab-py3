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


def _brute_force_isomorphic(G1, G2):
    """isomorphism test trying every bijection between the states"""
    import itertools
    if G1.empty or G2.empty:
        return G1.empty and G2.empty
    if len(G1) != len(G2) or G1.Sigma != G2.Sigma:
        return False
    X1 = list(G1.X)
    T1 = {(x, e, y) for x, y, e in G1.Graph.edges(keys=True)}
    T2 = {(x, e, y) for x, y, e in G2.Graph.edges(keys=True)}
    for image in itertools.permutations(list(G2.X)):
        f = dict(zip(X1, image))
        if ({f[x] for x in G1.X0} == G2.X0 and {f[x] for x in G1.Xm} == G2.Xm
                and {(f[x], e, f[y]) for x, e, y in T1} == T2):
            return True
    return False


def test_are_isomorphic_examples():
    syms('p q x y a b q1 q2 q3 q4')
    # numbering the states in the order of their names is not enough
    G1 = fsa([p, q], [a], [(p, a, q)], [p], [q])
    G2 = fsa([x, y], [a], [(y, a, x)], [y], [x])
    assert are_isomorphic(G1, G2) and are_isomorhic(G1, G2)
    T = [(q1, a, q2), (q1, b, q3), (q2, b, q3), (q3, b, q4), (q4, a, q1)]
    F = fsa([q1, q2, q3, q4], [a, b], T, [q1], [q1, q3])
    assert are_isomorphic(F, F.renamestates({q1: 'z', q2: 'y', q3: 'x', q4: 'w'}))
    assert are_isomorphic(F, F.renamestates('number'))
    assert not are_isomorphic(F, F.setpar(Xm=[q1, q2]))
    assert not are_isomorphic(F, F.addtransition([q4, b, q2]))
    assert not are_isomorphic(F, F.renamevents({a: b, b: a}))
    assert not are_isomorphic(F, F.deletetransition((q4, a, q1)).addtransition([q4, a, q2]))
    # nondeterministic automata and non accessible states
    N = fsa([q1, q2, q3], [a, b], [(q1, a, q2), (q1, a, q3), (q2, b, q1)], [q1], [q3])
    assert are_isomorphic(N, N.renamestates({q1: 'u', q2: 'v', q3: 'w'}))
    assert not are_isomorphic(N, N.renamestates({q1: 'u', q2: 'v', q3: 'w'}).setpar(X0=['v']))
    U = fsa([q1, q2, q3, q4], [a, b], [(q1, a, q2), (q2, b, q1), (q3, a, q4)], [q1], [q1])
    assert are_isomorphic(U, U.renamestates({q3: 0, q4: 1}))
    assert not are_isomorphic(U, ac(U))
    assert are_isomorphic(fsa(), fsa()) and not are_isomorphic(fsa(), F)


def test_are_isomorphic_parallel_composition():
    syms('I B E m1 m2 a1 b1 a2 b2 c')
    M1 = fsa([I, B], [a1, b1], [(I, a1, B), (B, b1, I)], [I], [I])
    M2 = fsa([I, B], [a2, b2], [(I, a2, B), (B, b2, I)], [I], [I])
    AGV = fsa([E, m1, m2], [b1, a2, b2, c], [(E, b1, m1), (m1, a2, E), (E, b2, m2), (m2, c, E)], [E], [E])
    G = M1 // M2 // AGV
    assert G != AGV // M2 // M1
    assert are_isomorphic(G, AGV // M2 // M1)
    assert not are_isomorphic(G, trim(G))


@pytest.mark.parametrize('rng', rngs(60))
def test_are_isomorphic_brute_force(rng):
    n = rng.randint(1, 5)
    G = random_fsa(rng, nstates=n, events=('a', 'b'), det=rng.random() < 0.7, p=0.6)
    if rng.random() < 0.5:
        G = ac(G)
    if G.empty:
        return
    names = list(range(len(G)))
    rng.shuffle(names)
    H = G.renamestates(dict(zip(sorted(G.X), names)))
    assert are_isomorphic(G, H)
    X, Sigma = sorted(H.X), sorted(H.Sigma)
    for K in (H.setpar(Xm=set(H.Xm) ^ {rng.choice(X)}),
              H.addtransition([rng.choice(X), rng.choice(Sigma), rng.choice(X)])):
        assert are_isomorphic(G, K) == _brute_force_isomorphic(G, K) == are_isomorphic(K, G)
