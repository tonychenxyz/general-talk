"""Smoothed price-vs-quality curve for slides (visual only).

The simulator's required-quality curve is two joined sigmoids with small kinks at the joins. For slides we sample it
densely, apply a Gaussian moving average (edges padded), and draw it as a Catmull-Rom spline through ~40 knots, ending
at the price cap (no vertical tail).
"""
import math


def smooth_path(qfun, cmax, X, Y, n=240, sigma_frac=0.08, knots=40):
    cs = [cmax * i / n for i in range(n + 1)]
    qs = [qfun(c) for c in cs]
    s = max(1, int(sigma_frac * n)); w = [math.exp(-0.5 * (k / s) ** 2) for k in range(-3 * s, 3 * s + 1)]
    pad = [qs[0]] * 3 * s + qs + [qs[-1]] * 3 * s
    sm = [sum(w[j] * pad[i + j] for j in range(len(w))) / sum(w) for i in range(len(qs))]
    idx = [round(i * n / knots) for i in range(knots + 1)]
    P = [(X(cs[i]), Y(sm[i])) for i in idx]
    d = [f'M{P[0][0]:.1f} {P[0][1]:.1f}']
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    return ' '.join(d)
