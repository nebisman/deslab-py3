from deslab import *

syms('q1 q2 q3 a1 b1 e f')

table = [(a1, 'a_1'), (b1, 'b_1'), (q1, 'q_1'), (q2, 'q_2'), (q3, 'q_3')]
X = [q1, q2, q3]
Sigma = [a1, b1, e]
X0 = [q1]
Xm = [q3]
T = [(q1, b1, q2), (q2, b1, q3), (q2, e, q3), (q3, a1, q1), (q2, b1, q2)]
G1 = fsa(X, Sigma, T, X0, Xm, table, name='$G_1$')
print(G1)
draw(G1)
