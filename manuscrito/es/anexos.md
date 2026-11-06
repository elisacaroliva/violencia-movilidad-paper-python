## Declaraciones

**Conflicto de interés.** Los autores declaran no tener conflictos de interés.

**Financiamiento.** Esta investigación no recibió financiamiento específico de agencias públicas, comerciales o sin fines de lucro. Se realizó como parte de la Concentración en Economía Aplicada y Ciencia de Datos para el Bien Público del Tecnológico de Monterrey.

**Aprobación ética.** No aplica. El estudio usa datos secundarios públicos y desidentificados, y no implicó contacto con personas.

**Contribución de los autores.** Todos los autores contribuyeron a la concepción del estudio, la construcción de los datos, el análisis empírico y la redacción, y todos leyeron y aprobaron la versión final.

**Disponibilidad de datos.** El estudio usa cuatro fuentes secundarias públicas. Los microdatos de la ESRU-EMOVI 2023 los distribuye el Centro de Estudios Espinosa Yglesias en https://ceey.org.mx. Las series delictivas las publica el Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública en https://www.gob.mx/sesnsp, en los archivos estatal y municipal de la metodología anterior de 1997 a 2017. Los microdatos de defunciones registradas y el producto interno bruto por entidad los publica el INEGI en https://www.inegi.org.mx. Las proyecciones de población municipal las publica el Consejo Nacional de Población en https://www.gob.mx/conapo. Los autores no generaron datos primarios.

**Disponibilidad de código.** Todo el código que genera los cuadros y figuras de este manuscrito, junto con los archivos derivados y un README con versiones de software y la semilla aleatoria fija, está depositado en [URL DEL REPOSITORIO]. El análisis es reproducible desde las fuentes públicas mencionadas; la semilla es 20261102 y se fija en cada script que extrae números aleatorios.

**Uso de inteligencia artificial generativa.** Véase la declaración del anexo E, preparada conforme a la política de Springer Nature sobre modelos grandes de lenguaje.

---

# Anexo A. Ficha editorial de la revista

## A.1 Identificación

| Elemento | Dato |
|---|---|
| Revista | *Empirical Economics* |
| Editorial | Springer-Verlag GmbH Germany, parte de Springer Nature |
| ISSN | 0377-7332 (impreso); 1435-8921 (electrónico) |
| Indexación | Scopus; Social Science Citation Index; EconLit; RePEc; ABS Academic Journal Quality Guide; lista del Australian Business Deans Council; Dimensions; EBSCO; ProQuest; Norwegian Register, entre otros |
| Cuartil SJR | **Q2 en Economics and Econometrics** (SJR 0.76, 2024). También Q2 en Statistics and Probability; Q1 en las categorías misceláneas de Social Sciences y de Mathematics |
| Factor de impacto | 1.9 (2025); a cinco años 3.1 (2025) |
| Índice h | 71 |
| Mediana de tiempo a primera decisión | 61 días |
| Guía para autores | https://link.springer.com/journal/181/submission-guidelines |

El cuartil reportado es el relevante para este manuscrito. *Empirical Economics* alcanza Q1 sólo en dos categorías misceláneas que agregan a través de disciplinas; en su propia categoría de campo, Economics and Econometrics, es Q2.

## A.2 Ajuste temático

*Empirical Economics* publica trabajo aplicado de cualquier campo de la economía cuya contribución sea empírica, y su propósito declarado es confrontar la teoría económica con los datos observados mediante métodos econométricos o estadísticos. Nuestro manuscrito es un ejercicio de identificación sobre datos de encuesta y administrativos mexicanos cuyo objeto es un efecto de tratamiento —el cambio en la pendiente rango-rango intergeneracional causado por la exposición a la violencia del crimen organizado durante la adolescencia— y cuyo resultado principal es una cota sobre ese efecto y no una estimación puntual. La lista de temas de la revista nombra explícitamente la estimación de efectos de tratamiento y la evaluación de políticas, y la revista declara que acepta artículos que confirmen o contradigan hallazgos establecidos. Ese es un ajuste inusualmente bueno para un artículo cuya afirmación central es que una comparación cruda, ampliamente disponible en los datos, atribuye a la violencia una tendencia que la antecede, y cuyo resultado es un nulo caracterizado con precisión. Una revista que no valorara la replicación y las cotas sería el destino equivocado para este trabajo aunque su cobertura temática fuera más cercana.

El ajuste por tema es igualmente directo: la revista publica sobre trabajo, educación, desarrollo y delito, y las tres literaturas con las que dialoga este artículo —violencia y capital humano, movilidad intergeneracional, y la econometría de diferencias en diferencias con pocos conglomerados— están dentro de su cobertura regular.

## A.3 Evidencia de que la revista acepta métodos de ciencia de datos

**Del Aims and Scope.** La revista se describe publicando artículos que aplican "advanced econometric or statistical methods" y que usan "econometric or statistical methods to fill the gap between economic theory and observed data", con temas que incluyen "treatment effect estimation", "policy evaluation", "simulation" y "forecasting", y trabajo sobre "econometric methods and measurement".

Registramos con honestidad que el Aims and Scope **no contiene los términos *machine learning*, *data science* ni *computational methods***. La aceptación de tales métodos se establece aquí a partir de artículos publicados, que es la segunda de las dos vías que la asignación permite. Consideramos y descartamos dos alternativas por esta razón: *The Journal of Economic Inequality* y *Research in Social Stratification and Mobility* son las dos más cercanas en tema y las dos publican artículos con aprendizaje automático, pero son Q1; el *Journal of Computational Social Science* es Q2 y su descripción sí refiere a enfoques computacionales y a la ciencia de datos entre sus campos afines, pero su ajuste temático es más débil para un artículo que es econometría en cuatro quintas partes, y su descripción tampoco nombra el aprendizaje automático.

**Artículo de referencia 1.** Lechner, M. y Okasa, G. (2025). Random Forest estimation of the ordered choice model. *Empirical Economics*, 68(1), 1–106. https://doi.org/10.1007/s00181-024-02646-4

*Método.* El Ordered Forest, un estimador de bosque aleatorio para modelos de elección ordenada construido sobre el bosque de regresión de Breiman. Recupera probabilidades condicionales de elección diferenciando probabilidades acumuladas estimadas a partir de indicadores binarios y, a diferencia de la mayoría de los estimadores de aprendizaje automático, entrega efectos marginales e inferencia válida mediante bosques honestos con división de muestra. El desempeño se evalúa con error cuadrático medio y el ranked probability score en simulación de Monte Carlo, y con diez repeticiones de validación cruzada de diez pliegues en datos reales. Códigos JEL C14, C25, C40.

*Por qué lo usamos como modelo.* Es la demostración de la propia revista de que un estimador de aprendizaje automático es publicable ahí cuando la inferencia se maneja correctamente, y el recurso de división honesta que usa es el que señalamos en la sección 6 como la forma natural de añadir un componente supervisado a nuestro diseño.

**Artículo de referencia 2.** Caravaggio, N., Lagravinese, R. y Resce, G. (2026). The determinants of health expenditure: a machine learning approach. *Empirical Economics*, 70(2). https://doi.org/10.1007/s00181-025-02854-6

*Método.* Cuatro aprendices supervisados —Elastic-Net, bosque aleatorio, gradient boosting y regresión de vectores de soporte— comparados contra una regresión multivariada de referencia y un modelo lineal generalizado, sobre datos administrativos regionales italianos de 1996 a 2019. Los hiperparámetros se ajustan por validación cruzada de diez pliegues repetida diez veces sólo sobre la partición de entrenamiento; los resultados se promedian sobre cien particiones aleatorias 80/20 de entrenamiento y prueba; el desempeño se reporta como error porcentual absoluto medio y R²; los modelos ajustados se interpretan mediante importancia de variables estandarizada y gráficas de dependencia parcial.

*Por qué lo usamos como modelo.* Es la plantilla que seguimos para *cómo reportar* un resultado computacional en esta revista: la separación entre ajuste y evaluación, el promedio sobre particiones repetidas, y el uso de medidas de importancia y dependencia para volver sustantivamente interpretable un modelo ajustado. Nuestro ejercicio es no supervisado y por tanto reporta cantidades distintas, y la sección 4.3 dice exactamente cuáles y por qué.

## A.4 Reglas de la guía para autores que obligan a este manuscrito

| Elemento | Regla | Qué hicimos |
|---|---|---|
| Idioma | No se declara explícitamente; la revista publica en inglés y ofrece servicio de edición | El manuscrito para someter va en inglés; ésta es la versión en español para uso del equipo |
| Tipo de artículo | Artículo de investigación; dictamen simple ciego | Artículo de investigación |
| Extensión máxima | **No la especifica la revista** | Aplica el límite del curso: cuerpo por debajo de 9 000 palabras. El nuestro son 8 665 |
| Resumen | "Please provide an abstract of 150 to 250 words" | 247 palabras, dentro del rango |
| Palabras clave | "Please provide 4 to 6 keywords which can be used for indexing purposes" | 5 palabras clave |
| Códigos JEL | Obligatorios: "An appropriate number of JEL codes should be provided" | J62, D63, K42, C38, O54 |
| Estructura | Portada separada; resumen, palabras clave, JEL; texto con sistema decimal de encabezados de "no more than three levels"; Declaraciones antes de las referencias; referencias; cuadros y figuras | Cumplido; los encabezados llegan a dos niveles |
| Citas | Autor-año en el texto, p. ej. "(Thompson 1990)"; lista alfabetizada por apellido del primer autor; DOI completo donde exista; nombres de revista abreviados según ISSN LTWA | Cumplido, con abreviaturas LTWA y DOI |
| Cuadros | Numeración arábiga, citados en orden consecutivo; pie que explica los componentes; notas con letras minúsculas voladas o asteriscos para significancia; construidos con la función de tabla de Word | Cumplido |
| Figuras | Numeración arábiga; archivos nombrados "Fig1"; EPS para vectoriales y TIFF para medios tonos, se aceptan archivos de MS Office; resolución mínima 1200 ppp arte lineal, 300 medios tonos, 600 arte combinado; líneas de al menos 0.1 mm; tipografía Helvetica o Arial de 8 a 12 pt; ancho 84 mm o 174 mm, alto máximo 234 mm; pies en el archivo de texto empezando con "Fig." en negritas y sin puntuación final; legibles en blanco y negro; contraste de al menos 4.5:1 | Cumplido. Las figuras de la versión en inglés van a 174 mm y 600 ppp en Liberation Sans, métricamente compatible con Arial, con marcadores y trazos distintos para que ninguna serie dependa sólo del color |
| Datos y código | Declaración de disponibilidad de datos obligatoria en todo artículo original; depósito en repositorio público fuertemente recomendado y obligatorio para algunos tipos de datos; sección separada de disponibilidad de datos y código antes de las referencias; los autores deben entregar documentación o datos para verificar resultados a solicitud; el alcance de la revista añade que los autores deben entregar datos y código antes de publicar | Declaraciones incluidas; código y datos derivados en el anexo D, para depositar en el repositorio nombrado en la declaración |
| Formato de envío | "Manuscripts should be submitted in LaTeX"; también se aceptan archivos de Word | El curso pide .docx, que la revista acepta. Para un envío real el manuscrito se reharía en LaTeX |
| IA generativa | Los modelos grandes de lenguaje "do not currently satisfy our authorship criteria"; su uso debe documentarse en la sección de métodos o equivalente; la edición de estilo asistida por IA no requiere declararse; los autores humanos siguen siendo responsables del texto final | Anexo E, referido desde las Declaraciones |

---

# Anexo B. Matriz de atención a comentarios del Entregable 1

La primera columna resume el contenido de cada comentario; la redacción es nuestra y no literal. Cuando un comentario no se atendió, la tercera columna da la razón en lugar de una ubicación.

| Comentario recibido | Cambio realizado | Sección |
|---|---|---|
| 1. Los títulos de cuadros y gráficas no describen lo que se muestra y faltan unidades y fuente. | Atendido. Cada cuadro y cada figura llevan título descriptivo, unidades explícitas en los encabezados de columna y nota al pie con fuente y periodo. | Cuadros 1 a 9 y Figuras 1 a 4 |
| 2. No se usa el diseño muestral complejo de la encuesta: unidades primarias de muestreo, estratos y factores de expansión. | Atendido. Se documenta el diseño y los rangos se calculan dentro de cohorte con factores de expansión. Se explica por qué los errores se agrupan por entidad y no por unidad primaria: la variación del tratamiento es estatal, de modo que la entidad es el nivel al que se asigna la dosis. | 3.4 |
| 3. Excluir a quienes migraron entre entidades sesga la muestra, porque la violencia misma induce migración. | Atendido. Se añade una especificación que los incluye, reasignando la dosis a la entidad de origen. El coeficiente pasa de 0.0161 a un valor estadísticamente indistinguible, y la migración se analiza además como desenlace propio. | 3.5, Cuadro 2 renglón 3 y 5.7 |
| 4. Se comparan pendientes entre grupos sin reportar el error estándar de la diferencia, así que no se sabe si las diferencias existen. | Atendido. Toda diferencia de pendientes se reporta con su error estándar, y el estudio de eventos acompaña los coeficientes con la prueba conjunta (F = 0.42, p = 0.79). | 5.3 y Figura 3 |
| 5. El número de entidades tratadas es inconsistente a lo largo del texto: aparece 31 y 30. | Atendido. Se reconcilia en 31 entidades tratadas, y las barras rayadas de la Figura 2 identifican las que no aportan observaciones a la muestra de estimación, que era el origen de la discrepancia. | 3.5 y Figura 2 |
| 6. La serie del SESNSP cuenta carpetas de investigación y no víctimas, de modo que la unidad de registro no es la que el argumento necesita. | Atendido parcialmente. Se reconoce explícitamente y se reconstruye el índice completo con defunciones por homicidio del INEGI, que sí cuenta víctimas; el Cuadro 9 compara las tres definiciones. No se adopta como medida principal porque la serie municipal del INEGI exige rehacer el diseño intraestatal, que queda pendiente. | 3.2, 5.10, Cuadro 9 y Anexo F.4 |
| 7. El periodo previo a 1997 no está observado, y la serie del SESNSP no permite saber si el repunte fue realmente un repunte. | Atendido. Se construye la serie de homicidio 1990-2020 con microdatos de defunciones generales del INEGI. El resultado va en contra del diseño y se reporta así: la tasa nacional de 1990 a 1997 fue de 13.6 por 100 000 contra 19.7 durante el repunte, 38.9 % de la muestra tuvo ventana formativa traslapada con ese periodo, y una dosis placebo sobre la violencia de 1990-97 da +0.0197 (0.0259), mayor que la dosis del repunte. | 5.10, Cuadro 9 y Anexo F.5 |
| 8. Los registros delictivos están afectados por subregistro y el trabajo no lo cuantifica. | Atendido. Se cuantifica contra las estadísticas vitales: correlación de 0.903 sobre 672 celdas de entidad por año, brecha agregada de 1.9 %, y brecha por entidad que va de −54 % en Tlaxcala a +34 % en Chihuahua con reversión de signo en algunas. Se discute como error de medición no clásico en el tratamiento, con sus dos consecuencias. | 3.2 y Anexo F.4 |
| 9. Conservar a quienes corresiden con sus padres contamina la medida de destino, porque los activos observados son los del hogar de los padres. | Atendido parcialmente. Se reporta la estimación que los excluye y el coeficiente no cambia de manera apreciable. Se mantienen en la especificación principal, y la razón se da en el texto: excluirlos elimina de manera desproporcionada a los más jóvenes y a los de origen más bajo, lo que introduce una selección peor que el problema que corrige. | Cuadro 2 renglón 2 y 5.7 |
| 10. Las cifras de movilidad no se reconcilian con los indicadores publicados por el CEEY. | No atendido. Nuestra pendiente rango-rango de 0.650 se estima sobre activos del hogar y una muestra de 15 558 casos con restricciones propias, mientras que los indicadores del CEEY usan matrices de transición por quintiles sobre la muestra completa; la reconciliación exige replicar su definición de origen y destino y no se hizo. Queda como pendiente declarado. | Pendiente |

---

# Anexo C. Carta de presentación

Estimados editores de *Empirical Economics*:

Sometemos a su consideración el manuscrito "Organized-crime violence and intergenerational persistence: evidence and bounds from Mexico".

El artículo pregunta si la exposición al repunte de homicidios posterior a 2007 en México, durante la ventana formativa de los 10 a los 18 años, elevó la persistencia intergeneracional del estatus socioeconómico. La literatura existente establece que esa violencia redujo la escolaridad y los puntajes en pruebas. Si cambió el *gradiente* que liga la posición de una persona con la de sus padres es una pregunta distinta, y sólo se ha abordado una vez, para Estados Unidos. Importa para la política porque las dos márgenes piden remedios distintos: una pérdida uniforme de escolaridad llama a inversión compensatoria en las cohortes afectadas, mientras que un gradiente más empinado llama a focalizar el fondo de la distribución de origen.

Nuestra respuesta es una cota y no un efecto, y creemos que la cota es la contribución. Con la ESRU-EMOVI 2023 y registros delictivos estatales de 1997 a 2017, estimamos una triple diferencia que exige que el efecto aparezca entre entidades y entre cohortes de manera simultánea, y que permite que la persistencia misma difiera por entidad y por cohorte. El cambio estimado en la pendiente rango-rango es 0.016 con error estándar de 0.026 por desviación estándar de intensidad de violencia estatal, contra una pendiente base de 0.650; una prueba de permutación sobre 2 000 reasignaciones da p = 0.62; la prueba conjunta de tendencias previas no se rechaza. Reexpresado en las unidades del precedente de Sharkey y Torrats-Espinosa (2017), el efecto sobre el rango esperado de destino de quien viene del percentil 25 es −0.81 puntos contra su −1.57: mismo signo, cerca de la mitad del tamaño, con un intervalo que contiene su valor.

Cuatro rasgos pueden interesar más allá del resultado principal. Mostramos que la comparación entre cohortes que motiva la hipótesis atribuye a la violencia una subida de la persistencia que ya estaba en marcha entre cohortes cuya adolescencia terminó en los noventa. Documentamos que medir la violencia municipal con conteos de homicidio en lugar de tasas produce un coeficiente negativo espurio y aparentemente significativo. Usamos agrupamiento no supervisado de las trayectorias de violencia como diagnóstico de la propia medida de exposición, y encuentra once entidades cuyo repunte llegó una década después de la fecha que la dosis les asigna. Y reconstruimos el índice completo sobre estadísticas vitales de 1990 a 2020, lo que revela que el periodo previo al repunte, que el diseño trata como no tratado, cargaba una tasa de homicidio no muy inferior a la del repunte.

Creemos que el manuscrito encaja en *Empirical Economics* por tres razones: su contribución es una estrategia de identificación y una cota y no una afirmación teórica; cae de lleno en la cobertura declarada de estimación de efectos de tratamiento y evaluación de políticas; y el compromiso de la revista con la reproducibilidad corresponde a un artículo cuyo valor depende de que el lector pueda verificar que los controles hacen lo que decimos. Todo el código, los datos derivados y la semilla aleatoria fija están disponibles para depósito.

El manuscrito es original, no está bajo consideración en otra parte, y todos los autores aprobaron el envío. Declaramos no tener conflictos de interés. El uso de inteligencia artificial generativa se declara en un anexo conforme a la política de Springer Nature.

Agradecemos su tiempo y consideración.

Atentamente,

[NOMBRES DE LOS AUTORES]
En representación de los autores
Tecnológico de Monterrey

---

# Anexo E. Declaración sobre el uso de inteligencia artificial generativa

Esta declaración se hace conforme a la política de Springer Nature sobre modelos grandes de lenguaje, que establece que tales modelos no satisfacen los criterios de autoría, que su uso debe documentarse, y que los autores humanos siguen siendo responsables del texto final.

**Ningún sistema de inteligencia artificial figura como autor de este manuscrito.** Los autores asumen plena responsabilidad por su contenido, incluido cada número reportado y cada afirmación hecha.

**Dónde se usó inteligencia artificial generativa.** Se usó un asistente basado en un modelo grande de lenguaje de las siguientes maneras:

1. *Desarrollo y depuración de código.* Los scripts de Python que construyen la muestra, estiman los modelos, corren las pruebas de permutación y el agrupamiento, procesan los microdatos de mortalidad y generan los cuadros y figuras se escribieron con asistencia de un modelo grande de lenguaje. Todo el código se incluye en el anexo D y puede inspeccionarse y ejecutarse de manera independiente. Los autores verificaron las salidas volviendo a correr el análisis desde los archivos fuente públicos.

2. *Diagnóstico de errores en nuestro propio análisis previo.* El asistente se usó para localizar y corregir errores sustantivos de versiones anteriores de este trabajo: una truncación de la escala de escolaridad que descartaba las categorías más altas, la omisión del bloque de nacimiento por rango de origen en el estudio de eventos, una mala codificación del origen rural, y un error en la lectura del año de ocurrencia de los microdatos de mortalidad, donde el año viene en dos dígitos hasta 1998 y en cuatro desde 1999. Cada corrección cambió resultados reportados, y los resultados corregidos son los que aquí aparecen. Los errores y sus consecuencias se describen en el manuscrito y en el README del paquete de replicación en lugar de ocultarse.

3. *Redacción y edición de prosa.* El asistente se usó para redactar y revisar secciones del texto. Los autores revisaron, editaron y aprobaron la totalidad, y confirman que el texto final refleja su propio análisis y sus conclusiones.

4. *Apoyo en la búsqueda de literatura.* El asistente se usó para localizar referencias candidatas. Toda referencia de la lista fue verificada después por los autores contra el registro de la editorial o una base bibliográfica equivalente; los datos bibliográficos, incluidos volumen, número, páginas y DOI, se comprobaron uno por uno.

**Dónde no se usó.** Ningún texto, cuadro, figura o resultado numérico de este manuscrito fue generado por un modelo de lenguaje sin verificación contra los datos. Ninguna figura o imagen fue generada por un modelo generativo; todas las figuras las produce el código del anexo D a partir de los datos fuente. Ninguna referencia se incluyó sobre la base de la afirmación de un modelo.

**Sobre la frontera con la edición de estilo.** La política de Springer Nature exime de declaración a la edición asistida por IA, entendida como mejoras de legibilidad, gramática, ortografía, puntuación y tono. Hemos declarado nuestro uso de manera completa en lugar de apoyarnos en esa exención, porque nuestro uso fue más allá de la edición de estilo.

---

# Anexo F. Detalle metodológico complementario

## F.1 Construcción de los rasgos del agrupamiento y elección de algoritmos

**Construcción de rasgos.** Para cada una de las 32 entidades tomamos los 21 valores anuales del índice de violencia y los estandarizamos dentro de la entidad, restando su propia media y dividiendo entre su propia desviación estándar. Eso separa la *forma* de una trayectoria de su *nivel*: dos entidades con el mismo perfil temporal quedan juntas aunque una sea mucho más violenta que la otra. La matriz de rasgos resultante es de 32 por 21.

**Algoritmos.** Aplicamos tres que difieren en lo que suponen. La aglomeración jerárquica de Ward (Ward 1963) produce un dendrograma completo y no exige fijar el número de conglomerados de antemano. k-medias es particional y sí lo exige, lo que vuelve útil el contraste entre ambos. DBSCAN (Ester et al. 1996) es basado en densidad y puede negarse a asignar puntos, etiquetándolos como ruido; lo aplicamos tanto a entidades como a municipios precisamente para mostrar en qué régimen de tamaño de muestra es informativo.

**Selección del hiperparámetro.** El número de conglomerados es el hiperparámetro. Lo elegimos por silueta media (Rousseeuw 1987), calculada para k = 2 hasta 8 tanto en Ward como en k-medias. Para DBSCAN los hiperparámetros son el radio de vecindad y el mínimo de puntos; reportamos resultados sobre una rejilla de radios en lugar de elegir uno, porque a nivel estatal ningún radio produce una partición informativa.

## F.2 Criterios internos y su discrepancia

Frente al modelo de referencia de k = 1, la partición de tres conglomerados explica 38.8 % de la suma de cuadrados total en la forma de las trayectorias. Dos criterios internos más discrepan con la silueta y la discrepancia vale la pena verla: el índice de Calinski-Harabasz se maximiza en k = 2, con 11.46 contra 9.18 en k = 3, y el de Davies-Bouldin sigue mejorando conforme k sube. Con 32 observaciones ninguno es decisivo. Lo que vuelve utilizable el resultado es que la conclusión no depende de cuál se siga: el conglomerado de primera ola de quince entidades es idéntico en k = 2, 3 y 4, y las once entidades de pico tardío permanecen juntas en un solo grupo en los tres casos.

Los tres criterios se reportan para cada k en el panel A del cuadro 4. Discrepan porque penalizan cosas distintas: la silueta premia la separación relativa a la cohesión interna para cada punto, Calinski-Harabasz es una razón de varianzas que penaliza conglomerados adicionales por sus grados de libertad, y Davies-Bouldin promedia una similitud de peor caso entre conglomerados y por tanto tiende a seguir mejorando conforme los grupos se encogen. Con 32 observaciones ninguno es decisivo, que es por qué la invariancia de la partición sustantiva entre k = 2 y 4 pesa más que cualquier criterio individual.

## F.3 El estimador de quiebre estructural usado para refechar la dosis

Para cada unidad ajustamos un cambio de nivel, y(t) = mu1 + delta × 1[t ≥ tau] + e(t), por mínimos cuadrados ordinarios sobre años de quiebre candidatos tau de 2001 a 2015, y elegimos el tau que minimiza la suma de cuadrados residual. La rejilla deja al menos cuatro años de cada lado para que el quiebre esté identificado. Para la versión por entidad exigimos que el salto estimado sea positivo, porque un salto negativo fecha una caída y no un repunte; las seis entidades cuyo mejor quiebre es una caída toman el de su conglomerado.

Los dos componentes de la dosis se redefinen de manera coherente: el tiempo viene de la serie estandarizada, porque la forma es lo que fecha un repunte, y la intensidad se recalcula como la media del índice *sin estandarizar* sobre la ventana posterior al quiebre de cada entidad, porque el nivel es lo que mide cuánta violencia hubo. Usar la serie estandarizada para las dos cosas borraría precisamente las diferencias de nivel entre entidades que la dosis necesita.

## F.4 Error de medición en el índice de exposición

Dos consecuencias se siguen y las dos juegan en nuestra contra. La serie mide delito registrado y no delito, aunque para el homicidio doloso la brecha es mucho menor que para otros delitos, que es una razón por la que el índice se ancla en él. Más importante para la identificación, la serie del SESNSP y el conteo de defunciones por homicidio de las estadísticas vitales del INEGI discrepan, con una correlación de 0.903 sobre 672 celdas de entidad por año, coincidencia dentro de 2 % en el agregado, y una brecha por entidad que va de −54 % en Tlaxcala a +34 % en Chihuahua, con reversión de signo en algunas a lo largo del periodo. Eso es error de medición no clásico en el tratamiento.

Si la brecha entre delito registrado y delito real fuera una proporción constante dentro de cada entidad, la absorberían los efectos fijos de entidad y la estandarización intraestatal, y sólo importaría la parte que varía en el tiempo. Las reversiones de signo indican que la brecha no es constante, así que parte sobrevive. Y como la dosis multiplica la intensidad estatal por una fracción de cohorte medida sin error, el error clásico en el componente de intensidad atenúa el coeficiente de interacción hacia cero de la manera estándar, lo que vuelve conservadora la cota reportada en el caso clásico pero no en el no clásico.

## F.5 El índice de exposición de estadísticas vitales

El índice de la sección 5.10 se construye con los microdatos de defunciones generales del INEGI de 1990 a 2020, un archivo por año. Un registro es homicidio cuando PRESUNTO vale 2, que es la clasificación de la propia INEGI de la presunta manera de muerte y es consistente a través del cambio de CIE-9 a CIE-10 en 1998; se verificó contra los códigos de causa, E960 a E969 en la clasificación anterior y X85 a Y09 en la posterior. Las defunciones se agregan por **año de ocurrencia** y no de registro, recorriendo los treinta y un archivos, porque una muerte ocurrida en diciembre puede registrarse al año siguiente y aparecer en el archivo del año siguiente. Dos detalles de codificación importan: el año de ocurrencia es una cadena de dos dígitos hasta 1998 y de cuatro desde 1999, con 99 y 9999 respectivamente como código de año ignorado, y los registros con año desconocido se descartan. El denominador es la población a mitad de año de CONAPO por entidad y municipio, que corre desde 1990.

La serie nacional resultante es de 11 502 defunciones en 1990, cayendo a lo largo de los noventa y los dos mil hasta un mínimo de 8 866 en 2007, luego 14 273 en 2008, 26 131 en 2010, 27 480 en 2011, un valle de 19 682 en 2014 y 31 818 en 2017. La cifra de 2007 coincide casi exactamente con el conteo publicado por el INEGI de 8 867. Los primeros años quedan ligeramente por debajo de los totales publicados por año de registro, porque se excluyen los registros con año de ocurrencia desconocido y porque las defunciones ocurridas antes de 1990 y registradas después no pueden recuperarse; como la comparación de 1990 a 1997 que usa la sección 5.10 es relativa entre entidades, un subconteo proporcional no la afecta.

El panel municipal se construye igual y corre desde 1990, contra 2011 de la serie municipal del SESNSP. Aplicarlo al diseño intraestatal de la sección 5.6 extendería su periodo previo en veintiún años y es el uso más prometedor que queda de estos datos; no lo hemos hecho aquí.

## F.6 Dos confusores que no sobreviven a la inspección

Primero lo que **no** es una amenaza, porque una versión anterior de este artículo lo reportaba como tal. La pandemia de COVID-19, la terminación del programa PROSPERA en 2019 y el fin de Escuelas de Tiempo Completo en 2022 se plantean a veces como confusores para trabajos sobre estas cohortes. No lo son aquí, por calendario: el encuestado de mayor edad de la muestra nació en 1959 y el más joven en 1998, así que la última ventana formativa de los datos cierra en **2016**, y ni un solo encuestado —cero de 15 558— tenía una ventana aún abierta cuando llegó cualquiera de esos tres choques. La persona más joven de la muestra tenía 22 años cuando empezó la pandemia. Esos eventos pueden afectar los activos de destino que medimos en 2023, pero llegan simultáneamente para cada cohorte y por tanto quedan absorbidos en lugar de confundir.

El choque con el calendario correcto es la recesión de 2008-2009, que cayó dentro de la ventana de exposición y de la que suele suponerse que golpeó más fuerte donde la violencia subió. Lo probamos en lugar de suponerlo. Con el producto interno bruto estatal del INEGI a precios constantes, la contracción entre 2007 y 2009 promedia 4.0 % con desviación estándar de 6.4 puntos y la encabezan Coahuila, Campeche y Baja California; su correlación con la intensidad de violencia entre las 32 entidades es **−0.09**, de modo que la premisa del confusor no se sostiene. Construyendo una dosis de recesión exactamente paralela a la de violencia —la contracción de la entidad multiplicada por la fracción de la ventana formativa que cae en 2008-2009— y agregándola, junto con su interacción con el rango de origen y finalmente un conjunto saturado de términos de contracción por cohorte por rango, las cuatro especificaciones dan 0.0161 sin control de recesión, 0.0161 agregando la dosis, 0.0160 agregando su interacción y 0.0159 en la versión saturada, con el error estándar moviéndose de 0.0255 a 0.0263.

Una versión anterior de este artículo listaba el primer grupo como la amenaza que no podía responder, y así la nombró en presentaciones. La aritmética que la descarta es elemental y debimos hacerla antes: quien nació en 1998, el más joven de la muestra, cumplió 18 años en 2016. Registramos el error aquí porque el mismo descuido es fácil en cualquier trabajo sobre estas cohortes, donde la pandemia es una preocupación natural y la ventana formativa no es la ventana en que se miden los desenlaces.
