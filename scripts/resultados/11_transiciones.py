# -*- coding: utf-8 -*-
"""
Medida de destino dirigida: transiciones entre quintiles.

La pendiente rango-rango promedia toda la distribución. Nuestra hipótesis es
más específica: la violencia atrapa abajo a quien nació abajo. Una medida que
apunte justo a eso puede detectar un efecto que la pendiente global diluye.

Para cada transición se estima

    1[destino en el grupo G] = a + b*Dosis + EF_entidad + EF_nacimiento
                               + c*rango_de_origen + e

sobre la submuestra con un origen dado, con factores de expansión y errores
agrupados por entidad. Como se condiciona en el origen, aquí no hay término de
interacción: b es directamente el cambio en la probabilidad de la transición.

Para poder comparar su potencia con la de la pendiente, al final se estima el
"tipo de cambio" entre ambas escalas con celdas de entidad por cohorte.
"""
import sys, numpy as np, pandas as pd, statsmodels.api as sm
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from base import construir, muestra, efectos_fijos, escala

df = construir()
M = muestra(df)
K = escala(M)
print(f"\nMuestra analítica: {len(M)}   d.e. de intensidad entre entidades: {K:.3f}")


def transicion(d, y, etiq):
    """Modelo de probabilidad lineal con efectos fijos de entidad y cohorte."""
    d = d.copy(); d["y"] = y.astype(float)
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"dosis": d.dosis.values, "r_ori": d.r_ori.values},
                      index=d.index)] + efectos_fijos(d, rango=False), axis=1))
    m = sm.WLS(d.y, X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d.p19})
    b, se = m.params["dosis"] * K, m.bse["dosis"] * K
    tasa = np.average(d.y, weights=d.factor)
    print(f"  {etiq:46s} n={len(d):5d}  tasa base {tasa:5.1%}  "
          f"b={b:+.4f} ({se:.4f})  t={b/se:+5.2f}  EMD {2.8*se/tasa:4.0%}")
    return b, se, tasa


print("\n" + "=" * 110)
print("TRANSICIONES — cambio en la probabilidad por desviación estándar de intensidad")
print("=" * 110)
q1 = M[M.q_ori == 1]
q5 = M[M.q_ori == 5]
b11, s11, t11 = transicion(q1, q1.q_des == 1, "Origen Q1 -> sigue en Q1 (quedarse abajo)")
b1a, s1a, t1a = transicion(q1, q1.q_des >= 4, "Origen Q1 -> llega a Q4 o Q5 (ascenso largo)")
transicion(q1, q1.r_des >= .5, "Origen Q1 -> rebasa la mediana")
transicion(q5, q5.q_des == 5, "Origen Q5 -> sigue en Q5 (quedarse arriba)")
q12 = M[M.q_ori <= 2]
b22, s22, t22 = transicion(q12, q12.q_des <= 2, "Origen Q1-Q2 -> sigue en Q1-Q2")

# ------------------------------------------------------------------------
# ¿Gana potencia? Para compararla con la pendiente hay que llevar ambas a la
# misma escala. Se estima cuánto se mueve cada tasa de transición cuando la
# pendiente rango-rango se mueve una unidad, usando celdas entidad x cohorte.
# ------------------------------------------------------------------------
print("\n" + "=" * 110)
print("TIPO DE CAMBIO ENTRE LAS DOS ESCALAS (celdas de entidad x cohorte)")
print("=" * 110)
filas = []
for (e, c), g in M.groupby(["p19", "cohorte"]):
    if len(g) < 60 or (g.q_ori == 1).sum() < 12:
        continue
    pend = np.polyfit(g.r_ori, g.r_des, 1, w=np.sqrt(g.factor))[0]
    a = g[g.q_ori == 1]
    b = g[g.q_ori <= 2]
    filas.append({"pend": pend,
                  "p11": np.average(a.q_des == 1, weights=a.factor),
                  "p1a": np.average(a.q_des >= 4, weights=a.factor),
                  "p22": np.average(b.q_des <= 2, weights=b.factor),
                  "n": len(g)})
cel = pd.DataFrame(filas)
print(f"  Celdas utilizables: {len(cel)}  (pendiente entre "
      f"{cel.pend.min():.2f} y {cel.pend.max():.2f})")

for col, nom, emd in [("p11", "quedarse en Q1", 2.8 * s11),
                      ("p1a", "ascenso largo desde Q1", 2.8 * s1a),
                      ("p22", "quedarse en Q1-Q2", 2.8 * s22)]:
    r = sm.OLS(cel[col], sm.add_constant(cel[["pend"]])).fit()
    g_, sg = r.params["pend"], r.bse["pend"]
    print(f"\n  {nom}: al subir la pendiente en 1, la tasa cambia "
          f"{g_:+.3f} ({sg:.3f})")
    if abs(g_) > 2 * sg:
        print(f"    EMD de esta transición = {emd:.4f} en tasa "
              f"-> equivale a {abs(emd/g_):.3f} de pendiente")
        print(f"    EMD de la pendiente rango-rango                 = 0.071")
        veredicto = "GANA potencia" if abs(emd / g_) < 0.071 else "NO gana potencia"
        print(f"    {veredicto}")
    else:
        print("    La relación no es distinguible de cero: la conversión no es fiable")
