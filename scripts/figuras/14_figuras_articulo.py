# -*- coding: utf-8 -*-
"""
figuras_articulo.py — las figuras del manuscrito, con el formato de Springer
============================================================================
Reglas de Empirical Economics que se respetan aquí:
  * ancho 174 mm (área de texto a una columna), alto máximo 234 mm
  * tipografía Arial o Helvetica entre 8 y 12 pt  -> Liberation Sans,
    métricamente compatible con Arial
  * 600 ppp (arte combinado)
  * legibles en blanco y negro: cada serie lleva marcador y trazo distintos,
    el color nunca es el único portador de la información
  * los pies de figura NO van en el archivo, van en el texto del manuscrito

De paso corrige en resultados.json el bloque de transiciones, que debe usar
las definiciones de transiciones.py y no una reimplementación.
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
FIG = _r.FIG_EN
os.makedirs(FIG, exist_ok=True)

MM = 174 / 25.4                      # ancho de la caja de texto, en pulgadas
plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "lines.linewidth": 1.3,
    "savefig.dpi": 600,
    "figure.dpi": 150,
})
GRIS = "#595959"
NEGRO = "#1A1A1A"


def limpiar(ax, eje_y=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if eje_y:
        ax.grid(axis="y", color="#D9D9D9", lw=0.6)
        ax.set_axisbelow(True)


from base import construir, muestra, escala, panel_violencia, efectos_fijos
from graficas_entregable1 import (poblacion_anual, cargar_sesnsp, ABREV, MESES)

R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))

# ===================================================================== datos
pob = poblacion_anual(range(1997, 2025))
panel, delitos = cargar_sesnsp(
    _r.SES, pob)
M = pd.read_pickle(f"{SAL}/M.pkl")
K = escala(M)
PEND = R["muestra"]["pendiente_base"]

# ============================================================ FIGURA 1
# Contexto: el repunte de la violencia, y que no es sólo homicidio.
nac = panel.groupby("year")[delitos].sum()
pobt = panel.groupby("year").pob.sum()
tasa = (nac.T / pobt).T * 1e5

fig, ax = plt.subplots(1, 2, figsize=(MM, 3.1))
ax[0].plot(tasa.index, tasa.homicidio, marker="o", ms=3.2, color="#A63A2B",
           ls="-")
ax[0].set_title("(a) Intentional homicide")
ax[0].set_ylabel("Investigation files per 100,000")
estilos = [("extorsion", "Extortion", "s", "--", "#1F4E79"),
           ("secuestro", "Kidnapping", "^", "-.", "#2E6B2E"),
           ("robo_carr", "Violent highway robbery", "D", ":", "#8C6D1F")]
for d, et, mk, ls, co in estilos:
    ax[1].plot(tasa.index, tasa[d], marker=mk, ms=3.0, ls=ls, color=co, label=et)
ax[1].set_title("(b) Crimes of economic predation")
ax[1].legend(frameon=False, handlelength=2.6)
for a in ax:
    a.axvspan(2007, 2012, color="#000000", alpha=0.055, zorder=0, lw=0)
    a.set_xlabel("Year")
    a.set_xlim(1997, 2017)
    a.set_xticks(range(1997, 2018, 4))
    limpiar(a)
plt.tight_layout()
plt.savefig(f"{FIG}/Fig1.png", bbox_inches="tight")
plt.close(fig)

# ============================================================ FIGURA 2
# Las dos piezas de la dosis, por separado: el calendario y la geografía.
fig, ax = plt.subplots(1, 2, figsize=(MM, 3.3),
                       gridspec_kw={"width_ratios": [1, 1.5]})

anios_nac = np.arange(1959, 1999)
phi = np.array([len([y for y in range(n + 10, n + 19) if y >= 2007]) / 9
                for n in anios_nac])
ax[0].step(anios_nac, phi, where="mid", color=NEGRO, lw=1.5)
ax[0].fill_between(anios_nac, 0, phi, step="mid", color="#A63A2B", alpha=0.16,
                   lw=0)
ax[0].set_xlabel("Birth year")
ax[0].set_ylabel(r"$\varphi(c)$: share of ages 10–18 after 2007")
ax[0].set_title("(a) The cohort component")
ax[0].set_xticks(range(1960, 1999, 10))
ax[0].set_ylim(-0.03, 1.05)
ax[0].annotate("fully\nexposed", xy=(1997.5, 1.0), xytext=(1986, 0.78),
               fontsize=8, color=GRIS, ha="center",
               arrowprops=dict(arrowstyle="->", color=GRIS, lw=0.7))
limpiar(ax[0])

ints = (panel[(panel.year >= 2007) & (panel.year <= 2017)]
        .groupby("cve").indice.mean().sort_values())
usada = set(M.p19.unique())
colores = ["#A63A2B" if e in usada else "#BFBFBF" for e in ints.index]
hatch = ["" if e in usada else "///" for e in ints.index]
barras = ax[1].bar(range(len(ints)), ints.values, color=colores,
                   edgecolor=NEGRO, lw=0.4)
for b, h in zip(barras, hatch):
    b.set_hatch(h)
ax[1].set_xticks(range(len(ints)))
ax[1].set_xticklabels([ABREV.get(int(e), str(e)) for e in ints.index],
                      rotation=90, fontsize=6.6)
ax[1].axhline(0, color=NEGRO, lw=0.7)
ax[1].set_ylabel("Mean violence index, 2007–2017")
ax[1].set_title("(b) The state component")
ax[1].legend(handles=[
    Line2D([0], [0], color="#A63A2B", lw=6, label="In estimation sample"),
    Line2D([0], [0], color="#BFBFBF", lw=6, label="Excluded (no observations)")],
    frameon=False, loc="upper left")
limpiar(ax[1])
plt.tight_layout()
plt.savefig(f"{FIG}/Fig2.png", bbox_inches="tight")
plt.close(fig)

# ============================================================ FIGURA 3
# La prueba del supuesto, en los dos diseños.
ev = pd.read_pickle(f"{SAL}/ev_estatal.pkl")
evm = R["municipal"]
etq = ["≤1970", "1971–74", "1975–78", "1979–82", "1983–86", "1987–90",
       "1991–94", "1995–98"]

# el evento municipal se vuelve a estimar aquí para tener los coeficientes
from municipal import construir_municipal, dummies_tam
Mm = construir_municipal(verbose=False)
tams = dummies_tam(Mm)
REF = "g3"
G = pd.get_dummies(Mm.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
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
km_ = Mm.Dm.std()
bm, sem = [], []
for i in range(8):
    if f"g{i}" == REF:
        bm.append(0.0); sem.append(0.0)
    else:
        bm.append(mm.params[f"ev_g_g{i}"] * km_)
        sem.append(mm.bse[f"ev_g_g{i}"] * km_)

fig, ax = plt.subplots(1, 2, figsize=(MM, 3.5), sharey=False)
for j, (b_, se_, tit, prev) in enumerate([
        (ev.b.values, ev.se.values, "(a) State design",
         ev.previo.values | ev.ref.values),
        (np.array(bm), np.array(sem), "(b) Within-state municipal design",
         np.array([True, True, True, True, True, False, False, False]))]):
    a = ax[j]
    x = np.arange(8)
    a.axhline(0, color=NEGRO, lw=0.7)
    a.axvspan(4.5, 7.5, color="#A63A2B", alpha=0.055, zorder=0, lw=0)
    a.errorbar(x[prev], b_[prev], yerr=1.96 * se_[prev], fmt="o", ms=4.2,
               mfc="white", mec="#1F4E79", ecolor="#1F4E79", lw=1.1, capsize=2.4)
    a.errorbar(x[~prev], b_[~prev], yerr=1.96 * se_[~prev], fmt="s", ms=4.2,
               color="#A63A2B", ecolor="#A63A2B", lw=1.1, capsize=2.4)
    a.set_xticks(x)
    a.set_xticklabels(etq, rotation=45, ha="right", fontsize=7.4)
    a.set_xlabel("Birth-year group")
    a.set_title(tit)
    limpiar(a)
ax[0].set_ylabel("Change in the rank–rank slope\nper SD of violence intensity")
ax[0].annotate(f"Joint pre-trend test:\n$F$ = {R['evento_estatal']['F']:.2f}, "
               f"$p$ = {R['evento_estatal']['p']:.2f}",
               xy=(0.03, 0.97), xycoords="axes fraction", va="top",
               fontsize=7.6, color=GRIS)
ax[1].annotate(f"Joint pre-trend test:\n$F$ = 1.77, $p$ = 0.13",
               xy=(0.03, 0.97), xycoords="axes fraction", va="top",
               fontsize=7.6, color=GRIS)
fig.legend(handles=[
    Line2D([0], [0], marker="o", ms=4.6, mfc="white", mec="#1F4E79",
           color="#1F4E79", lw=1.1, label="Formative window before the surge"),
    Line2D([0], [0], marker="s", ms=4.6, color="#A63A2B", lw=1.1,
           label="Formative window reached by the surge")],
    loc="lower center", ncol=2, frameon=False, fontsize=8.2,
    bbox_to_anchor=(0.5, -0.045))
plt.tight_layout()
plt.savefig(f"{FIG}/Fig3.png", bbox_inches="tight")
plt.close(fig)

# ============================================================ FIGURA 4
# El componente de ciencia de datos.
from scipy.cluster.hierarchy import dendrogram, fcluster

Z = np.load(f"{SAL}/Z_ward.npy")
F = pd.read_pickle(f"{SAL}/F_trayectorias.pkl")
anios = F.columns.values
K_USO = R["conglomerados"]["k_elegido"]
ward = fcluster(Z, K_USO, criterion="maxclust")
sil_w = R["conglomerados"]["silueta_ward"]
sil_k = R["conglomerados"]["silueta_kmedias"]

fig = plt.figure(figsize=(MM, 5.6))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.6, 1],
                      hspace=0.42, wspace=0.26)
a1 = fig.add_subplot(gs[0, 0])
a2 = fig.add_subplot(gs[0, 1])
a3 = fig.add_subplot(gs[1, :])

dendrogram(Z, labels=[ABREV.get(int(e), str(e)) for e in F.index], ax=a1,
           color_threshold=Z[-(K_USO - 1), 2], above_threshold_color="#8C8C8C",
           leaf_font_size=6.6, leaf_rotation=90)
a1.set_title("(a) Ward dendrogram of violence trajectories")
a1.set_ylabel("Distance")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)

ks = sorted(int(k) for k in sil_w)
a2.plot(ks, [sil_w[str(k)] for k in ks], marker="o", ms=4, ls="-",
        color="#1F4E79", label="Ward")
a2.plot(ks, [sil_k[str(k)] for k in ks], marker="s", ms=4, ls="--",
        color="#A63A2B", label="$k$-means")
a2.axvline(K_USO, color=GRIS, lw=0.9, ls=":")
a2.set_xlabel("Number of clusters ($k$)")
a2.set_ylabel("Mean silhouette")
a2.set_title("(b) Choice of $k$")
a2.legend(frameon=False, handlelength=2.4)
limpiar(a2)

est = {"1": ("-", "o", "#1F4E79"), "2": ("--", "s", "#A63A2B"),
       "3": (":", "^", "#2E6B2E")}
for p in R["conglomerados"]["perfiles"]:
    c = str(p["cg"])
    ent = F.index[ward == p["cg"]]
    mu = F.loc[ent].mean()
    sd = F.loc[ent].std()
    ls, mk, co = est[c]
    a3.plot(anios, mu, ls=ls, marker=mk, ms=3.2, color=co, lw=1.5,
            label=f"Cluster {c}: {p['n_entidades']} states, peak {p['pico']}")
    a3.fill_between(anios, mu - sd, mu + sd, color=co, alpha=0.08, lw=0)
a3.axvline(2007, color=NEGRO, lw=0.9, ls="--")
a3.annotate("2007", xy=(2007, a3.get_ylim()[1]), xytext=(3, -11),
            textcoords="offset points", fontsize=7.6, color=NEGRO)
a3.axhline(0, color=GRIS, lw=0.7)
a3.set_xticks(np.arange(1997, 2018, 2))
a3.set_xlabel("Year")
a3.set_ylabel("Violence index\n(standardised within state)")
a3.set_title("(c) Mean trajectory by cluster")
a3.legend(frameon=False, loc="upper left", handlelength=2.6)
limpiar(a3)
plt.savefig(f"{FIG}/Fig4.png", bbox_inches="tight")
plt.close(fig)

# ======================================= parche: transiciones con su definición
df = construir(verbose=False)
Mt = muestra(df)


def transicion(d, y, etiq):
    d = d.copy()
    d["y"] = y.astype(float)
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"dosis": d.dosis.values, "r_ori": d.r_ori.values},
                      index=d.index)] + efectos_fijos(d, rango=False), axis=1))
    m = sm.WLS(d.y, X, weights=d.factor).fit(cov_type="cluster",
                                             cov_kwds={"groups": d.p19})
    b, se = m.params["dosis"] * K, m.bse["dosis"] * K
    tasa = float(np.average(d.y, weights=d.factor))
    return {"etiq": etiq, "b": float(b), "se": float(se), "t": float(b / se),
            "tasa_base": tasa, "n": int(len(d)), "emd_tasa": float(2.8 * se)}


q1, q5 = Mt[Mt.q_ori == 1], Mt[Mt.q_ori == 5]
q12 = Mt[Mt.q_ori <= 2]
trs = [transicion(q1, q1.q_des == 1, "Origin Q1 -> stays in Q1"),
       transicion(q1, q1.q_des >= 4, "Origin Q1 -> reaches Q4 or Q5"),
       transicion(q5, q5.q_des == 5, "Origin Q5 -> stays in Q5"),
       transicion(q12, q12.q_des <= 2, "Origin Q1-Q2 -> stays in Q1-Q2")]

filas = []
for (e, c), g in Mt.groupby(["p19", "cohorte"]):
    if len(g) < 60 or (g.q_ori == 1).sum() < 12:
        continue
    a_ = g[g.q_ori == 1]
    filas.append({"pend": float(np.polyfit(g.r_ori, g.r_des, 1,
                                           w=np.sqrt(g.factor))[0]),
                  "p11": float(np.average(a_.q_des == 1, weights=a_.factor))})
cel = pd.DataFrame(filas)
rr = sm.OLS(cel.p11, sm.add_constant(cel[["pend"]])).fit()
g_, sg = float(rr.params["pend"]), float(rr.bse["pend"])
emd_pend = trs[0]["emd_tasa"] / abs(g_)
R["transiciones"] = {
    "modelos": trs, "celdas": int(len(cel)), "tipo_de_cambio": g_,
    "tipo_de_cambio_se": sg, "emd_en_pendiente": float(emd_pend),
    "emd_pct_pendiente": float(emd_pend / PEND),
    "emd_pendiente_rangorango": float(R["potencia"]["emd_de"]),
    "emd_pct_rangorango": float(R["potencia"]["emd_de_pct"])}

with open(f"{SAL}/resultados.json", "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False)

print("Figuras escritas en", FIG)
for f_ in sorted(os.listdir(FIG)):
    print("  ", f_, f"{os.path.getsize(f'{FIG}/{f_}')/1e6:.2f} MB")
print(f"\nTransiciones: tipo de cambio {g_:+.3f} ({sg:.3f}) sobre {len(cel)} celdas")
print(f"  EMD de la transición en unidades de pendiente: {emd_pend:.4f} "
      f"= {emd_pend/PEND:.0%} de la pendiente")
print(f"  EMD de la pendiente rango-rango:               "
      f"{R['potencia']['emd_de']:.4f} = {R['potencia']['emd_de_pct']:.0%}")
