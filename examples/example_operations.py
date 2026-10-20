from deslab import *

syms('a b c d e f s1 s2 s3 s4')
table = [(a, '\\alpha'), (b, '\\beta'), (c, 'c_c'), (s1, 'x_1'), (s2, 'x_2'), (s3, 'x_3'), (s4, 'y_4')]

X1 = [s1, s2, s3, s4]
E1 = [a, b, c]
T1 = [(s1, a, s2), (s2, b, s3), (s3, c, s4), (s1, b, s4)]
H1 = fsa(X1, E1, T1, [s1], [s2, s3, s4], table, name='$G_1$')

X2 = [s1, s2, s3, s4]
E2 = [a, b, c, d, e, f]
T2 = [(s1, a, s2), (s2, e, s3), (s3, f, s4), (s1, b, s3), (s1, f, s4), (s2, f, s4)]
H2 = fsa(X2, E2, T2, [s1], [s1, s2], table, name='$G_2$')

P = (H1 & H2).setpar(name='$G_1 \\times G_2$')         # product
Par = (H1 // H2).setpar(name='$G_1 \\| G_2$')          # parallel composition
U = (H1 + H2).setpar(name='$L_m(G_1) \\cup L_m(G_2)$')  # union
C = (H1 * H2).setpar(name='$L_m(G_1) L_m(G_2)$')       # concatenation
Co = (~H1).setpar(name='$L_m(G_1)^c$')                 # complement
K = kleeneclos(H1).setpar(name='$L_m(G_1)^*$')         # Kleene closure

draw(H1, H2, P, Par, U, C, Co, K)

print('Lm(G1 x G2) <= Lm(G1):', P <= H1)
print('Lm(G1) = Lm(complement(complement(G1))):', are_langequiv(H1, ~~H1))
