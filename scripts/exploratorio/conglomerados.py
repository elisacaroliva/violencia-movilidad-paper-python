# -*- coding: utf-8 -*-
"""
Componente de ciencia de datos: conglomerados de trayectorias de violencia.

Por qué conglomerados y no simplemente la dosis
-----------------------------------------------
La dosis es un producto de dos cosas: cuánta violencia tuvo la entidad
(intensidad promedio 2007-2017) y cuántos años de la ventana 10-18 de la
persona cayeron después de 2007. El segundo factor es mecánico e idéntico para
todas las entidades: supone que el repunte empezó en 2007 en todas partes.

Eso es una suposición, no un dato. Agrupar las trayectorias sin mirar el
resultado permite contrastarla: si hay entidades cuyo repunte llegó tarde, o
que ya eran violentas desde los noventa, la dosis las está mal clasificando.

Tres algoritmos, como corresponde a un ejercicio no supervisado:
  - Jerárquico de Ward: da el dendrograma y no exige fijar k de antemano.
  - k-medias: particional, se elige k por silueta y se compara con Ward.
  - DBSCAN: basado en densidad; se aplica a entidades y a municipios para
    mostrar en qué régimen de tamaño de muestra sirve y en cuál no.

El resultado se usa de dos maneras: como diagnóstico de la dosis y como una
partición del país construida SIN mirar la movilidad, lo que la vuelve una
heterogeneidad legítima y no una pesca de subgrupos.
"""
import sys, numpy as np, pandas as pd
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from base import construir, muestra, ddd, escala, panel_violencia, ABREV, OUT
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.neighbors import NearestNeighbors
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

MUN = _r.MUN
MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO",
         "SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
COL = ["#3F7CAC", "#A63A2B", "#7D9B76", "#C98F2E", "#8E6BA8"]

# ----------------------------------------------------------- insumos
panel, intens = panel_violencia()
W = panel.pivot(index="cve", columns="year", values="indice").sort_index()
anios = W.columns.values
print(f"Matriz de trayectorias: {W.shape[0]} entidades x {W.shape[1]} años "
      f"({anios.min()}-{anios.max()})")

# La forma de la trayectoria, separada del nivel: cada entidad se estandariza
# consigo misma, así dos entidades con el mismo perfil temporal quedan juntas
# aunque una sea mucho más violenta que la otra.
F = W.sub(W.mean(axis=1), axis=0).div(W.std(axis=1), axis=0)
X = F.values

# ------------------------------------------------- 1. jerárquico de Ward
Z = linkage(X, method="ward")
print("\n" + "=" * 78)
print("1. JERÁRQUICO DE WARD")
print("=" * 78)
coph = np.corrcoef(pdist(X), __import__("scipy.cluster.hierarchy", fromlist=["cophenet"]).cophenet(Z))[0, 1]
print(f"  Correlación cofenética: {coph:.3f} "
      f"(qué tan fiel es el dendrograma a las distancias reales)")
for k in range(2, 7):
    et = fcluster(Z, k, criterion="maxclust")
    print(f"  k={k}: silueta {silhouette_score(X, et):.3f}   "
          f"tamaños {np.bincount(et)[1:]}")

# ------------------------------------------------------- 2. k-medias
print("\n" + "=" * 78)
print("2. K-MEDIAS")
print("=" * 78)
sil = {}
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=50, random_state=7).fit(X)
    sil[k] = silhouette_score(X, km.labels_)
    print(f"  k={k}: silueta {sil[k]:.3f}   inercia {km.inertia_:7.1f}   "
          f"tamaños {np.bincount(km.labels_)}")
K_OPT = max(sil, key=sil.get)
print(f"  Mejor silueta en k={K_OPT}")

K_USO = 3      # se fija en 3 por interpretabilidad; ver comentario abajo
km = KMeans(n_clusters=K_USO, n_init=50, random_state=7).fit(X)
ward = fcluster(Z, K_USO, criterion="maxclust")
print(f"\n  Acuerdo entre Ward y k-medias con k={K_USO}: "
      f"índice de Rand ajustado {adjusted_rand_score(ward, km.labels_):.3f}")

# ---------------------------------------------------- 3. DBSCAN
print("\n" + "=" * 78)
print("3. DBSCAN")
print("=" * 78)
d4 = np.sort(NearestNeighbors(n_neighbors=4).fit(X).kneighbors(X)[0][:, -1])
print(f"  Entidades (n={len(X)}). Distancia al 4º vecino: mediana {np.median(d4):.2f}, "
      f"rango [{d4.min():.2f}, {d4.max():.2f}]")
for eps in [2.5, 3.0, 3.5, 4.0]:
    lab = DBSCAN(eps=eps, min_samples=3).fit(X).labels_
    nc, nr = len(set(lab) - {-1}), (lab == -1).sum()
    print(f"    eps={eps}: {nc} conglomerado(s), {nr} entidades marcadas como ruido")
print("  Con 32 observaciones la densidad es demasiado escasa: DBSCAN manda a")
print("  ruido a buena parte del país. Es el algoritmo equivocado a este nivel.")

# --------------------------------------------- DBSCAN a nivel municipal
mu = pd.read_csv(MUN, encoding="latin-1", low_memory=False)
mu["tot"] = mu[MESES].apply(pd.to_numeric, errors="coerce").sum(axis=1)
h = mu[(mu.MODALIDAD == "HOMICIDIOS") & (mu.TIPO == "DOLOSOS")]
h = h[h["AÑO"].between(2011, 2017)]
Wm = h.groupby(["INEGI", "AÑO"]).tot.sum().unstack().fillna(0)
Wm = Wm[Wm.sum(axis=1) >= 35]                      # municipios con señal
Fm = np.log1p(Wm)
Fm = Fm.sub(Fm.mean(axis=1), axis=0).div(Fm.std(axis=1).replace(0, np.nan), axis=0).dropna()
Xm = Fm.values
print(f"\n  Municipios (n={len(Xm)}, al menos 35 homicidios en 2011-2017)")
for eps in [0.8, 1.0, 1.2]:
    lab = DBSCAN(eps=eps, min_samples=10).fit(Xm).labels_
    nc, nr = len(set(lab) - {-1}), (lab == -1).sum()
    print(f"    eps={eps}: {nc} conglomerado(s), {nr/len(lab):.0%} como ruido")
print("  Aquí sí hay densidad y DBSCAN separa el grueso de los municipios de")
print("  una cola de trayectorias atípicas, que es justo para lo que sirve.")

# ------------------------------------- caracterización de los conglomerados
et = pd.Series(ward, index=W.index, name="cg")
print("\n" + "=" * 78)
print(f"CARACTERIZACIÓN DE LOS {K_USO} CONGLOMERADOS (Ward)")
print("=" * 78)
nombres = {}
for c in sorted(et.unique()):
    ent = et[et == c].index
    perfil = F.loc[ent].mean()
    pico = int(anios[np.argmax(perfil.values)])
    niv = intens.reindex(ent).mean()
    arriba = [int(a) for a in anios if perfil[a] > 0]
    nombres[c] = f"pico {pico}"
    print(f"\n  Conglomerado {c}  ({len(ent)} entidades)")
    print(f"    Año del máximo del perfil: {pico}   "
          f"años por encima de su propia media: {min(arriba)}-{max(arriba)}")
    print(f"    Intensidad media 2007-2017: {niv:+.3f}")
    print(f"    {', '.join(ABREV.get(int(e), str(e)) for e in ent)}")

# ------------------------------------ el modelo dentro de cada conglomerado
df = construir(verbose=False)
M = muestra(df)
M["cg"] = M.p19.map(et)
K = escala(M)
print("\n" + "=" * 78)
print("EL MODELO DENTRO DE CADA CONGLOMERADO")
print("  (partición hecha sin mirar la movilidad: no es pesca de subgrupos)")
print("=" * 78)
for c in sorted(et.unique()):
    s = M[M.cg == c]
    try:
        m = ddd(s)
        b, se = m.params["b3"] * K, m.bse["b3"] * K
        print(f"  Conglomerado {c} ({nombres[c]:10s}) n={len(s):5d} "
              f"entidades={s.p19.nunique():2d}  b3={b:+.4f} ({se:.4f})  t={b/se:+.2f}")
    except Exception as ex:
        print(f"  Conglomerado {c}: no estimable ({type(ex).__name__})")
print("  Advertencia: con ~10 entidades por conglomerado los errores agrupados")
print("  son poco fiables. De ahí la permutación que sigue.")

# ------------------------------------------------------------------------
# Con 6 a 15 entidades por conglomerado, el error agrupado está sesgado hacia
# abajo y los t de arriba no se pueden creer. La permutación no depende de ese
# supuesto: se reasigna al azar la intensidad ENTRE LAS ENTIDADES DEL MISMO
# conglomerado, se recalcula b3 y se compara el valor real con esa distribución.
# ------------------------------------------------------------------------
def permutar(s, n_perm=2000, semilla=11):
    import statsmodels.api as sm_
    ents = sorted(s.p19.unique())
    E = pd.get_dummies(s.p19.astype(int), prefix="e", drop_first=True).astype(float)
    C = pd.get_dummies(s.nac.astype(int), prefix="c", drop_first=True).astype(float)
    FE = sm_.add_constant(pd.concat(
        [pd.DataFrame({"r_ori": s.r_ori.values}, index=s.index), E, C,
         E.mul(s.r_ori, axis=0).add_prefix("ri_"),
         C.mul(s.r_ori, axis=0).add_prefix("rc_")], axis=1)).to_numpy()
    sw = np.sqrt(s.factor.to_numpy())
    Q, _ = np.linalg.qr(FE * sw[:, None])
    res = lambda v: (v * sw) - Q @ (Q.T @ (v * sw))
    ry, ro, fr = res(s.r_des.to_numpy()), s.r_ori.to_numpy(), s.frac.to_numpy()
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
    p = (np.abs(nulo) >= abs(real)).mean()
    return real, p, np.percentile(nulo, [2.5, 97.5])

print("\n" + "=" * 78)
print("INFERENCIA POR PERMUTACIÓN DENTRO DE CADA CONGLOMERADO")
print("=" * 78)
for c in sorted(et.unique()):
    s = M[M.cg == c]
    real, p, ic = permutar(s)
    print(f"  Conglomerado {c} ({nombres[c]:10s}) entidades={s.p19.nunique():2d}  "
          f"b3={real*K:+.4f}  p={p:.3f}  nulo en [{ic[0]*K:+.3f}, {ic[1]*K:+.3f}]")

# ------------------------------------------------------------- figuras
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.3),
                             gridspec_kw={"width_ratios": [1.45, 1]})
dendrogram(Z, labels=[ABREV.get(int(e), str(e)) for e in W.index], ax=a1,
           color_threshold=Z[-(K_USO - 1), 2], above_threshold_color="#B9BEB4",
           leaf_font_size=7.5)
a1.set_title("Dendrograma de trayectorias (Ward)", fontsize=10.5)
a1.set_ylabel("Distancia")
for s_ in ("top", "right"): a1.spines[s_].set_visible(False)
a2.plot(list(sil), list(sil.values()), "o-", color="#3F7CAC", lw=1.6, ms=5)
a2.axvline(K_USO, color="#A63A2B", lw=1.2, ls="--")
a2.set_xlabel("Número de conglomerados (k)"); a2.set_ylabel("Silueta media")
a2.set_title("Selección de k por silueta", fontsize=10.5)
a2.grid(axis="y", color="#e6e6e6", lw=.8); a2.set_axisbelow(True)
for s_ in ("top", "right"): a2.spines[s_].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/g4_conglomerados.png", dpi=200, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(9.2, 4.3))
for j, c in enumerate(sorted(et.unique())):
    ent = et[et == c].index
    ax.plot(anios, F.loc[ent].mean(), lw=2.4, color=COL[j],
            label=f"Conglomerado {c} ({len(ent)} entidades, {nombres[c]})")
    ax.fill_between(anios, F.loc[ent].mean() - F.loc[ent].std(),
                    F.loc[ent].mean() + F.loc[ent].std(), color=COL[j], alpha=.10)
ax.axvline(2007, color="#1A2238", lw=1.1, ls="--")
ax.annotate("2007", (2007, ax.get_ylim()[1]), xytext=(4, -12),
            textcoords="offset points", fontsize=9, color="#1A2238")
ax.axhline(0, color="#666", lw=.8)
ax.set_xticks(np.arange(1997, 2018, 2))
ax.set_xlabel("Año"); ax.set_ylabel("Índice de violencia\n(estandarizado dentro de cada entidad)")
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.grid(axis="y", color="#e6e6e6", lw=.8); ax.set_axisbelow(True)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/g5_trayectorias.png", dpi=200, bbox_inches="tight")
print(f"\nGuardadas: {OUT}/g4_conglomerados.png y {OUT}/g5_trayectorias.png")
et.to_frame().to_csv(f"{OUT}/conglomerados_entidad.csv")
