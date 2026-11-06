# -*- coding: utf-8 -*-
"""
limpiar_math.py — sustituye el LaTeX del manuscrito por álgebra legible
=======================================================================
Word no renderiza LaTeX, y convertir a OMML para cuatro ecuaciones no vale la
complejidad. Se reescriben como texto plano inequívoco: los nombres de las
variables se escriben completos y los subíndices se marcan con paréntesis, de
modo que la especificación se lee igual de bien sin notación matemática.

Reemplazos explícitos, no expresiones regulares generales: si aparece un
patrón nuevo el script avisa en lugar de dejarlo pasar.
"""
import sys as _s, pathlib as _pl; _s.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "funciones"))
import rutas as _r  # equivalente a here::here(); ver scripts/funciones/rutas.py
import re
import sys

RUTA = _r.MAN_EN + "/manuscript.md"

BLOQUES = [
    # ----- definición de phi
    (r"$$\varphi(c) = \frac{\left|\{\, y \in [c+10,\, c+18] : y \ge 2007 \,\}\right|}{9},$$",
     "[EQ]φ(c)  =  #{ y ∈ [c+10, c+18] : y ≥ 2007 }  ⁄  9[/EQ]"),
    # ----- dosis
    (r"$$D_{ec} = I_e \times \varphi(c).$$",
     "[EQ]D(e,c)  =  I(e)  ×  φ(c)[/EQ]"),
    # ----- especificación principal
    (r"""$$r^{\text{des}}_{i} = \beta_1 r^{\text{ori}}_{i} + \beta_2 D_{ec} + \beta_3 \left(r^{\text{ori}}_{i} \times D_{ec}\right) + \alpha_e + \gamma_c + \left(\alpha_e \times r^{\text{ori}}_{i}\right) + \left(\gamma_c \times r^{\text{ori}}_{i}\right) + \varepsilon_i ,$$""",
     "[EQ]rank_des(i)  =  β₁·rank_ori(i)  +  β₂·D(e,c)  +  "
     "β₃·[rank_ori(i) × D(e,c)][/EQ]"
     "[EQ]              +  α(e)  +  γ(c)  +  [α(e) × rank_ori(i)]  +  "
     "[γ(c) × rank_ori(i)]  +  ε(i)[/EQ]"),
    # ----- reescritura
    (r"""$$r^{\text{des}}_{i} = \left(\beta_1 + \beta_3 D_{ec}\right) r^{\text{ori}}_{i} + \cdots$$""",
     "[EQ]rank_des(i)  =  [ β₁  +  β₃·D(e,c) ] · rank_ori(i)  +  ⋯[/EQ]"),
]

EN_LINEA = [
    (r"$r^{\text{des}} = \beta_0 + \beta_1 r^{\text{ori}} + \varepsilon$",
     "rank_des = β₀ + β₁·rank_ori + ε"),
    (r"$\beta_1$", "β₁"),
    (r"$\beta_3$", "β₃"),
    (r"$|\beta_3|$", "|β₃|"),
    (r"$\alpha_e$", "α(e)"),
    (r"$\gamma_c$", "γ(c)"),
    (r"$I_e$", "I(e)"),
    (r"$\varphi(c)=0$", "φ(c) = 0"),
    (r"$\varphi(c)=1$", "φ(c) = 1"),
    (r"$\varphi(c)$", "φ(c)"),
    (r"$\varphi$", "φ"),
    (r"$k=2,\dots,8$", "k = 2, …, 8"),
    (r"$k=1$", "k = 1"),
    (r"$k=2$", "k = 2"),
    (r"$k=3$", "k = 3"),
    (r"$k=4$", "k = 4"),
    (r"$k$", "k"),
    (r"$c$", "c"),
    (r"$t$", "t"),
    (r"$2.8$", "2.8"),
    (r"$2.8 = 1.96 + 0.84$", "2.8 = 1.96 + 0.84"),
    (r"$R^2$", "R²"),
    (r"$(\,\text{cumsum}(w) - \tfrac{1}{2}w\,)/\sum w$",
     "[cumsum(w) − ½·w] ⁄ Σw"),
    (r"$e$", "e"),
    (r"$p$", "p"),
]

t = open(RUTA, encoding="utf-8").read()
hechos = []
for viejo, nuevo in BLOQUES + EN_LINEA:
    if viejo in t:
        t = t.replace(viejo, nuevo)
        hechos.append(viejo[:46].replace("\n", " "))

resto = re.findall(r"\$[^$\n]{0,120}\$|\$\$", t)
if resto:
    print("AVISO: queda notación sin convertir:", file=sys.stderr)
    for r in sorted(set(resto)):
        print("   ", r, file=sys.stderr)
    sys.exit(1)

open(RUTA, "w", encoding="utf-8").write(t)
print(f"Convertidos {len(hechos)} patrones. No queda LaTeX en el manuscrito.")
