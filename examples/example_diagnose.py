from deslab import *

syms('a b c d e sf x1 x2 x3 x4 x5 x6 x7')

X = [x1, x2, x3, x4, x5, x6, x7]
Sigma = [a, b, c, d, e, sf]
T = [(x1, c, x2), (x1, a, x5), (x2, sf, x3), (x3, e, x4), (x4, d, x4),
     (x5, b, x6), (x6, d, x6), (x7, e, x7), (x3, a, x7)]
table = [(x1, 'x_1'), (x2, 'x_2'), (x3, 'x_3'), (x4, 'x_4'), (x5, 'x_5'), (x6, 'x_6'),
         (x7, 'x_7'), (sf, '\\sigma_f')]
G = fsa(X, Sigma, T, [x1], [], table, Sigobs=[a, b, c, d, e], name='$G$')

Gl = (G // labelfailaut(sf)).setpar(name='$G \\| A_l$')
O = observer(G).setpar(name='$Obs(G)$')
D = diagnoser(G, sf)
draw(G, Gl, O, D)
