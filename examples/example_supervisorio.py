from deslab import *

"""Factory with two machines and a test unit (all the states of
the specifications are marked)"""

syms('x0 x1 y0 y1 z0 z1 z2 z3 xh10 xh11 xh20 xh21 e1 e2 e3 e4 e5 e60 e80 e62 e82')
table = [(e1, 'e_1'), (e2, 'e_2'), (e3, 'e_3'), (e4, 'e_4'), (e5, 'e_5'),
         (e60, 'e_{60}'), (e62, 'e_{62}'), (e80, 'e_{80}'), (e82, 'e_{82}')]

G1 = fsa([x0, x1], [e1, e2], [(x0, e1, x1), (x1, e2, x0)], [x0], [x0], table, name='$G_{M1}$')
G2 = fsa([y0, y1], [e3, e4], [(y0, e3, y1), (y1, e4, y0)], [y0], [y0], table, name='$G_{M2}$')
G3 = fsa([z0, z1, z2, z3], [e5, e62, e82, e80, e60],
         [(z0, e5, z1), (z1, e60, z2), (z2, e62, z0), (z1, e80, z3), (z3, e82, z0)],
         [z0], [z0], table, name='$G_{ut}$')

G = G1 // G2 // G3
G = G.setpar(Sigcon=set([e1, e3, e5]))

Xh1 = [xh10, xh11]
Th1 = [(xh10, e2, xh11), (xh10, e82, xh11), (xh11, e3, xh10)]
H1 = fsa(Xh1, [e2, e82, e3], Th1, [xh10], Xh1, table, name='$H_{spec,1}$', type='specification')

Xh2 = [xh20, xh21]
Th2 = [(xh20, e4, xh21), (xh21, e5, xh20)]
H2 = fsa(Xh2, [e4, e5], Th2, [xh20], Xh2, table, name='$H_{spec,2}$', type='specification')

R = G // H1 // H2
R = R.renamestates('number')
G = G.renamestates('number')
Ksup = supcontrollable(R, G, verbose=True)
Ksup = Ksup.setpar(type='supervisor')
print('K is controllable:', iscontrollable(Ksup, G))
draw(G1, G2, G3, H1, H2, Ksup)
