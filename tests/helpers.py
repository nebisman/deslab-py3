"""Brute force language utilities used to check the DESlab algorithms."""
import random
from itertools import product as cartesian
from deslab import fsa, epsilon


def closure(G, Q, unobservable=frozenset([epsilon])):
    """states reached from Q through unobservable (by default epsilon) events"""
    stack, reached = list(Q), set(Q)
    while stack:
        x = stack.pop()
        for _, y, e in G.Graph.out_edges(x, keys=True):
            if e in unobservable and y not in reached:
                reached.add(y)
                stack.append(y)
    return frozenset(reached)


def step(G, Q, event, unobservable=frozenset([epsilon])):
    nxt = {y for x in Q for _, y, e in G.Graph.out_edges(x, keys=True) if e == event}
    return closure(G, nxt, unobservable)


def languages(G, n, alphabet=None):
    """generated and marked languages of G restricted to strings of length <= n"""
    if G.empty:
        return set(), set()
    alphabet = sorted(set(G.Sigma if alphabet is None else alphabet) - {epsilon}, key=str)
    L, Lm = set(), set()
    frontier = [((), closure(G, G.X0))]
    while frontier:
        s, Q = frontier.pop()
        L.add(s)
        if Q & G.Xm:
            Lm.add(s)
        if len(s) < n:
            for e in alphabet:
                Q2 = step(G, Q, e)
                if Q2:
                    frontier.append((s + (e,), Q2))
    return L, Lm


def projected_languages(G, obs, n):
    """P(L(G)) and P(Lm(G)) restricted to length <= n (exact, unobservable
    events are closed with a reachability search)"""
    unobs = frozenset(G.Sigma - frozenset(obs)) | {epsilon}
    obs = sorted(set(obs) - {epsilon}, key=str)
    L, Lm = set(), set()
    frontier = [((), closure(G, G.X0, unobs))]
    while frontier:
        s, Q = frontier.pop()
        L.add(s)
        if Q & G.Xm:
            Lm.add(s)
        if len(s) < n:
            for e in obs:
                Q2 = step(G, Q, e, unobs)
                if Q2:
                    frontier.append((s + (e,), Q2))
    return L, Lm


def strings(alphabet, n):
    alphabet = sorted(set(alphabet) - {epsilon}, key=str)
    for k in range(n + 1):
        for s in cartesian(alphabet, repeat=k):
            yield s


def P(s, obs):
    return tuple(e for e in s if e in obs)


def random_fsa(rng, nstates=4, events=('a', 'b', 'c'), det=True, eps=False,
               p=0.45, pm=0.4, acyclic=False, **kwargs):
    X = ['x%d' % i for i in range(nstates)]
    Sigma = list(events) + ([epsilon] if eps else [])
    T = []
    for i, x in enumerate(X):
        targets = X[i + 1:] if acyclic else X
        if not targets:
            continue
        for e in Sigma:
            if det and e != epsilon:
                if rng.random() < p:
                    T.append((x, e, rng.choice(targets)))
            else:
                for y in targets:
                    if rng.random() < p / 2:
                        T.append((x, e, y))
    Xm = [x for x in X if rng.random() < pm]
    return fsa(X, Sigma, T, [X[0]], Xm, **kwargs)


def rngs(count=25, seed=0):
    return [random.Random(seed + k) for k in range(count)]
