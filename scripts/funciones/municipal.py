# -*- coding: utf-8 -*-
"""
Diseño municipal dentro del estado.

Por qué
-------
El 64 % de la varianza del homicidio municipal que ven nuestros encuestados
está DENTRO de su estado. Medir el tratamiento a nivel entidad promedia esa
variación y atenúa el coeficiente.

Pero el beneficio mayor no es de precisión. Si el tratamiento varía dentro del
estado, se pueden incluir efectos fijos de estado por cohorte, que absorben
cualquier choque común a un estado en un momento dado: la pandemia, el fin de
PROSPERA, Escuelas de Tiempo Completo, cambios de gobierno estatal. A nivel
entidad eso es imposible, porque estado por cohorte ES la variación de
tratamiento. A nivel municipal, no.

Construcción
------------
  Im = log(1 + homicidios dolosos 2011-2017) del municipio, estandarizado
  Dm = Im menos la media de su estado  -> variación puramente intraestatal
  dosis_m = Dm x fracción de la ventana formativa posterior a 2007

Dos límites que hay que declarar
--------------------------------
1. La serie municipal del SESNSP empieza en 2011, así que aquí no se puede
   correr la prueba de tendencias previas. La validación sigue viniendo del
   diseño estatal, que sí tiene periodo previo desde 1997.
2. El SESNSP municipal no trae población, así que Im es un conteo en
   logaritmos y no una tasa. Un municipio grande tiene más homicidios de
   manera mecánica. Se controla el tamaño de localidad de origen interactuado
   con el rango, pero con proyecciones municipales de CONAPO se podría
   construir la tasa correcta.
"""
import sys, numpy as np, pandas as pd, statsmodels.api as sm
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
from base import construir, muestra, panel_violencia

POB = _r.POB
MUN = _r.MUN
MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO",
         "SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
GRUPOS = [1958, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998]


def homicidios_municipales():
    mu = pd.read_csv(MUN, encoding="latin-1", low_memory=False)
    mu["tot"] = mu[MESES].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    h = mu[(mu.MODALIDAD == "HOMICIDIOS") & (mu.TIPO == "DOLOSOS")]
    return h.groupby(["INEGI", "AÑO"]).tot.sum().unstack()


def construir_municipal(verbose=True):
    H = homicidios_municipales()
    tot = H.loc[:, 2011:2017].sum(axis=1)

    if verbose:
        # ¿es persistente el ranking municipal? Es el supuesto que sustituye
        # a la prueba de tendencias previas, que aquí no se puede correr.
        a = np.log1p(H.loc[:, 2011:2013].sum(axis=1))
        b = np.log1p(H.loc[:, 2015:2017].sum(axis=1))
        ok = a.notna() & b.notna() & ((a > 0) | (b > 0))
        print(f"Persistencia del ranking municipal: correlación entre 2011-2013 "
              f"y 2015-2017 = {np.corrcoef(a[ok], b[ok])[0,1]:.3f}  (n={ok.sum():,})")

    df = construir(verbose=False)
    M = muestra(df)
    M["mun"] = pd.to_numeric(M.p20_COD, errors="coerce")
    M = M[M.mun.between(1001, 32999)].copy()          # descarta códigos de no respuesta
    # El conteo en logaritmos confunde violencia con tamaño del municipio: se
    # correlaciona −0.30 con la ruralidad, y con él el diseño no pasa la prueba
    # de tendencias previas. La tasa lo corrige. El denominador son las
    # proyecciones municipales de CONAPO, población a mitad de año promediada
    # sobre 2011-2017.
    pob = pd.read_csv(POB).set_index("CLAVE").pob
    hom_anual = M.mun.map(tot) / 7.0
    M["Im"] = np.log1p(hom_anual / M.mun.map(pob) * 1e5)   # tasa por 100 000
    M["Im_conteo"] = np.log1p(M.mun.map(tot))
    M = M.dropna(subset=["Im"]).copy()
    M["Im"] = (M.Im - M.Im.mean()) / M.Im.std()
    # desviación intraestatal: lo que queda al quitar la media de su entidad
    M["Dm"] = M.Im - M.groupby("p19").Im.transform("mean")
    M["dosis_m"] = M.Dm * M.frac
    M["grp"] = pd.cut(M.nac, GRUPOS, labels=[f"g{i}" for i in range(8)])
    M["tam"] = M.p21.fillna(9).astype(int)            # tamaño de localidad a los 14

    if verbose:
        print(f"\nMuestra municipal: {len(M):,} personas en {M.mun.nunique():,} municipios")
        print(f"  d.e. de la intensidad municipal: total {M.Im.std():.2f}  "
              f"intraestatal {M.Dm.std():.2f}")
        print(f"  personas por municipio: mediana {M.groupby('mun').size().median():.0f}, "
              f"máximo {M.groupby('mun').size().max()}")
    return M


def estimar(d, termino, controles=(), ef_estado_cohorte=False, cl="mun", etiq="",
            esc=None):
    """Estima el coeficiente de rango de origen x <termino>."""
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    piezas = [pd.DataFrame({"r_ori": d.r_ori.values, "trat": d[termino].values,
                            "b3": (d.r_ori * d[termino]).values}, index=d.index),
              C, C.mul(d.r_ori, axis=0).add_prefix("rc_")]
    if ef_estado_cohorte:
        # Absorbe cualquier choque común a un estado en un grupo de cohortes.
        # Los efectos fijos de entidad quedan anidados dentro de éstos, así que
        # incluirlos además vuelve singular la matriz: se omiten.
        EC = pd.get_dummies(d.p19.astype(int).astype(str) + "_" + d.grp.astype(str),
                            prefix="ec", drop_first=True).astype(float)
        piezas += [EC, EC.mul(d.r_ori, axis=0).add_prefix("ecr_")]
    else:
        E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
        piezas += [E, E.mul(d.r_ori, axis=0).add_prefix("ri_")]
    for c in controles:
        piezas.append(pd.DataFrame({f"x_{c}": d[c].values,
                                    f"xr_{c}": (d[c] * d.r_ori).values}, index=d.index))
    X = sm.add_constant(pd.concat(piezas, axis=1))
    m = sm.WLS(d.r_des, X, weights=d.factor).fit(cov_type="cluster",
                                                 cov_kwds={"groups": d[cl]})
    # Escala de reporte: una desviación estándar del tratamiento. Para la dosis
    # estatal es la d.e. ENTRE entidades; para la municipal, la de la desviación
    # intraestatal. Se puede pasar explícita con `esc`.
    if esc is not None:
        k = esc
    elif termino == "dosis":
        k = d.groupby("p19").intens.first().std()
    else:
        k = d[termino.replace("dosis_m", "Dm").replace("dosis_c", "Dc")].std()
    b, se = m.params["b3"] * k, m.bse["b3"] * k
    pend = np.polyfit(d.r_ori, d.r_des, 1, w=np.sqrt(d.factor))[0]
    print(f"  {etiq:54s} b3={b:+.4f} ({se:.4f})  t={b/se:+.2f}  EMD {2.8*se/pend:4.0%}")
    return b, se


def dummies_tam(d):
    T = pd.get_dummies(d.tam.astype(int), prefix="t", drop_first=True).astype(float)
    for c in T.columns:
        d[c] = T[c]
    return list(T.columns)


def evento_municipal(d, controles=(), cl="mun"):
    """
    Estudio de eventos a nivel municipal.

    Sustituye la dosis por interacciones de rango x intensidad municipal con
    cada grupo de nacimiento. Los grupos cuya ventana formativa terminó antes
    de 2007 tienen dosis mecánicamente cero, así que un coeficiente distinto
    de cero en ellos es una tendencia previa diferencial: la señal de que la
    variación municipal está confundida con algo estructural.
    """
    REF = "g3"                                  # nacidos 1979-82
    G = pd.get_dummies(d.grp, prefix="g", dtype=float).drop(columns=[f"g_{REF}"])
    C = pd.get_dummies(d.nac.astype(int), prefix="c", drop_first=True).astype(float)
    E = pd.get_dummies(d.p19.astype(int), prefix="e", drop_first=True).astype(float)
    piezas = [pd.DataFrame({"r_ori": d.r_ori.values}, index=d.index),
              G.mul(d.Dm, axis=0).add_prefix("d_"),
              G.mul(d.r_ori * d.Dm, axis=0).add_prefix("ev_"),
              C, E, C.mul(d.r_ori, axis=0).add_prefix("rc_"),
              E.mul(d.r_ori, axis=0).add_prefix("ri_")]
    for c in controles:
        piezas.append(pd.DataFrame({f"x_{c}": d[c].values,
                                    f"xr_{c}": (d[c] * d.r_ori).values}, index=d.index))
    X = sm.add_constant(pd.concat(piezas, axis=1))
    m = sm.WLS(d.r_des, X, weights=d.factor).fit(cov_type="cluster",
                                                 cov_kwds={"groups": d[cl]})
    k = d.Dm.std()
    etq = {f"g{i}": e for i, e in enumerate(
        ["<=1970","1971-74","1975-78","1979-82","1983-86","1987-90","1991-94","1995-98"])}
    previos = [g for g in etq if g != REF and (d.frac[d.grp == g] == 0).all()]
    print(f"\n  {'grupo':>9} {'b':>9} {'ee':>8} {'t':>7}")
    for g, e in etq.items():
        if g == REF:
            print(f"  {e:>9} {0:>9.3f} {0:>8.3f} {'—':>7}  (referencia)")
            continue
        b, se = m.params[f"ev_g_{g}"] * k, m.bse[f"ev_g_{g}"] * k
        print(f"  {e:>9} {b:>9.3f} {se:>8.3f} {b/se:>7.2f}"
              f"{'  previo' if g in previos else '  expuesto'}")
    ft = m.f_test([f"ev_g_{g}=0" for g in previos])
    print(f"\n  Prueba conjunta de tendencias previas municipales: "
          f"F={float(ft.fvalue):.2f}  p={float(ft.pvalue):.3f}")
    return float(ft.pvalue)
