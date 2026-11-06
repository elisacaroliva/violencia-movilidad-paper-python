# -*- coding: utf-8 -*-
"""
figuras_es.py — versiones en español de las dos figuras de resultados
=====================================================================
Mismas estimaciones que Fig3 y Fig4 del manuscrito; sólo cambian las
etiquetas. Resolución menor (200 ppp) porque éstas van a pantalla, no a
imprenta.
"""
import json, os, sys, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
SEED = 20261102
np.random.seed(SEED)

SAL = _r.SAL
FIG = _r.FIG_ES
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "Liberation Sans", "font.size": 10,
    "axes.titlesize": 10.5, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.linewidth": 0.8, "lines.linewidth": 1.4,
    "savefig.dpi": 200, "figure.dpi": 120,
})
GRIS, NEGRO = "#595959", "#1A1A1A"
AZUL, ROJO, VERDE = "#1F4E79", "#A63A2B", "#2E6B2E"


def limpiar(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", lw=0.6)
    ax.set_axisbelow(True)


R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
from base import escala
from graficas_entregable1 import ABREV

ETQ = ["≤1970", "1971-74", "1975-78", "1979-82", "1983-86", "1987-90",
       "1991-94", "1995-98"]

# ====================================================== Figura A: evento
ev = pd.read_pickle(f"{SAL}/ev_estatal.pkl")

from municipal import construir_municipal, dummies_tam
Mm = construir_municipal(verbose=False)
tams = dummies_tam(Mm)
G = pd.get_dummies(Mm.grp, prefix="g", dtype=float).drop(columns=["g_g3"])
C = pd.get_dummies(Mm.nac.astype(int), prefix="c", drop_first=True).astype(float)
E = pd.get_dummies(Mm.p19.astype(int), prefix="e", drop_first=True).astype(float)
piezas = [pd.DataFrame({"r_ori": Mm.r_ori.values}, index=Mm.index),
          G.mul(Mm.Dm, axis=0).add_prefix("d_"),
          G.mul(Mm.r_ori * Mm.Dm, axis=0).add_prefix("ev_"),
          C, E, C.mul(Mm.r_ori, axis=0).add_prefix("rc_"),
          E.mul(Mm.r_ori, axis=0).add_prefix("ri_")]
for c in tams:
    piezas.append(pd.DataFrame({f"x_{c}": Mm[c].values,
                                f"xr_{c}": (Mm[c] * Mm.r_ori).values},
                               index=Mm.index))
mm = sm.WLS(Mm.r_des, sm.add_constant(pd.concat(piezas, axis=1)),
            weights=Mm.factor).fit(cov_type="cluster",
                                   cov_kwds={"groups": Mm.mun})
km = Mm.Dm.std()
bm = [0.0 if f"g{i}" == "g3" else mm.params[f"ev_g_g{i}"] * km for i in range(8)]
sem = [0.0 if f"g{i}" == "g3" else mm.bse[f"ev_g_g{i}"] * km for i in range(8)]

fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.2))
paneles = [
    (ev.b.values, ev.se.values, "(a) Diseño estatal",
     ev.previo.values | ev.ref.values, R["evento_estatal"]["F"],
     R["evento_estatal"]["p"]),
    (np.array(bm), np.array(sem), "(b) Diseño municipal intraestatal",
     np.array([True] * 5 + [False] * 3), 1.77, 0.13),
]
for j, (b_, se_, tit, prev, F_, p_) in enumerate(paneles):
    a = ax[j]
    x = np.arange(8)
    a.axhline(0, color=NEGRO, lw=0.8)
    a.axvspan(4.5, 7.5, color=ROJO, alpha=0.06, zorder=0, lw=0)
    a.errorbar(x[prev], b_[prev], yerr=1.96 * se_[prev], fmt="o", ms=5,
               mfc="white", mec=AZUL, ecolor=AZUL, lw=1.2, capsize=2.6)
    a.errorbar(x[~prev], b_[~prev], yerr=1.96 * se_[~prev], fmt="s", ms=5,
               color=ROJO, ecolor=ROJO, lw=1.2, capsize=2.6)
    a.set_xticks(x)
    a.set_xticklabels(ETQ, rotation=45, ha="right", fontsize=8.4)
    a.set_xlabel("Grupo de año de nacimiento")
    a.set_title(tit)
    a.annotate(f"Prueba conjunta de\ntendencias previas:\nF = {F_:.2f}, p = {p_:.2f}",
               xy=(0.03, 0.97), xycoords="axes fraction", va="top",
               fontsize=8.4, color=GRIS)
    limpiar(a)
ax[0].set_ylabel("Cambio en la pendiente origen-destino\npor desviación estándar de intensidad")
fig.legend(handles=[
    Line2D([0], [0], marker="o", ms=5.4, mfc="white", mec=AZUL, color=AZUL,
           lw=1.2, label="Ventana formativa previa al repunte"),
    Line2D([0], [0], marker="s", ms=5.4, color=ROJO, lw=1.2,
           label="Ventana formativa alcanzada por el repunte")],
    loc="lower center", ncol=2, frameon=False, fontsize=9,
    bbox_to_anchor=(0.5, -0.04))
plt.tight_layout()
plt.savefig(f"{FIG}/evento_es.png", bbox_inches="tight")
plt.close(fig)

# =================================================== Figura B: conglomerados
from scipy.cluster.hierarchy import dendrogram, fcluster

Z = np.load(f"{SAL}/Z_ward.npy")
F = pd.read_pickle(f"{SAL}/F_trayectorias.pkl")
anios = F.columns.values
ward = fcluster(Z, 3, criterion="maxclust")
sw, sk = R["conglomerados"]["silueta_ward"], R["conglomerados"]["silueta_kmedias"]

fig = plt.figure(figsize=(10.4, 8.0))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], width_ratios=[1.55, 1],
                      hspace=0.45, wspace=0.24)
a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])

dendrogram(Z, labels=[ABREV.get(int(e), str(e)) for e in F.index], ax=a1,
           color_threshold=Z[-2, 2], above_threshold_color="#8C8C8C",
           leaf_font_size=7.4, leaf_rotation=90)
a1.set_title("(a) Dendrograma de Ward sobre las trayectorias")
a1.set_ylabel("Distancia")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)

ks = sorted(int(k) for k in sw)
a2.plot(ks, [sw[str(k)] for k in ks], marker="o", ms=4.6, ls="-", color=AZUL,
        label="Ward")
a2.plot(ks, [sk[str(k)] for k in ks], marker="s", ms=4.6, ls="--", color=ROJO,
        label="k-medias")
a2.axvline(3, color=GRIS, lw=1.0, ls=":")
a2.set_xlabel("Número de conglomerados (k)")
a2.set_ylabel("Silueta media")
a2.set_title("(b) Elección de k")
a2.legend(frameon=False, handlelength=2.4)
limpiar(a2)

est = {1: ("-", "o", AZUL), 2: ("--", "s", ROJO), 3: (":", "^", VERDE)}
for p in R["conglomerados"]["perfiles"]:
    c = p["cg"]
    ent = F.index[ward == c]
    mu, sd = F.loc[ent].mean(), F.loc[ent].std()
    ls, mk, co = est[c]
    a3.plot(anios, mu, ls=ls, marker=mk, ms=3.6, color=co, lw=1.7,
            label=f"Conglomerado {c}: {p['n_entidades']} entidades, pico {p['pico']}")
    a3.fill_between(anios, mu - sd, mu + sd, color=co, alpha=0.08, lw=0)
a3.axvline(2007, color=NEGRO, lw=1.0, ls="--")
a3.annotate("2007", xy=(2007, a3.get_ylim()[1]), xytext=(4, -12),
            textcoords="offset points", fontsize=8.6, color=NEGRO)
a3.axhline(0, color=GRIS, lw=0.8)
a3.set_xticks(np.arange(1997, 2018, 2))
a3.set_xlabel("Año")
a3.set_ylabel("Índice de violencia\n(estandarizado dentro de cada entidad)")
a3.set_title("(c) Trayectoria media de cada conglomerado")
a3.legend(frameon=False, loc="upper left", handlelength=2.6)
limpiar(a3)
plt.savefig(f"{FIG}/conglomerados_es.png", bbox_inches="tight")
plt.close(fig)

for f in sorted(os.listdir(FIG)):
    print(f"  {FIG}/{f}  {os.path.getsize(f'{FIG}/{f}')/1e6:.2f} MB")
