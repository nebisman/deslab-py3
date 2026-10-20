import pytest
from deslab import *
from helpers import languages


def example():
    syms('q1 q2 q3 a1 b1 e')
    table = [(a1, '\\alpha_1'), (b1, '\\beta_1'), (q1, 'q_1'), (q2, 'q_2'), (q3, 'q_3')]
    T = [(q1, b1, q2), (q2, b1, q3), (q2, e, q3), (q3, a1, q1), (q2, a1, q2)]
    return fsa([q1, q2, q3], [a1, b1, e], T, [q1], [q1, q3], table, name='$G_1$ -- example 1')


def test_syms_injects_names():
    names = syms('p1 p2 p3')
    assert names == ['p1', 'p2', 'p3']
    assert globals()['p2'] == 'p2'
    a, b = syms('a b')
    assert (a, b) == ('a', 'b')


def test_construction():
    G = example()
    assert len(G) == 3 and set(G) == {'q1', 'q2', 'q3'}
    assert G.is_dfa() and not G.has_epsilon()
    assert G.Gamma('q1') == {'b1'}
    assert G.Gamma('q3') == {'a1'}
    assert G.delta('q1', 'b1') == 'q2'
    assert G.delta('q1', 'a1') is None
    assert G.Sigobs == G.Sigma == G.Sigcon
    assert G.symDict['q1'] == 'q_1'
    assert 'example 1' in str(G)


def test_state_without_transitions_has_empty_gamma():
    G = fsa(['x', 'y'], ['a'], [('x', 'a', 'y')], ['x'], ['y'])
    assert G.Gamma('y') == frozenset()
    with pytest.raises(stateError):
        G.Gamma('z')


def test_invalid_definitions():
    with pytest.raises(stateMembershipError):
        fsa(['x'], ['a'], [('x', 'a', 'z')], ['x'], [])
    with pytest.raises(eventMembershipError):
        fsa(['x'], ['a'], [('x', 'b', 'x')], ['x'], [])
    with pytest.raises(markedSetError):
        fsa(['x'], ['a'], [], ['x'], ['z'])
    with pytest.raises(initialStateError):
        fsa(['x'], ['a'], [], ['z'], [])


def test_empty_automaton():
    E = fsa()
    assert E.empty and E == fsa() and len(E) == 0
    assert isitempty(E)
    assert repr(E) == '<fsa: Empty Automaton>'


def test_nondeterminism_and_epsilon():
    G = fsa(['x', 'y', 'z'], ['a', epsilon], [('x', 'a', 'y'), ('x', 'a', 'z'), ('y', epsilon, 'z')],
            ['x'], ['z'])
    assert not G.is_dfa() and G.has_epsilon() and G.has_nondetrans()
    assert G.delta('x', 'a') == {'y', 'z'}
    assert epsilon not in G.Sigobs
    assert G.symDict[epsilon] == '\\varepsilon'


def test_unobsreach_and_deltaobs():
    syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')
    T = [[x1, c, x2], [x1, a, x5], [x2, sf, x3], [x3, e, x4], [x4, d, x4],
         [x5, b, x6], [x6, d, x6], [x7, e, x7], [x3, a, x7]]
    G = fsa([x1, x2, x3, x4, x5, x6, x7], [a, b, c, d, e, sf], T, [x1], [x2, x4],
            Sigobs=[a, e, d])
    assert G.unobsreach(x1) == {x1, x2, x3}
    assert G.unobsreach(x2, [a, b, c, d, e]) == {x2, x3}
    assert G.deltaobs(x2, a, [a, b, c, d, e]) == {x7}


def test_structure_operations():
    syms('q1 q2 q3 q4 a1 b1 e f')
    G = fsa([q1, q2, q3], [a1, b1], [(q1, a1, q2), (q1, b1, q3), (q2, b1, q3)], [q1], [q1, q3])
    G2 = G.addtransition([q3, e, q4])
    assert q4 in G2.X and e in G2.Sigma and G2.Gamma(q3) == {e} and q4 not in G.X
    G3 = G2.addtransition([q1, a1, q3])  # nondeterministic now
    assert not G3.is_dfa() and G3.delta(q1, a1) == {q2, q3}
    G4 = G3.deletetransition([q1, a1, q3])
    assert G4.is_dfa() and G4.delta(q1, a1) == q2
    with pytest.raises(invalidTransition):
        G.deletetransition([q1, b1, q2])
    G5 = G.addstate(q4, marked=True)
    assert q4 in G5.Xm and G5.Gamma(q4) == frozenset()
    G6 = G.deletestate(q2)
    assert G6.X == {q1, q3} and G6.Gamma(q1) == {b1}
    G7 = G.deletevent(b1)
    assert b1 not in G7.Sigma and G7.Gamma(q1) == {a1} and G7.Gamma(q2) == frozenset()
    G8 = G.addevents([e, f])
    assert G8.Sigma == {a1, b1, e, f} and G8.Graph.size() == G.Graph.size()
    G9 = G.renametransition([q1, (a1, f), q2])
    assert G9.Gamma(q1) == {f, b1}
    G10 = G.addselfloop(q1, a1)
    assert G10.delta(q1, a1) == {q1, q2}
    G11 = G.setpar(Xm=[q2], name='H', Sigobs=[a1], Sigcon=[b1])
    assert G11.Xm == {q2} and G11.name == 'H' and G11.Sigobs == {a1} and G11.Sigcon == {b1}
    with pytest.raises(invalidArgument):
        G.setpar(color='red')


def test_renamevents_keeps_properties():
    G = fsa(['x', 'y'], ['a', 'u'], [('x', 'a', 'y'), ('y', 'u', 'x'), ('x', 'u', 'x')],
            ['x'], ['y'], Sigobs=['a'], Sigcon=['a'])
    R = G.renamevents([('a', 'b'), ('u', 'v')])
    assert R.Sigma == {'b', 'v'} and R.Sigobs == {'b'} and R.Sigcon == {'b'}
    assert R.delta('x', 'v') == 'x' and R.delta('y', 'v') == 'x'
    assert languages(R, 4)[1] == {tuple({'a': 'b', 'u': 'v'}[e] for e in s) for s in languages(G, 4)[1]}
    S = G.renamevents({'a': 'u', 'u': 'a'})  # swap
    assert S.delta('x', 'u') == 'y' and S.delta('y', 'a') == 'x'


def test_renamestates():
    G = example()
    for mapping in ('number', 'letter', [('q1', 'z1')], {'q1': 'q2', 'q2': 'q1'}):
        R = G.renamestates(mapping)
        assert languages(R, 6) == languages(G, 6)
    N = G.renamestates('number')
    assert N.X0 == {1} and N.X == {1, 2, 3}


def test_save_load(tmp_path):
    G = example()
    fn = save(G, str(tmp_path / 'G1'))
    H = load(fn)
    assert H == G and H.symDict == G.symDict and H.name == G.name


def test_graph_utilities():
    G = example()
    assert {frozenset(c) for c in strconncomps(G)} == {frozenset({'q1', 'q2', 'q3'})}
    assert selfloopnodes(G) == ['q2']
