"""Language level checks of the operations, using random automata."""
import pytest
from deslab import *
from helpers import (languages, projected_languages, strings, P, random_fsa, rngs)

N = 6


@pytest.mark.parametrize('rng', rngs(30))
def test_accessibility_and_trim(rng):
    G = random_fsa(rng, nstates=5)
    L, Lm = languages(G, N)
    A = ac(G)
    assert languages(A, N) == (L, Lm)
    C = coac(G)
    assert languages(C, N)[1] == Lm
    T = trim(G)
    assert languages(T, N)[1] == Lm
    if not T.empty:
        assert ac(T).X == T.X and coac(T).X == T.X
    # in a trim automaton with 5 states every prefix is completed with at most 4 events
    prefixes = {s[:k] for s in languages(T, N + 4)[1] for k in range(min(len(s), N) + 1)}
    assert languages(pclosure(G), N)[1] == prefixes


@pytest.mark.parametrize('rng', rngs(30))
@pytest.mark.parametrize('det', [True, False])
def test_product(rng, det):
    G1 = random_fsa(rng, det=det, eps=not det)
    G2 = random_fsa(rng, det=det)
    L1, Lm1 = languages(G1, N)
    L2, Lm2 = languages(G2, N)
    Pr = G1 & G2
    assert languages(Pr, N) == (L1 & L2, Lm1 & Lm2)


@pytest.mark.parametrize('rng', rngs(30))
@pytest.mark.parametrize('det', [True, False])
def test_parallel(rng, det):
    G1 = random_fsa(rng, events=('a', 'b', 'c'), det=det, eps=not det)
    G2 = random_fsa(rng, events=('b', 'c', 'd'), det=det)
    L1, Lm1 = languages(G1, N)
    L2, Lm2 = languages(G2, N)
    Pa = G1 // G2
    L, Lm = languages(Pa, N)
    S1, S2 = G1.Sigma, G2.Sigma
    for s in strings(S1 | S2, N - 1):
        assert (s in L) == (P(s, S1) in L1 and P(s, S2) in L2)
        assert (s in Lm) == (P(s, S1) in Lm1 and P(s, S2) in Lm2)



def test_parallel_flat_states():
    syms('I B E m1 m2 a1 b1 a2 b2 c')
    tab = [(m1, 'M_1'), (m2, 'M_2')]
    M1 = fsa([I, B], [a1, b1], [(I, a1, B), (B, b1, I)], [I], [I])
    M2 = fsa([I, B], [a2, b2], [(I, a2, B), (B, b2, I)], [I], [I])
    AGV = fsa([E, m1, m2], [b1, a2, b2, c], [(E, b1, m1), (m1, a2, E), (E, b2, m2), (m2, c, E)],
              [E], [E], tab)
    G = M1 // M2 // AGV
    assert all(isinstance(x, tuple) and len(x) == 3 for x in G.X)
    assert G.X0 == {(I, I, E)} and G.Xm == {(I, I, E)}
    assert G == M1 // (M2 // AGV)                     # the result does not depend on the grouping
    assert G.symDict[(I, I, m1)] == '(I,I,M_1)'       # flat latex labels
    nested = parallel(M1 // M2, AGV, flat=False)
    assert all(len(x) == 2 and len(x[0]) == 2 for x in nested.X)
    assert are_isomorphic(G, nested)
    # (G // G) has states with 6 components
    assert all(len(x) == 6 for x in (G // G).X)


def test_parallel_flat_mixed_states():
    """ an operand whose states are not tuples of a single length is
    not flattened, so that different states keep different names """
    G1 = fsa(['a', ('a', 'b')], ['u', 'v'], [('a', 'u', ('a', 'b')), (('a', 'b'), 'v', 'a')],
             ['a'], ['a'])
    G2 = fsa([('b', 'c'), 'c'], ['v', 'w'], [(('b', 'c'), 'w', 'c'), ('c', 'v', ('b', 'c'))],
             [('b', 'c')], ['c'])
    P = G1 // G2
    assert len(P) == len(parallel(G1, G2, flat=False))
    assert are_isomorphic(P, parallel(G1, G2, flat=False))
    assert ('a', ('b', 'c')) in P.X


@pytest.mark.parametrize('rng', rngs(30))
@pytest.mark.parametrize('det', [True, False])
def test_parallel_flat_is_isomorphic_to_pairs(rng, det):
    G1 = random_fsa(rng, events=('a', 'b', 'c'), det=det, eps=not det)
    G2 = random_fsa(rng, events=('b', 'c', 'd'), det=det)
    G3 = random_fsa(rng, nstates=3, events=('a', 'd'), det=det)
    flat = G1 // G2 // G3
    pairs = parallel(parallel(G1, G2, flat=False), G3, flat=False)
    assert are_isomorphic(flat, pairs)
    assert all(len(x) == 3 for x in flat.X)


def test_diagnoser_of_a_composed_plant():
    syms('x0 x1 y0 y1 a b sf')
    G1 = fsa([x0, x1], [a, sf], [(x0, sf, x1), (x1, a, x1), (x0, a, x0)], [x0], [], Sigobs=[a])
    G2 = fsa([y0, y1], [b], [(y0, b, y1), (y1, b, y0)], [y0], [], Sigobs=[b])
    D = diagnoser(G1 // G2, sf)
    assert D.is_dfa()
    assert all(isinstance(x, tuple) and len(x) == 2 and x[1] in ('N', 'Y')
               for xd in D.X for x in xd)

@pytest.mark.parametrize('rng', rngs(30))
def test_union(rng):
    G1 = random_fsa(rng, events=('a', 'b'))
    G2 = random_fsa(rng, events=('b', 'c'), det=False)
    U = G1 + G2
    assert languages(U, N)[1] == languages(G1, N)[1] | languages(G2, N)[1]
    U2 = union(G1, G2, False)
    assert languages(U2, N)[1] == languages(G1, N)[1] | languages(G2, N)[1]
    # when one language is empty the other automaton is returned unchanged
    if not (isitempty(G1) or isitempty(G2)):
        assert U.is_dfa()


@pytest.mark.parametrize('rng', rngs(30))
def test_concatenation(rng):
    G1 = random_fsa(rng, events=('a', 'b'))
    G2 = random_fsa(rng, events=('b', 'c'))
    Lm1, Lm2 = languages(G1, N)[1], languages(G2, N)[1]
    C = G1 * G2
    expected = {u + v for u in Lm1 for v in Lm2 if len(u + v) <= N}
    assert languages(C, N)[1] == expected


@pytest.mark.parametrize('rng', rngs(30))
def test_kleene_closure(rng):
    G = random_fsa(rng, events=('a', 'b'))
    Lm = languages(G, N)[1] - {()}
    K = kleeneclos(G)
    memo = {(): True}

    def inK(s):
        if s not in memo:
            memo[s] = any(s[:k] in Lm and inK(s[k:]) for k in range(1, len(s) + 1))
        return memo[s]
    assert languages(K, N)[1] == {s for s in strings(G.Sigma, N) if inK(s)}
    assert K.is_dfa()


@pytest.mark.parametrize('rng', rngs(30))
@pytest.mark.parametrize('det', [True, False])
def test_complement(rng, det):
    G = random_fsa(rng, det=det, eps=not det)
    Lm = languages(G, N)[1]
    C = ~G
    assert languages(C, N)[1] == set(strings(G.Sigma, N)) - Lm


@pytest.mark.parametrize('rng', rngs(30))
def test_langdiff(rng):
    G1 = random_fsa(rng, events=('a', 'b', 'c'))
    G2 = random_fsa(rng, events=('a', 'b'), det=False)
    D = G1 - G2
    assert languages(D, N)[1] == languages(G1, N)[1] - languages(G2, N)[1]


@pytest.mark.parametrize('rng', rngs(30))
def test_langquotient(rng):
    G1 = random_fsa(rng, events=('a', 'b'))
    G2 = random_fsa(rng, events=('a', 'b'), acyclic=True)  # finite language
    Lm2 = languages(G2, 4)[1]
    Lm1 = languages(G1, N + 4)[1]
    Q = G1 / G2
    expected = {s for s in strings(G1.Sigma, N) if any(s + t in Lm1 for t in Lm2)}
    assert languages(Q, N)[1] == expected


@pytest.mark.parametrize('rng', rngs(30))
@pytest.mark.parametrize('det', [True, False])
def test_observer_and_projection(rng, det):
    G = random_fsa(rng, nstates=5, events=('a', 'b', 'u', 'v'), det=det, eps=not det)
    obs = ['a', 'b']
    expected = projected_languages(G, obs, N)
    O = observer(G, obs)
    assert O.is_dfa()
    assert languages(O, N) == expected
    Pj = proj(G, obs)
    assert languages(Pj, N) == expected
    assert Pj.Sigma == frozenset(obs)


@pytest.mark.parametrize('rng', rngs(20))
def test_epsilonobserver(rng):
    G = random_fsa(rng, det=False, eps=True)
    E = epsilonobserver(G)
    assert E.is_dfa() and epsilon not in E.Sigma
    assert languages(E, N) == languages(G, N)


@pytest.mark.parametrize('rng', rngs(20))
def test_invproj(rng):
    G = random_fsa(rng, events=('a', 'b'))
    I = invproj(G, ['c', 'd'])
    L, Lm = languages(G, N)
    LI, LmI = languages(I, N)
    for s in strings(['a', 'b', 'c', 'd'], N - 1):
        assert (s in LI) == (P(s, {'a', 'b'}) in L)
        assert (s in LmI) == (P(s, {'a', 'b'}) in Lm)


def test_complete_and_isitcomplete():
    G = fsa(['x', 'y'], ['a', 'b'], [('x', 'a', 'y')], ['x'], ['y'])
    assert not isitcomplete(G)
    C = complete(G)
    assert isitcomplete(C)
    assert languages(C, N)[1] == languages(G, N)[1]
    assert languages(C, 3)[0] == set(strings(['a', 'b'], 3))


def test_sigmakleeneclos():
    K = sigmakleeneclos(['a', 'b'])
    assert languages(K, 3)[1] == set(strings(['a', 'b'], 3))
    E = sigmakleeneclos([])
    assert languages(E, 3)[1] == {()}


def test_operations_with_empty_automaton():
    G = fsa(['x'], ['a'], [('x', 'a', 'x')], ['x'], ['x'])
    E = fsa()
    assert (G & E).empty and (G // E).empty and (G * E).empty
    assert languages(G + E, 3) == languages(G, 3)
    assert (E - G).empty and languages(G - E, 3) == languages(G, 3)
    assert languages(~E, 0)[1] == {()}
