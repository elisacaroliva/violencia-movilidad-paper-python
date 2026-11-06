## Statements and Declarations

**Competing interests.** The authors declare that they have no competing interests.

**Funding.** This research received no specific grant from any funding agency in the public, commercial or not-for-profit sectors. It was conducted as part of the Concentración en Economía Aplicada y Ciencia de Datos para el Bien Público at Tecnológico de Monterrey.

**Ethics approval.** Not applicable. The study uses publicly available, de-identified secondary data and involved no contact with human subjects.

**Author contributions.** All authors contributed to the conception of the study, the construction of the data, the empirical analysis and the writing of the manuscript, and all authors read and approved the final version.

**Data availability.** The study uses three public secondary sources. The ESRU-EMOVI 2023 microdata are distributed by the Centro de Estudios Espinosa Yglesias and are available on request from the CEEY at https://ceey.org.mx. The crime series are published by the Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública at https://www.gob.mx/sesnsp, in the state and municipal files of the earlier methodology covering 1997–2017. The municipal population projections are published by the Consejo Nacional de Población at https://www.gob.mx/conapo. The authors generated no new primary data.

**Code availability.** All code that generates the tables and figures in this manuscript, together with the derived data files and a README specifying software versions and the fixed random seed, is deposited at [REPOSITORY URL]. The analysis is fully reproducible from the public sources named above; the seed is 20261102 and is set in every script that draws random numbers.

**Use of generative artificial intelligence.** See the declaration in Appendix E, prepared in accordance with the Springer Nature policy on large language models.

---

# Appendix A. Journal fact sheet

## A.1 Identification

| Item | Detail |
|---|---|
| Journal | *Empirical Economics* |
| Publisher | Springer-Verlag GmbH Germany, part of Springer Nature |
| ISSN | 0377-7332 (print); 1435-8921 (electronic) |
| Indexing | Scopus; Social Science Citation Index; EconLit; RePEc; ABS Academic Journal Quality Guide; Australian Business Deans Council list; Dimensions; EBSCO; ProQuest; Norwegian Register; among others |
| SJR quartile | **Q2 in Economics and Econometrics** (SJR 0.76, 2024). Also Q2 in Statistics and Probability; Q1 in the miscellaneous categories of Social Sciences and of Mathematics |
| Journal Impact Factor | 1.9 (2025); five-year 3.1 (2025) |
| h-index | 71 |
| Median time to first decision | 61 days |
| Author guidelines | https://link.springer.com/journal/181/submission-guidelines |

The quartile reported above is the one relevant to this manuscript. *Empirical Economics* reaches Q1 only in two miscellaneous categories that aggregate across disciplines; in its own field category, Economics and Econometrics, it is Q2.

## A.2 Thematic fit

*Empirical Economics* publishes applied work in any field of economics whose contribution is empirical, and its stated purpose is to confront economic theory with observed data using econometric or statistical methods. Our manuscript is an identification exercise on Mexican survey and administrative data whose object is a treatment effect — the change in the intergenerational rank–rank slope caused by exposure to organized-crime violence during adolescence — and whose principal result is a bound on that effect rather than a point estimate. The journal's own list of topics names treatment effect estimation and policy evaluation explicitly, and the journal states that it accepts papers that confirm or contradict established findings in the literature. That is an unusually good fit for a paper whose central claim is that a crude comparison widely available in the data attributes to violence a trend that pre-dates it, and whose headline result is a precisely characterised null. A journal that did not value replication and bounds would be the wrong destination for this paper even if its topic coverage were closer.

The fit on topic is likewise direct. The journal publishes on labour, education, development and crime, and the three literatures this paper speaks to — violence and human capital, intergenerational mobility, and the econometrics of differences-in-differences with few clusters — are all within its regular coverage.

## A.3 Evidence that the journal accepts data-science methods

**From the Aims and Scope.** The journal describes itself as publishing papers that apply "advanced econometric or statistical methods" and that use "econometric or statistical methods to fill the gap between economic theory and observed data", with listed topics that include "treatment effect estimation", "policy evaluation", "simulation" and "forecasting", and work on "econometric methods and measurement".

We record honestly that the Aims and Scope **does not contain the terms *machine learning*, *data science* or *computational methods***. The journal's acceptance of such methods is therefore established here from published articles, which is the second of the two routes the assignment permits. We considered and rejected two alternatives on this ground: *The Journal of Economic Inequality* and *Research in Social Stratification and Mobility* are both closer on topic and both publish machine-learning articles, but both are Q1; the *Journal of Computational Social Science* is Q2 and its overview does refer to computational approaches and to data science among its related fields, but its thematic fit for a paper that is four-fifths econometrics is weaker, and its overview does not name machine learning either.

**Reference article 1.** Lechner, M., & Okasa, G. (2025). Random Forest estimation of the ordered choice model. *Empirical Economics*, 68(1), 1–106. https://doi.org/10.1007/s00181-024-02646-4

*Method.* The Ordered Forest, a random-forest estimator for ordered choice models built on the regression random forest of Breiman. The estimator recovers conditional choice probabilities by differencing cumulative probabilities estimated from binary indicators, and — unlike most machine-learning estimators — delivers marginal effects and valid inference, using honest forests with sample splitting. Performance is assessed by mean squared error and the ranked probability score in Monte Carlo simulation, and by ten repetitions of ten-fold cross-validation on real data. JEL codes C14, C25, C40.

*Why we use it as a model.* It is the journal's own demonstration that a machine-learning estimator is publishable there when inference is handled properly, and the honest-splitting device it uses is the one we point to in Section 6 as the natural way to add a supervised component to our design.

**Reference article 2.** Caravaggio, N., Lagravinese, R., & Resce, G. (2026). The determinants of health expenditure: a machine learning approach. *Empirical Economics*, 70(2). https://doi.org/10.1007/s00181-025-02854-6

*Method.* Four supervised learners — Elastic-Net, random forest, gradient boosting machines and support-vector regression — compared against a multivariate regression baseline and a generalised linear model, on Italian regional administrative data for 1996–2019. Hyperparameters are tuned by ten-times-repeated ten-fold cross-validation on the training split alone; results are averaged over one hundred random 80/20 train–test partitions; performance is reported as mean absolute percentage error and R²; the fitted models are interpreted through standardised variable importance and partial dependence plots.

*Why we use it as a model.* It is the template we follow for *how to report* a computational result in this journal: the separation of tuning from evaluation, the averaging over repeated partitions, and the use of importance and dependence measures to make a fitted model substantively interpretable. Our own exercise is unsupervised and therefore reports different quantities, and Section 4.3 states exactly which and why.

## A.4 Rules from the author guidelines that bind this manuscript

| Element | Rule | What we did |
|---|---|---|
| Language | Not stated explicitly; the journal publishes in English and offers English-language editing | Manuscript written in English |
| Article type | Research article; single-blind peer review | Research article |
| Maximum length | **Not specified by the journal** | Course limit applies: body under 9,000 words. Ours is 9,707 — **over by 707**, see note below |
| Abstract | "Please provide an abstract of 150 to 250 words" | 271 words — **over by 21**, see note below |
| Keywords | "Please provide 4 to 6 keywords which can be used for indexing purposes" | 5 keywords |
| JEL codes | Required: "An appropriate number of JEL codes should be provided" | J62, D63, K42, C38, O54 |
| Structure | Separate title page; abstract, keywords, JEL; main text with the decimal heading system, "no more than three levels"; Statements and Declarations before the reference list; references; tables and figures | Followed; headings go to two levels |
| Citations | Author–date in text, e.g. "(Thompson 1990)"; reference list alphabetised by first author's surname; full DOI links where available; journal names abbreviated per ISSN LTWA | Followed, with LTWA abbreviations and DOIs |
| Tables | Arabic numerals, cited in consecutive order; caption explaining the components; footnotes as superscript lowercase letters or asterisks for significance; built with Word's table function, not a spreadsheet | Followed |
| Figures | Arabic numerals; files named "Fig1"; EPS for vector and TIFF for halftone, MS Office files also accepted; minimum 1200 dpi line art, 300 dpi halftone, 600 dpi combination; lines at least 0.1 mm; lettering in Helvetica or Arial at 8–12 pt; width 84 mm or 174 mm, height at most 234 mm; captions in the text file beginning with bold "Fig." and no closing punctuation; legible in black and white; lettering contrast at least 4.5:1 | Followed. Figures are 174 mm wide at 600 dpi, set in Liberation Sans, which is metrically compatible with Arial, with distinct markers and line styles so that no series depends on colour alone |
| Data and code | Data Availability Statement required for every original research article; deposit in a public repository strongly encouraged and mandatory for some data types; a separate data and computer code availability section before the references; authors must supply documentation or data to verify results on request; the journal's scope statement adds that authors must submit data and code before publication | Statements included; code and derived data in Appendix D, to be deposited at the repository named in the Code availability statement |
| Submission format | "Manuscripts should be submitted in LaTeX"; Word files are also accepted | The course requires .docx, which the journal accepts. For an actual submission the manuscript would be reset in LaTeX |
| Generative AI | Large language models "do not currently satisfy our authorship criteria"; LLM use must be documented in the Methods section or a suitable alternative; AI-assisted copy editing for readability, grammar, spelling and punctuation need not be declared; human authors remain accountable for the final text | Appendix E, cross-referenced from the Statements and Declarations |

---

# Appendix B. Response to comments on Deliverable 1

The first column summarises each comment; the wording is ours and not verbatim. Where a comment is not acted on, the third column states the reason rather than a location.

| Comment received | Change made | Where it appears |
|---|---|---|
| 1. Table and figure titles do not describe what is shown, and units and sources are missing. | Done. Every table and figure now carries a descriptive title, explicit units in the column headers, and a footnote giving source and period. | Tables 1–9 and Figures 1–4 |
| 2. The survey's complex sample design — primary sampling units, strata and expansion factors — is not used. | Done. The design is documented and ranks are computed within cohort using expansion factors. We also state why errors are clustered by state rather than by primary sampling unit: treatment varies at the state level, so the state is the level at which the dose is assigned. | 3.4 |
| 3. Dropping inter-state migrants biases the sample, because violence itself induces migration. | Done. A specification that keeps them, assigning the dose by state of origin, is added; the coefficient moves from 0.0161 to a statistically indistinguishable value. Migration is also analysed as an outcome in its own right. | 3.5, Table 2 row 3, and 5.7 |
| 4. Slopes are compared across groups without a standard error on the difference, so it is impossible to tell whether the differences are real. | Done. Every slope difference is reported with its standard error, and the event study reports the joint test alongside the coefficients (F = 0.42, p = 0.79). | 5.3 and Figure 3 |
| 5. The number of treated states is inconsistent across the text: both 31 and 30 appear. | Done. Reconciled at 31 treated states, and the hatched bars in Figure 2 identify those contributing no observations to the estimation sample, which was the source of the discrepancy. | 3.5 and Figure 2 |
| 6. The SESNSP series counts investigation files rather than victims, so the unit of record is not the one the argument requires. | Partly done. Acknowledged explicitly, and the full index is rebuilt on INEGI homicide deaths, which do count victims; Table 9 compares the three definitions. It is not adopted as the main measure because the municipal INEGI series requires rebuilding the within-state design, which remains pending. | 3.2, 5.10, Table 9 and Appendix F.4 |
| 7. The period before 1997 is unobserved, so the SESNSP series cannot establish that the surge was in fact a surge. | Done. The 1990–2020 homicide series is built from INEGI vital-statistics microdata. The result runs against the design and is reported as such: the national rate from 1990 to 1997 was 13.6 per 100,000 against 19.7 during the surge, 38.9 % of the sample had a formative window overlapping that period, and a placebo dose on 1990–97 violence gives +0.0197 (0.0259), larger than the surge dose itself. | 5.10, Table 9 and Appendix F.5 |
| 8. Crime records are affected by under-reporting and the paper does not quantify it. | Done. Quantified against vital statistics: correlation of 0.903 over 672 state-by-year cells, aggregate gap of 1.9 %, and a state-level gap running from −54 % in Tlaxcala to +34 % in Chihuahua, with sign reversals in some states. Discussed as non-classical measurement error in the treatment, with both of its consequences. | 3.2 and Appendix F.4 |
| 9. Keeping respondents who co-reside with their parents contaminates the destination measure, since the assets observed are the parents'. | Partly done. The estimate excluding them is reported and the coefficient does not move appreciably. They are kept in the main specification, and the reason is given in the text: excluding them disproportionately removes the youngest respondents and those of lowest origin, introducing a selection worse than the problem it fixes. | Table 2 row 2 and 5.7 |
| 10. The mobility figures are not reconciled with CEEY's published indicators. | Not done. Our rank-rank slope of 0.650 is estimated on household assets over a sample of 15,558 with its own restrictions, whereas CEEY's indicators use quintile transition matrices on the full sample; reconciling them requires replicating their definitions of origin and destination, which we did not do. Declared as pending. | Pending |

---

# Appendix C. Cover letter

Dear Editors of *Empirical Economics*,

We submit for your consideration the manuscript "Organized-crime violence and intergenerational persistence: evidence and bounds from Mexico".

The paper asks whether exposure to Mexico's post-2007 homicide surge during the formative window of ages 10 to 18 raised the intergenerational persistence of socioeconomic status. The existing literature establishes that this violence reduced schooling and test scores. Whether it changed the *gradient* linking a person's position to their parents' position is a separate question, and to our knowledge it has not been addressed directly. It matters for policy because the two margins call for different remedies: a uniform loss in attainment argues for compensatory investment in the affected cohorts, whereas a steeper gradient argues for targeting the bottom of the origin distribution.

Our answer is a bound rather than an effect, and we think the bound is the paper's contribution. Using the ESRU-EMOVI 2023 retrospective mobility survey and state crime records for 1997–2017, we estimate a triple difference that requires the effect to appear across states and across birth cohorts simultaneously, and that allows persistence itself to differ both by state and by cohort. The estimated change in the rank–rank slope is 0.016 with a standard error of 0.026 per standard deviation of state violence intensity, against a base slope of 0.650; a permutation test over 2,000 reassignments of intensity across states gives p = 0.62; the joint pre-trend test is not rejected. Exploiting within-state variation across 821 municipalities tightens the bound, and we can rule out effects larger than 8 per cent of the base slope at 80 per cent power.

Three features may be of interest beyond the headline. First, we show that the cross-cohort comparison that motivates the hypothesis attributes to violence a rise in persistence that was already underway among cohorts whose adolescence ended in the 1990s; a specification that allows each state its own persistence but not each cohort reports a significant effect that the complete specification removes. Second, we document that measuring municipal violence by homicide counts rather than rates produces a spurious and apparently significant negative coefficient, because within a state the municipalities with more homicides are the urban ones; the municipal event study detects this and a population denominator corrects it. Third, we use unsupervised clustering of state violence trajectories as a diagnostic for the exposure measure itself, and it identifies eleven states whose violence peaked in 2017 rather than 2010, for which our common 2007 calendar is demonstrably mis-dated.

We believe the manuscript suits *Empirical Economics* on three grounds: its contribution is an identification strategy and a bound rather than a theoretical claim; it falls squarely within the journal's stated coverage of treatment effect estimation and policy evaluation; and the journal's commitment to reproducibility matches a paper whose value depends on the reader being able to verify that the controls do the work we say they do. All code, derived data and the fixed random seed are available for deposit.

The manuscript is original, is not under consideration elsewhere, and all authors have approved the submission. We declare no competing interests. The use of generative artificial intelligence is declared in an appendix in accordance with Springer Nature policy.

We thank you for your time and consideration.

Yours sincerely,

[AUTHOR NAMES]
On behalf of the authors
Tecnológico de Monterrey

---

# Appendix E. Declaration on the use of generative artificial intelligence

This declaration is made in accordance with the Springer Nature policy on large language models, which states that such models do not satisfy the criteria for authorship, that their use must be documented, and that the human authors remain accountable for the final text.

**No artificial intelligence system is listed as an author of this manuscript.** The authors accept full responsibility for its content, including for every number reported and every claim made.

**Where generative artificial intelligence was used.** A large language model assistant was used in the following ways during the preparation of this work:

1. *Code development and debugging.* The Python scripts that construct the sample, estimate the models, run the permutation tests and the clustering, and generate the tables and figures were written with the assistance of a large language model. All code is included in Appendix D and can be inspected and executed independently. The authors verified the outputs by re-running the analysis from the public source files.

2. *Diagnosis of errors in our own earlier analysis.* The assistant was used to locate and correct three substantive errors in earlier versions of this work: a truncation of the schooling scale that dropped the highest categories, the omission of the birth-year-by-origin-rank interaction block from the event study, and a mis-coding of rural origin. Each correction changed reported results, and the corrected results are the ones reported here. The errors and their consequences are described in Sections 3.4, 4.2 and 5.3 of the manuscript rather than being concealed.

3. *Drafting and editing of prose.* The assistant was used to draft and revise sections of the text. The authors reviewed, edited and approved all of it, and confirm that the final text reflects their own analysis and conclusions.

4. *Literature search support.* The assistant was used to locate candidate references. Every reference in the list was then verified by the authors against the publisher's record or an equivalent bibliographic database; bibliographic details, including volume, issue, pages and DOI, were checked individually.

**Where it was not used.** No text, table, figure or numerical result in this manuscript was generated by a language model without verification against the data. No figure or image was generated by a generative model; all figures are produced by the code in Appendix D from the source data. No reference was included on the basis of a model's assertion alone.

**On the boundary with copy editing.** The Springer Nature policy exempts AI-assisted copy editing, meaning improvements to readability, grammar, spelling, punctuation and tone, from the requirement to declare. We have declared our use in full rather than relying on that exemption, because our use went beyond copy editing.
