from deslab import *

a, b, c, d, e, sf, g, x0, x1, x2, x3, x4, x5, x6, x7 = syms('a b c d e sf g 0 1 2 3 4 5 6 7')
sigma = set([a, b, c, d, e, sf])
X = [x1, x2, x3, x4, x5, x6, x7]
X0 = [x1]
Xm = [x1, x7]
T = [[x1, c, x2], [x1, a, x5], [x2, sf, x3], [x3, e, x4], [x4, a, x1], [x6, a, x1], [x6, e, x3],
     [x7, b, x1], [x4, d, x4], [x1, a, x5], [x5, b, x6], [x6, d, x6], [x7, d, x7], [x3, a, x7]]
G = fsa(X, sigma, T, X0, Xm, Sigobs=[a, c, d, e], name='$G$ -- nominal model')


def dilatation(G, Sigmaisf):
    """ each transition labelled by an event of Sigmaisf receives a
    parallel transition labelled by an unobservable copy of the event"""
    GA = G
    for state in G.X:
        for event in (G.Gamma(state) & set(Sigmaisf)):
            next_state = G.delta(state, event)
            event_uo = event + "'"
            GA = GA.addtransition([state, event_uo, next_state])
    Gisf = observer(GA, G.Sigma)
    Gisf = Gisf.setpar(Sigobs=G.Sigobs, name='$G_{isf}$ -- intermitent failure model', direction='LR')
    return Gisf


Gisf = dilatation(G, [a])
draw(G, Gisf)
