# -*- coding: utf-8 -*-
"""
Inferencia por permutación dentro de un subconjunto de entidades.

Con 6 a 15 entidades por conglomerado el error estándar agrupado está sesgado
hacia abajo (Cameron y Miller 2015), así que el estadístico t no es creíble.
La permutación no depende de ese supuesto: reasigna al azar la intensidad
ENTRE las entidades del subconjunto, recalcula b3 y compara el valor observado
con esa distribución nula.

Se usa Frisch-Waugh-Lovell con una descomposición QR del bloque de efectos
fijos, que se calcula una sola vez; cada permutación sólo residualiza las dos
columnas que cambian.
"""
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import numpy as np
import pandas as pd
import statsmodels.api as sm


def permutar_cg(s, n_perm=2000, semilla=20261102):
    """Devuelve (b3 observado en escala cruda, p de permutación, nulo al 95 %)."""
    ents = sorted(s.p19.unique())
    E = pd.get_dummies(s.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(s.nac.astype(int), prefix="c", drop_first=True).astype(float)
    FE = sm.add_constant(pd.concat(
        [pd.DataFrame({"r_ori": s.r_ori.values}, index=s.index), E, C,
         E.mul(s.r_ori, axis=0).add_prefix("ri_"),
         C.mul(s.r_ori, axis=0).add_prefix("rc_")], axis=1)).to_numpy()
    sw = np.sqrt(s.factor.to_numpy())
    Q, _ = np.linalg.qr(FE * sw[:, None])
    res = lambda v: (v * sw) - Q @ (Q.T @ (v * sw))
    ry = res(s.r_des.to_numpy())
    ro = s.r_ori.to_numpy()
    fr = s.frac.to_numpy()
    idx = {e: (s.p19 == e).to_numpy() for e in ents}
    iv = np.array([s[s.p19 == e].intens.iloc[0] for e in ents])

    def b3_de(vec):
        dos = np.empty(len(s))
        for e, v in zip(ents, vec):
            dos[idx[e]] = v
        dos = dos * fr
        A = np.column_stack([res(dos), res(ro * dos)])
        return np.linalg.lstsq(A, ry, rcond=None)[0][1]

    real = b3_de(iv)
    rng = np.random.default_rng(semilla)
    nulo = np.array([b3_de(rng.permutation(iv)) for _ in range(n_perm)])
    p = float((np.abs(nulo) >= abs(real)).mean())
    return float(real), p, np.percentile(nulo, [2.5, 97.5])
