# -*- coding: utf-8 -*-
"""
congelar.py — fuente única de verdad del manuscrito
===================================================
Corre todas las estimaciones del proyecto con semilla fija y escribe
  resultados/resultados.json   todos los números citados en el texto
  resultados/tN_*.csv          una tabla por archivo
  resultados/log.txt           bitácora legible

Todo lo que aparezca en el manuscrito debe salir de aquí. Si un número del
texto no está en resultados.json, es que alguien lo escribió a mano.

Uso:  python congelar.py
"""
import json, os, sys, warnings
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from guardar import guardar
import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

SEED = 20261102                       # semilla fija del proyecto
np.random.seed(SEED)

from base import (construir, muestra, ddd, escala, panel_violencia,
                  efectos_fijos, ANIOS_ESC)
from graficas_entregable1 import ABREV
from conglomerados_perm import permutar_cg

SAL = _r.SAL
os.makedirs(SAL, exist_ok=True)
R = {"semilla": SEED}
LOG = []


def di(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def titulo(t):
    di("\n" + "=" * 74)
    di(t)
    di("=" * 74)


def pend_base(d):
    """Pendiente rango-rango ponderada, sin controles."""
    return float(np.polyfit(d.r_ori, d.r_des, 1, w=np.sqrt(d.factor))[0])


# ====================================================================== A
titulo("A. MUESTRA")
df = construir(verbose=True)
M = muestra(df)
K = escala(M)                          # d.e. de la intensidad entre entidades
PEND = pend_base(M)

di(f"Encuestados con dosis y rangos válidos : {len(df):,}")
di(f"Muestra analítica (sin migrantes)      : {len(M):,}")
di(f"Entidades                              : {M.p19.nunique()}")
di(f"Años de nacimiento                     : {int(M.nac.min())}-{int(M.nac.max())}")
di(f"Pendiente rango-rango base             : {PEND:.4f}")
di(f"D.e. de la intensidad entre entidades  : {K:.4f}")

R["muestra"] = {"n_total": int(len(df)), "n_analitica": int(len(M)),
                "entidades": int(M.p19.nunique()),
                "nac_min": int(M.nac.min()), "nac_max": int(M.nac.max()),
                "pendiente_base": PEND, "de_intensidad": float(K),
                "municipios_origen": int(pd.to_numeric(M.p20_COD, errors="coerce")
                                         .between(1001, 32999).sum())}

# ====================================================================== B
titulo("B. TABLA 1 — ESTADÍSTICAS DESCRIPTIVAS")


def wstat(s, w):
    s = pd.to_numeric(s, errors="coerce")
    ok = s.notna()
    s, w = s[ok], w[ok]
    m = np.average(s, weights=w)
    v = np.average((s - m) ** 2, weights=w)
    return m, np.sqrt(v), int(ok.sum())


VARS = [("r_ori", "Origin rank (household assets at 14)"),
        ("r_des", "Destination rank (household assets at survey)"),
        ("r_des_ed", "Destination rank (years of schooling)"),
        ("ed_yo", "Years of schooling, respondent"),
        ("ed_pad", "Years of schooling, most educated parent"),
        ("intens", "Violence intensity of state (2007-2017 index)"),
        ("frac", "Share of formative window after 2007"),
        ("dosis", "Dose (intensity x window share)"),
        ("mujer", "Female"),
        ("rural", "Rural origin (locality < 2,500)"),
        ("corresid", "Co-resides with parents")]

expuesto = M.frac > 0
filas = []
for v, et in VARS:
    m, s, n = wstat(M[v], M.factor)
    m1, s1, _ = wstat(M.loc[expuesto, v], M.loc[expuesto, "factor"])
    m0, s0, _ = wstat(M.loc[~expuesto, v], M.loc[~expuesto, "factor"])
    filas.append({"Variable": et, "Mean": m, "SD": s, "N": n,
                  "Mean_exposed": m1, "Mean_unexposed": m0,
                  "Diff": m1 - m0})
t1 = pd.DataFrame(filas)
t1.to_csv(f"{SAL}/t1_descriptivas.csv", index=False)
di(t1.round(3).to_string(index=False))
di(f"\nExpuestos (fracción de ventana > 0): {int(expuesto.sum()):,} "
   f"({expuesto.mean():.1%})   No expuestos: {int((~expuesto).sum()):,}")
R["descriptivas"] = {"n_expuestos": int(expuesto.sum()),
                     "share_expuestos": float(expuesto.mean())}

# ====================================================================== C
titulo("C. TABLA 2 — RESULTADO PRINCIPAL (DISEÑO ESTATAL)")
di(f"{'Especificación':50s} {'b3':>9} {'ee':>8} {'t':>7} {'n':>7}")


def fila(nombre, d, extra=None, cl="p19", y="r_des", esc=None):
    m = ddd(d, extra=extra, cl=cl, y=y)
    k = K if esc is None else esc
    b, se = m.params["b3"] * k, m.bse["b3"] * k
    di(f"  {nombre:48s} {b:+9.4f} {se:8.4f} {b/se:+7.2f} {len(d):7,}")
    return {"nombre": nombre, "b3": float(b), "se": float(se),
            "t": float(b / se), "n": int(len(d)),
            "ic_bajo": float(b - 1.96 * se), "ic_alto": float(b + 1.96 * se),
            "emd": float(2.8 * se), "emd_pct": float(2.8 * se / pend_base(d))}


t2 = []
t2.append(fila("(1) Baseline", M))
B0, SE0 = t2[0]["b3"], t2[0]["se"]
t2.append(fila("(2) Excluding co-residents", M[M.corresid == 0]))
t2.append(fila("(3) Including inter-state migrants", df[df.p19 <= 32]))

panel, _ = panel_violencia()
ih = panel[(panel.year >= 2007) & (panel.year <= 2017)].groupby("cve").homicidio_t.mean()
ihz = (ih - ih.mean()) / ih.std()
Mh = M.copy()
Mh["intens"] = Mh.p19.map(ihz)
Mh["dosis"] = Mh.intens * Mh.frac
Mh = Mh.dropna(subset=["dosis"])
t2.append(fila("(4) Dose from intentional homicide only", Mh,
               esc=escala(Mh)))

t2.append(fila("(5) Clustering by birth year instead of state", M, cl="nac"))

t2d = pd.DataFrame(t2)
t2d.to_csv(f"{SAL}/t2_principal.csv", index=False)
R["principal"] = t2

# ====================================================================== D
titulo("D. TABLA 3 — CAMINO DE ESPECIFICACIÓN (qué quita cada capa)")


def capa(nombre, piezas):
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"r_ori": M.r_ori.values, "dosis": M.dosis.values,
                       "b3": (M.r_ori * M.dosis).values}, index=M.index)] + piezas,
        axis=1))
    m = sm.WLS(M.r_des, X, weights=M.factor).fit(
        cov_type="cluster", cov_kwds={"groups": M.p19})
    b, se = m.params["b3"] * K, m.bse["b3"] * K
    di(f"  {nombre:52s} {b:+9.4f} {se:8.4f} {b/se:+7.2f}")
    return {"nombre": nombre, "b3": float(b), "se": float(se), "t": float(b / se)}


E = pd.get_dummies(M.p19.astype(int), prefix="e", drop_first=True).astype(float)
C = pd.get_dummies(M.nac.astype(int), prefix="c", drop_first=True).astype(float)
di(f"{'Capa':54s} {'b3':>9} {'ee':>8} {'t':>7}")
t3 = [capa("(1) No controls", []),
      capa("(2) + state and birth-year fixed effects", [E, C]),
      capa("(3) + state x origin rank", [E, C, E.mul(M.r_ori, axis=0).add_prefix("ri_")]),
      capa("(4) + birth-year x origin rank (full model)",
           [E, C, E.mul(M.r_ori, axis=0).add_prefix("ri_"),
            C.mul(M.r_ori, axis=0).add_prefix("rc_")])]
pd.DataFrame(t3).to_csv(f"{SAL}/t3_capas.csv", index=False)
R["capas"] = t3

# ====================================================================== E
titulo("E. POTENCIA Y COTAS")
mde_u = 2.8 * (SE0 / K)
di(f"Escala cruda (por unidad de dosis)")
di(f"  ee = {SE0/K:.4f}   EMD = {mde_u:.4f}   = {mde_u/PEND:.0%} de la pendiente")
di(f"Escala reportada (por d.e. de intensidad)")
di(f"  ee = {SE0:.4f}   EMD = {2.8*SE0:.4f}   = {2.8*SE0/PEND:.0%} de la pendiente")
di(f"\nEMD = 2.8 x ee, donde 2.8 = 1.96 (significancia) + 0.84 (potencia de 80 %)")
R["potencia"] = {"se_unidad": float(SE0 / K), "emd_unidad": float(mde_u),
                 "emd_unidad_pct": float(mde_u / PEND),
                 "se_de": float(SE0), "emd_de": float(2.8 * SE0),
                 "emd_de_pct": float(2.8 * SE0 / PEND)}

# ====================================================================== F
titulo("F. INFERENCIA POR PERMUTACIÓN (2 000 reasignaciones de intensidad)")
rng = np.random.default_rng(SEED)
ents = sorted(M.p19.unique())
FE = sm.add_constant(pd.concat(
    [pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index), E, C,
     E.mul(M.r_ori, axis=0).add_prefix("ri_"),
     C.mul(M.r_ori, axis=0).add_prefix("rc_")], axis=1)).to_numpy()
sw = np.sqrt(M.factor.to_numpy())
Q, _ = np.linalg.qr(FE * sw[:, None])
res = lambda v: (v * sw) - Q @ (Q.T @ (v * sw))
ry, ro, fr = res(M.r_des.to_numpy()), M.r_ori.to_numpy(), M.frac.to_numpy()
idx = {e: (M.p19 == e).to_numpy() for e in ents}
iv = np.array([M[M.p19 == e].intens.iloc[0] for e in ents])


def b3_de(vec):
    dos = np.empty(len(M))
    for e, v in zip(ents, vec):
        dos[idx[e]] = v
    dos = dos * fr
    A = np.column_stack([res(dos), res(ro * dos)])
    return np.linalg.lstsq(A, ry, rcond=None)[0][1]


real = b3_de(iv)
nulo = np.array([b3_de(rng.permutation(iv)) for _ in range(2000)])
p_perm = float((np.abs(nulo) >= abs(real)).mean())
q = np.percentile(nulo, [2.5, 97.5])
di(f"  b3 observado (escala d.e.) : {real*K:+.4f}")
di(f"  p de permutación           : {p_perm:.3f}")
di(f"  nulo al 95 %               : [{q[0]*K:+.4f}, {q[1]*K:+.4f}]")
R["permutacion"] = {"b3": float(real * K), "p": p_perm,
                    "nulo_bajo": float(q[0] * K), "nulo_alto": float(q[1] * K),
                    "n_perm": 2000}

# ====================================================================== G
titulo("G. TABLA 4 — ESTUDIO DE EVENTOS (DISEÑO ESTATAL)")
cortes = [1958, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998]
etiq = ["<=1970", "1971-74", "1975-78", "1979-82", "1983-86", "1987-90",
        "1991-94", "1995-98"]
M = M.copy()
M["grp"] = pd.cut(M.nac, cortes, labels=etiq)
REF = "1979-82"
G = pd.get_dummies(M.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
X = sm.add_constant(pd.concat([
    pd.DataFrame({"r_ori": M.r_ori.values}, index=M.index),
    G.mul(M.intens, axis=0).add_prefix("d_"),
    G.mul(M.r_ori * M.intens, axis=0).add_prefix("ev_"),
    E, C, E.mul(M.r_ori, axis=0).add_prefix("ri_"),
    C.mul(M.r_ori, axis=0).add_prefix("rc_")], axis=1))
me = sm.WLS(M.r_des, X, weights=M.factor).fit(
    cov_type="cluster", cov_kwds={"groups": M.p19})
ev = []
for e_ in etiq:
    if e_ == REF:
        ev.append({"grupo": e_, "b": 0.0, "se": 0.0, "t": np.nan,
                   "ref": True, "previo": False})
        continue
    k = f"ev_g_{e_}"
    b, se = me.params[k] * K, me.bse[k] * K
    prev = bool((M.dosis[M.grp == e_] == 0).all())
    ev.append({"grupo": e_, "b": float(b), "se": float(se), "t": float(b / se),
               "ref": False, "previo": prev})
evd = pd.DataFrame(ev)
evd.to_csv(f"{SAL}/t4_evento_estatal.csv", index=False)
di(evd.round(4).to_string(index=False))
PRE = [e_ for e_ in etiq if e_ != REF and (M.dosis[M.grp == e_] == 0).all()]
ft = me.f_test([f"ev_g_{e_}=0" for e_ in PRE])
di(f"\n  Grupos previos al repunte: {', '.join(PRE)}")
di(f"  Prueba conjunta: F = {float(ft.fvalue):.3f}   p = {float(ft.pvalue):.3f}")
R["evento_estatal"] = {"coef": ev, "grupos_previos": PRE,
                       "F": float(ft.fvalue), "p": float(ft.pvalue),
                       "referencia": REF}

# ====================================================================== H
titulo("H. TABLA 5 — HETEROGENEIDAD Y DESENLACES ALTERNATIVOS")
di(f"{'Submuestra o desenlace':50s} {'b3':>9} {'ee':>8} {'t':>7} {'n':>7}")
t5 = []
for nom, sub in [("Women", M[M.mujer == 1]), ("Men", M[M.mujer == 0]),
                 ("Rural origin", M[M.rural == 1]),
                 ("Urban origin", M[M.rural == 0]),
                 ("Origin in Q1-Q2", M[M.q_ori <= 2]),
                 ("Origin in Q4-Q5", M[M.q_ori >= 4])]:
    try:
        t5.append(fila(nom, sub))
    except Exception as ex:
        di(f"  {nom:48s} no estimable ({type(ex).__name__})")
try:
    t5.append(fila("Outcome: schooling rank", M.dropna(subset=["r_des_ed"]),
                   y="r_des_ed"))
except Exception as ex:
    di(f"  schooling rank: {ex}")
pd.DataFrame(t5).to_csv(f"{SAL}/t5_heterogeneidad.csv", index=False)
R["heterogeneidad"] = t5

# ====================================================================== I
titulo("I. PRIMERA ETAPA — ¿MOVIÓ LA VIOLENCIA ALGO MÁS?")
di(f"{'Desenlace':50s} {'b_dosis':>9} {'ee':>8} {'t':>7}")
t6 = []
for nom, y in [("Years of schooling", "ed_yo"),
               ("Destination asset index (level)", "idx_des"),
               ("Inter-state migration", "migro")]:
    d = df[df.p19 <= 32].dropna(subset=[y]).copy() if nom.endswith("migration") \
        else M.dropna(subset=[y]).copy()
    Ex = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    Cx = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    X = sm.add_constant(pd.concat(
        [pd.DataFrame({"dosis": d.dosis.values}, index=d.index), Ex, Cx], axis=1))
    m = sm.WLS(pd.to_numeric(d[y], errors="coerce"), X, weights=d.factor).fit(
        cov_type="cluster", cov_kwds={"groups": d.p19})
    k = escala(d)
    b, se = m.params["dosis"] * k, m.bse["dosis"] * k
    di(f"  {nom:48s} {b:+9.4f} {se:8.4f} {b/se:+7.2f}")
    t6.append({"desenlace": nom, "b": float(b), "se": float(se),
               "t": float(b / se), "n": int(len(d)),
               "cota_sup": float(b + 1.96 * se)})
pd.DataFrame(t6).to_csv(f"{SAL}/t6_primera_etapa.csv", index=False)
R["primera_etapa"] = t6

# ====================================================================== J
titulo("J. DISEÑO MUNICIPAL")
from municipal import construir_municipal, estimar, evento_municipal, dummies_tam

Mm = construir_municipal(verbose=True)
di("")
t7 = []
# conteos vs tasa, ambos en desviación intraestatal
Mm["Im_conteo"] = (Mm.Im_conteo - Mm.Im_conteo.mean()) / Mm.Im_conteo.std()
Mm["Dc"] = Mm.Im_conteo - Mm.groupby("p19").Im_conteo.transform("mean")
Mm["dosis_c"] = Mm.Dc * Mm.frac
# Dos correlaciones distintas y conviene no mezclarlas. En niveles, el conteo
# de homicidios confunde violencia con tamaño de ciudad. En desviación
# intraestatal, que es la variación que el diseño usa de verdad, la confusión
# es menor pero sigue ahí.
corr_c_niv = float(np.corrcoef(Mm.Im_conteo, Mm.rural)[0, 1])
corr_r_niv = float(np.corrcoef(Mm.Im, Mm.rural)[0, 1])
corr_c = float(np.corrcoef(Mm.Dc, Mm.rural)[0, 1])
corr_r = float(np.corrcoef(Mm.Dm, Mm.rural)[0, 1])
di(f"Correlación con ruralidad, en niveles        : conteo {corr_c_niv:+.3f}   "
   f"tasa {corr_r_niv:+.3f}")
di(f"Correlación con ruralidad, intraestatal      : conteo {corr_c:+.3f}   "
   f"tasa {corr_r:+.3f}")
di("")
di(f"{'Especificación':56s} {'b3':>9} {'ee':>8} {'t':>7}")
b, se = estimar(Mm, "dosis_c", etiq="(1) Within-state dose from counts",
                esc=Mm.Dc.std())
t7.append({"nombre": "(1) Within-state dose from counts", "b3": float(b),
           "se": float(se), "t": float(b / se), "n": int(len(Mm))})
b, se = estimar(Mm, "dosis_m", etiq="(2) Within-state dose from rate per 100,000")
t7.append({"nombre": "(2) Within-state dose from rate", "b3": float(b),
           "se": float(se), "t": float(b / se), "n": int(len(Mm)),
           "emd_pct": float(2.8 * se / pend_base(Mm))})
tams = dummies_tam(Mm)
b, se = estimar(Mm, "dosis_m", controles=tams,
                etiq="(3) Rate, controlling locality size x rank")
t7.append({"nombre": "(3) Rate + locality size x rank", "b3": float(b),
           "se": float(se), "t": float(b / se), "n": int(len(Mm))})
b, se = estimar(Mm, "dosis_m", cl="p19",
                etiq="(4) Rate, standard errors clustered by state")
t7.append({"nombre": "(4) Rate, clustered by state", "b3": float(b),
           "se": float(se), "t": float(b / se), "n": int(len(Mm))})
pd.DataFrame(t7).to_csv(f"{SAL}/t7_municipal.csv", index=False)

di("\nEstudio de eventos municipal (con tasa):")
p_evm = evento_municipal(Mm)
R["municipal"] = {"n": int(len(Mm)), "municipios": int(Mm.mun.nunique()),
                  "corr_conteo_rural": corr_c, "corr_tasa_rural": corr_r,
                  "corr_conteo_rural_nivel": corr_c_niv,
                  "corr_tasa_rural_nivel": corr_r_niv,
                  "de_total": float(Mm.Im.std()), "de_intra": float(Mm.Dm.std()),
                  "especificaciones": t7, "p_evento": float(p_evm),
                  "pendiente_base": pend_base(Mm)}

# ====================================================================== K
titulo("K. CONGLOMERADOS DE TRAYECTORIAS (componente de ciencia de datos)")
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.neighbors import NearestNeighbors

W = panel.pivot(index="cve", columns="year", values="indice").sort_index()
anios = W.columns.values
F = W.sub(W.mean(axis=1), axis=0).div(W.std(axis=1), axis=0)
Xc = F.values
di(f"Matriz de trayectorias: {Xc.shape[0]} entidades x {Xc.shape[1]} años "
   f"({anios.min()}-{anios.max()})")

Z = linkage(Xc, method="ward")
coph = float(np.corrcoef(pdist(Xc), cophenet(Z))[0, 1])
di(f"\nWard. Correlación cofenética: {coph:.3f}")
sil_w, sil_k = {}, {}
for k in range(2, 9):
    etw = fcluster(Z, k, criterion="maxclust")
    sil_w[k] = float(silhouette_score(Xc, etw))
    km = KMeans(n_clusters=k, n_init=50, random_state=SEED).fit(Xc)
    sil_k[k] = float(silhouette_score(Xc, km.labels_))
    di(f"  k={k}:  silueta Ward {sil_w[k]:.3f}   silueta k-medias {sil_k[k]:.3f}   "
       f"tamaños Ward {np.bincount(etw)[1:]}")
K_USO = 3
km = KMeans(n_clusters=K_USO, n_init=50, random_state=SEED).fit(Xc)
ward = fcluster(Z, K_USO, criterion="maxclust")
ari = float(adjusted_rand_score(ward, km.labels_))
di(f"\n  k elegido = {K_USO}. Índice de Rand ajustado Ward vs k-medias: {ari:.3f}")

# estabilidad por submuestreo: partición de la muestra de entidades
rng2 = np.random.default_rng(SEED)
aris = []
for _ in range(500):
    sel = rng2.choice(len(Xc), size=int(len(Xc) * 0.8), replace=False)
    zz = linkage(Xc[sel], method="ward")
    aris.append(adjusted_rand_score(ward[sel],
                                    fcluster(zz, K_USO, criterion="maxclust")))
aris = np.array(aris)
di(f"  Estabilidad (500 submuestras del 80 % de las entidades): "
   f"Rand ajustado medio {aris.mean():.3f}, p5 {np.percentile(aris,5):.3f}")

d4 = np.sort(NearestNeighbors(n_neighbors=4).fit(Xc).kneighbors(Xc)[0][:, -1])
dbs = []
for eps in [2.5, 3.0, 3.5, 4.0]:
    lab = DBSCAN(eps=eps, min_samples=3).fit(Xc).labels_
    dbs.append({"eps": eps, "k": int(len(set(lab) - {-1})),
                "ruido": int((lab == -1).sum())})
    di(f"  DBSCAN eps={eps}: {dbs[-1]['k']} conglomerado(s), "
       f"{dbs[-1]['ruido']} entidades como ruido")

et = pd.Series(ward, index=W.index, name="cg")
perfiles = []
for c in sorted(et.unique()):
    ent = et[et == c].index
    perfil = F.loc[ent].mean()
    pico = int(anios[np.argmax(perfil.values)])
    niv = float(panel[(panel.year >= 2007) & (panel.year <= 2017)]
                .groupby("cve").indice.mean().reindex(ent).mean())
    perfiles.append({"cg": int(c), "n_entidades": int(len(ent)), "pico": pico,
                     "intensidad_media": niv,
                     "entidades": [ABREV.get(int(e), str(e)) for e in ent]})
    di(f"\n  Conglomerado {c} ({len(ent)} entidades)  pico {pico}  "
       f"intensidad media {niv:+.3f}")
    di(f"    {', '.join(perfiles[-1]['entidades'])}")

M["cg"] = M.p19.map(et)
di("")
di(f"{'El modelo dentro de cada conglomerado':50s} {'b3':>9} {'ee':>8} {'t':>7} {'n':>7}")
porcg = []
pico_de = {p["cg"]: p["pico"] for p in perfiles}
for c in sorted(et.unique()):
    s = M[M.cg == c]
    try:
        f_ = fila(f"Cluster {c} (peak {pico_de[int(c)]})", s)
        rb, pp, ic = permutar_cg(s, n_perm=2000, semilla=SEED)
        f_.update({"cg": int(c), "entidades": int(s.p19.nunique()),
                   "p_perm": float(pp), "b3_perm": float(rb * K)})
        di(f"      permutación dentro del conglomerado: p = {pp:.3f}")
        porcg.append(f_)
    except Exception as ex:
        di(f"  Cluster {c}: no estimable ({type(ex).__name__}: {ex})")
pd.DataFrame(porcg).to_csv(f"{SAL}/t8_por_conglomerado.csv", index=False)
pd.DataFrame([{"k": k, "silueta_ward": sil_w[k], "silueta_kmedias": sil_k[k]}
              for k in sil_w]).to_csv(f"{SAL}/t9_silueta.csv", index=False)
et.to_frame().to_csv(f"{SAL}/conglomerados_entidad.csv")

R["conglomerados"] = {
    "n_entidades": int(Xc.shape[0]), "anios": [int(anios.min()), int(anios.max())],
    "cofenetica": coph, "silueta_ward": sil_w, "silueta_kmedias": sil_k,
    "k_elegido": K_USO, "ari_ward_kmedias": ari,
    "estabilidad_ari_media": float(aris.mean()),
    "estabilidad_ari_p5": float(np.percentile(aris, 5)),
    "dbscan": dbs, "perfiles": perfiles, "por_conglomerado": porcg,
    "d4_mediana": float(np.median(d4))}

# ====================================================================== fin
guardar(R, f"{SAL}/resultados.json")
with open(f"{SAL}/log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
M.to_pickle(f"{SAL}/M.pkl")
F.to_pickle(f"{SAL}/F_trayectorias.pkl")
np.save(f"{SAL}/Z_ward.npy", Z)
evd.to_pickle(f"{SAL}/ev_estatal.pkl")
di(f"\n\nEscrito: {SAL}/resultados.json  y  {SAL}/log.txt")
