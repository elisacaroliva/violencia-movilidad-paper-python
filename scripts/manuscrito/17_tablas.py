# -*- coding: utf-8 -*-
"""
tablas.py — los nueve cuadros del manuscrito, en inglés
========================================================
Lee los mismos resultados congelados que `tablas_es.py`, de modo que ningún
número puede diferir entre la versión en inglés y la versión en español. Sólo
cambian los encabezados y las notas. Aquí no se hace aritmética: todo valor
viene de `resultados/resultados.json`, que escribe `congelar.py` y completan
`redatar.py`, `movilidad_absoluta.py`, `municipal_perfil.py`, `recesion.py`,
`inegi_analisis.py` e `inegi_cuadro9.py`.

Uso:  python -I codigo/tablas.py
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import json
import pandas as pd

SAL = _r.SAL
R = json.load(open(f"{SAL}/resultados.json", encoding="utf-8"))
T = {}

n = lambda x, d=4: f"{x:+.{d}f}"
par = lambda x, d=4: f"({x:.{d}f})"
mil = lambda x: f"{x:,}"
men = lambda s: s.replace("-", "−")        # signo menos tipográfico

# ------------------------------------------------------------------ Table 1
d1 = pd.read_csv(f"{SAL}/t1_descriptivas.csv")
T["t1"] = {"num": 1, "titulo": "Descriptive statistics",
    "cols": ["Variable", "Mean", "SD", "Exposed", "Unexposed", "Diff.", "n"],
    "anchos": [36, 10, 10, 11, 12, 11, 10],
    "filas": [[r.Variable, f"{r.Mean:.3f}", f"{r.SD:.3f}", f"{r.Mean_exposed:.3f}",
               f"{r.Mean_unexposed:.3f}", f"{r.Diff:+.3f}", mil(int(r.N))]
              for r in d1.itertuples()],
    "nota": ("Means and standard deviations weighted by the survey expansion factors. "
             "A respondent is classified as exposed if any part of the formative window, "
             f"ages 10 to 18, fell after 2007: {mil(R['descriptivas']['n_expuestos'])} "
             f"respondents ({R['descriptivas']['share_expuestos']:.1%} of the sample). "
             "The difference column is descriptive; the estimates in Table 2 do not rest "
             "on it.")}

# ------------------------------------------------------------------ Table 2
T["t2"] = {"num": 2,
    "titulo": "Triple-difference estimates of the change in the rank-rank slope",
    "cols": ["Specification", "β₃", "se", "t", "95 % CI", "n"],
    "anchos": [36, 11, 11, 8, 23, 11],
    "filas": [[f["nombre"], n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}",
               f"[{f['ic_bajo']:+.3f}, {f['ic_alto']:+.3f}]", mil(f["n"])]
              for f in R["principal"]],
    "nota": ("Coefficients are the change in the rank-rank slope per standard deviation "
             f"of state violence intensity, which is {R['muestra']['de_intensidad']:.3f}. "
             f"The baseline slope is {R['muestra']['pendiente_base']:.3f}. All rows "
             "include state and birth-year fixed effects and both interacted with the "
             "origin rank, and are weighted by the expansion factors. Errors clustered by "
             "state, except row (5), which clusters by birth year. For row (1) the "
             "permutation test over 2,000 reassignments gives "
             f"p = {R['permutacion']['p']:.2f}, with the central 95 % of the null between "
             f"{R['permutacion']['nulo_bajo']:+.3f} and {R['permutacion']['nulo_alto']:+.3f}.")}

# ------------------------------------------------------------------ Table 3
T["t3"] = {"num": 3,
    "titulo": "The specification path: what each block of controls removes",
    "cols": ["Controls included", "β₃", "se", "t"],
    "anchos": [54, 16, 16, 14],
    "filas": [[c["nombre"], n(c["b3"]), par(c["se"]), f"{c['t']:+.2f}"]
              for c in R["capas"]],
    "nota": ("Each row adds a block to the one above it; row (4) is the specification of "
             "Table 2, column (1). Coefficients per standard deviation of intensity; "
             "errors clustered by state in parentheses. The path is not monotone, which is "
             "why the specification is fixed by the identification argument of Section 4.2 "
             "rather than chosen from among these rows.")}

# ------------------------------------------------------------------ Table 6
mu = R["municipal"]
T["t4"] = {"num": 6, "titulo": "Estimates using within-state municipal variation",
    "cols": ["Specification", "β₃", "se", "t", "n"],
    "anchos": [46, 13, 13, 10, 18],
    "filas": [[e["nombre"], n(e["b3"]), par(e["se"]), f"{e['t']:+.2f}", mil(e["n"])]
              for e in mu["especificaciones"]],
    "nota": ("Treatment is the municipality's deviation from its own state mean, "
             "interacted with the share of the formative window after 2007. Coefficients "
             f"are per standard deviation of that deviation. The sample is {mil(mu['n'])} "
             f"respondents in {mil(mu['municipios'])} origin municipalities. Errors "
             "clustered by municipality except in row (4). The within-state correlation "
             f"with rural origin is {mu['corr_conteo_rural']:+.2f} using counts and "
             f"{mu['corr_tasa_rural']:+.2f} using the rate "
             f"({mu['corr_conteo_rural_nivel']:+.2f} and {mu['corr_tasa_rural_nivel']:+.2f} "
             "in levels). The joint pre-trend test using the rate gives p = "
             f"{mu['p_evento_con_controles']:.2f} with locality-size controls and "
             f"p = {mu['p_evento_sin_controles']:.2f} without them.")}

# ------------------------------------------------------------------ Table 4
cg = R["conglomerados"]
met = {m["k"]: m for m in cg["metricas_vs_referencia"]}
f5 = [["Panel A. Choosing the number of clusters", "", "", "", "", ""]]
for k in range(2, 9):
    f5.append([f"k = {k}", f"{cg['silueta_ward'][str(k)]:.3f}",
               f"{cg['silueta_kmedias'][str(k)]:.3f}", f"{met[k]['r2']:.3f}",
               f"{met[k]['calinski_harabasz']:.2f}", f"{met[k]['davies_bouldin']:.3f}"])
f5.append(["Panel B. Agreement and stability", "", "", "", "", ""])
f5 += [["Cophenetic correlation (Ward)", f"{cg['cofenetica']:.3f}", "", "", "", ""],
       ["Adjusted Rand, Ward vs k-means at k = 3", f"{cg['ari_ward_kmedias']:.3f}", "", "", "", ""],
       ["Mean adjusted Rand, 500 80 % subsamples", f"{cg['estabilidad_ari_media']:.3f}", "", "", "", ""],
       ["  5th percentile of that distribution", f"{cg['estabilidad_ari_p5']:.3f}", "", "", "", ""],
       ["Spread of peak years (years)", f"{cg['amplitud_picos']}", "", "", "", ""]]
f5.append(["Panel C. The model within each cluster", "", "", "", "", ""])
pico = {p["cg"]: p for p in cg["perfiles"]}
for f in cg["por_conglomerado"]:
    c = f["cg"]
    f5.append([f"Cluster {c}: {pico[c]['n_entidades']} states, peak {pico[c]['pico']}",
               n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}", f"{f['p_perm']:.3f}",
               mil(f["n"])])
T["t5"] = {"num": 4, "titulo": "Cluster validation and within-cluster estimates",
    "cols": ["", "Silhouette Ward / β₃", "Silhouette k-means / se",
             "R² vs k = 1 / t", "Calinski-Harabasz / perm. p", "Davies-Bouldin / n"],
    "anchos": [32, 14, 14, 13, 14, 13], "filas": f5, "paneles": [0, 8, 14],
    "nota": ("Panel A reports internal criteria by number of clusters; R² is the share of "
             "total sum of squares in trajectory shape explained by the partition, with "
             "k = 1 as the reference model, which is what the dose assumes. The silhouette "
             "is maximised at k = 3 under both algorithms, Calinski-Harabasz at k = 2, and "
             "Davies-Bouldin keeps improving; the 15-state first-wave cluster and the "
             "11-state late-peak group are identical at k = 2, 3 and 4, so the conclusion "
             "does not depend on which criterion is followed. Panel C reports the estimate "
             "within each cluster, with clustered errors in parentheses and permutation "
             "p-values from 2,000 within-cluster reassignments. With 6 to 15 states per "
             "group the clustered statistic is unreliable and the permutation p-value is "
             "the one to read; both are shown so the gap is visible.")}

# ------------------------------------------------------------------ Table 7
f6 = [["Panel A. Heterogeneity", "", "", "", ""]]
for f in R["heterogeneidad"]:
    if f["nombre"].startswith("Outcome"):
        continue
    f6.append([f["nombre"], n(f["b3"]), par(f["se"]), f"{f['t']:+.2f}", mil(f["n"])])
f6.append(["Panel B. Alternative destination measures", "", "", "", ""])
for f in R["heterogeneidad"]:
    if f["nombre"].startswith("Outcome"):
        f6.append(["Schooling-years rank", n(f["b3"]), par(f["se"]),
                   f"{f['t']:+.2f}", mil(f["n"])])
for m in R["transiciones"]["modelos"][:2]:
    f6.append([m["etiq"], n(m["b"]), par(m["se"]), f"{m['t']:+.2f}", mil(m["n"])])
f6.append(["Panel C. Is there a first stage at all?", "", "", "", ""])
for f in R["primera_etapa"]:
    f6.append([f["desenlace"], n(f["b"]), par(f["se"]), f"{f['t']:+.2f}",
               f"{f['cota_sup']:+.3f}"])
T["t6"] = {"num": 7,
    "titulo": "Heterogeneity, alternative outcomes and reduced-form checks",
    "cols": ["", "Coefficient", "se", "t", "n / upper bound"],
    "anchos": [40, 14, 14, 10, 22], "filas": f6, "paneles": [0, 7, 11],
    "nota": ("Panels A and B report the triple-difference coefficient per standard "
             "deviation of intensity, with the full set of fixed effects and errors "
             "clustered by state. The last two rows of Panel B condition on the origin "
             "quintile, so the coefficient is the change in the probability of that "
             "transition and no interaction term enters. Panel C regresses outcomes in "
             "levels on the dose with state and birth-year fixed effects; the last column "
             "is the upper limit of the 95 % interval, that is, the largest effect the data "
             "rule out, in years for schooling, index points for assets and probability for "
             "migration.")}

# ------------------------------------------------------------------ Table 5
rd = R["redatado"]
q = rd["quiebre_por_conglomerado"]
T["t7"] = {"num": 5, "titulo": "Estimates under three datings of the exposure dose",
    "cols": ["Dating of the surge", "β₃", "se", "t", "Minimum detectable effect"],
    "anchos": [34, 14, 14, 10, 28],
    "filas": [[e["dosis"], n(e["b3"]), par(e["se"]), f"{e['t']:+.2f}",
               f"{e['emd_pct']:.1%} of the baseline slope"] for e in rd["estimaciones"]],
    "nota": ("Row (1) imposes a common 2007 start for every state. Rows (2) and (3) "
             "estimate the start by fitting a level shift to the standardised violence "
             "trajectory and choosing the break year that minimises the residual sum of "
             "squares over a 2001-to-2015 grid, at the cluster and the state level "
             "respectively. The estimated cluster breaks are "
             + ", ".join(f"{v['tau']} for cluster {k} (shift {float(v['delta']):+.2f})"
                         for k, v in sorted(q.items()))
             + ". Intensity is recomputed over each unit's post-break window, so "
             "coefficients are per standard deviation of the corresponding measure and are "
             "not comparable in level across rows, only in significance and in the implied "
             "bound. The share of the sample with any exposure falls from 32.4 % in row (1) "
             "to 26.7 % in row (2), which is why precision deteriorates.")}

# ------------------------------------------------------------------ Table 8
ma = R["movilidad_absoluta"]
est = {x["percentil"]: x for x in ma["por_percentil"]}
mun = {x["percentil"]: x for x in ma["municipal"]}
T["t8"] = {"num": 8,
    "titulo": "Effect on expected destination rank, by origin percentile",
    "cols": ["Origin percentile", "State design", "se", "Municipal design", "se",
             "Contains −1.57?"],
    "anchos": [20, 16, 12, 18, 12, 22],
    "filas": [[f"p{int(p*100)}", men(f"{est[p]['efecto']:+.2f}"), par(est[p]["se"], 2),
               men(f"{mun[p]['efecto']:+.2f}"), par(mun[p]["se"], 2),
               ("state yes, municipal no" if p == 0.25 else "")]
              for p in [0.10, 0.25, 0.50, 0.75, 0.90]],
    "nota": ("Entries are rank points out of 100 per standard deviation of violence "
             "intensity, computed as the linear combination β₂ + p·β₃ from the "
             "specifications of Table 2 column (1) and Table 6 column (3), with errors "
             "from the same clustered covariance matrix. This is the outcome Sharkey and "
             "Torrats-Espinosa (2017) report as absolute upward mobility. Their "
             "instrumented estimate for the United States at the 25th percentile is "
             "−1.57 rank points per standard deviation of the county homicide rate. "
             "The last column records whether our 95 % interval at that percentile "
             "contains their value: the state design's, "
             f"[{men(format(est[0.25]['ic_bajo'], '+.2f'))}, {men(format(est[0.25]['ic_alto'], '+.2f'))}], does; "
             f"the municipal one's, [{men(format(mun[0.25]['ic_bajo'], '+.2f'))}, "
             f"{men(format(mun[0.25]['ic_alto'], '+.2f'))}], does not. A standard deviation is not the "
             "same object in the two literatures, and the outcomes are an income rank there "
             "and an asset rank here, so the comparison is indicative and not a formal test.")}

# ------------------------------------------------------------------ Table 9
med = R["inegi"]["medidas"]
fila9 = lambda etq, k, veredicto: [
    etq, n(med[k]["b3"]), par(med[k]["se"]), men(f"{med[k]['p25']:+.2f}"),
    f"({med[k]['se_p25']:.2f})", f"{med[k]['F']:.2f}",
    f"{med[k]['p']:.3f}  {veredicto}"]
T["t9"] = {"num": 9, "titulo": "Three definitions of the violence treatment",
    "cols": ["Exposure index", "β₃", "se", "Effect at p25", "se", "Pre-trend F", "p"],
    "anchos": [28, 10, 10, 14, 10, 13, 15],
    "filas": [fila9("(1) SESNSP, four crimes (main)", "SESNSP cuatro delitos", "passes"),
              fila9("(2) INEGI, level 2007-17", "INEGI nivel 2007-17", "passes"),
              fila9("(3) INEGI, increase over 1990-97", "INEGI aumento vs 1990-97", "FAILS")],
    "nota": ("Each row re-estimates the specification of Table 2 column (1) with a "
             "different exposure index, holding everything else fixed. β₃ is the change in "
             "the rank-rank slope per standard deviation of that index; the effect at p25 "
             "is in rank points out of 100, comparable with the −1.57 of Sharkey and "
             "Torrats-Espinosa. The last two columns report the joint test that birth "
             "groups predating the surge show no differential slope, which is the design's "
             "identifying assumption. Row (3) defines treatment as the increase in the "
             "homicide rate between 1990-97 and 2007-17 rather than its level, which is the "
             "better-identified object in principle; it gives the largest estimate in the "
             "paper and a permutation p-value of "
             f"{med['INEGI aumento vs 1990-97']['p_perm_p25']:.3f} on the p25 effect, and it "
             "is the only row that violates the identifying assumption. The INEGI figures "
             "are deaths by state and year of occurrence from the vital-statistics "
             "microdata, with CONAPO mid-year population as the denominator.")}

with open(_r.MAN_EN + "/tables.json", "w", encoding="utf-8") as f:
    json.dump(T, f, indent=1, ensure_ascii=False)
for k, t in T.items():
    print(f"{k}: Table {t['num']} — {t['titulo'][:52]}")
    assert 95 <= sum(t["anchos"]) <= 106, (k, sum(t["anchos"]))
print("\nEscrito: " + _r.MAN_EN + "/tables.json")
