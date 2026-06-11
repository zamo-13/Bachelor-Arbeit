# Thesis Intelligence Log
**Project:** Moderation Dynamics in Transition — TikTok vs. X, Germany, 2025 Federal Snap Election  
**Author:** Solo project  
**Last updated:** 2026-06-03  
**Purpose:** Living record of all findings, data anomalies, methodological decisions, and writing notes discovered during thesis development. Updated every session a relevant finding is made.

---

## How to read this log

Each entry has:
- **What was found** — the factual observation
- **Source** — where the evidence comes from
- **Where it goes in the thesis** — Body (which section) or Appendix
- **Status** — Open (needs action) / Resolved (decision made) / Writing note (just needs to appear in text)

---

## Entry 001 — All rows are multi-territory; zero rows are DE-only
**Date discovered:** 2026-06-01  
**What was found:** 100% of rows on both TikTok (999,079,277) and X (183,324) have a `territorial_scope` that spans multiple EEA territories. Neither platform issues decisions scoped exclusively to Germany. The `contains("DE")` filter correctly captures all decisions affecting German users, but none of these are Germany-only enforcement actions.  
**Source:** B2 profiling script output (run locally against harmonized parquet files)  
**Implication:** The thesis cannot describe these as "German moderation decisions." The correct framing throughout is "moderation decisions whose territorial scope includes Germany" or "decisions affecting the German information environment."  
**Where it goes:**
- **Body §3.1** (Data Source & Scope): one sentence clarifying the territorial framing
- **Body §3.3** (Research Design): one sentence confirming inclusion of multilateral-scope decisions is intentional and consistent with the exposé
- **Body §5.3** (Limitations): one paragraph — the data does not distinguish between decisions targeting Germany specifically and EU-wide enforcement actions that happen to include Germany  
**Status:** Writing note

---

## Entry 002 — Pre-2025 rows exist due to backdated platform submissions
**Date discovered:** 2026-06-01  
**What was found:** Both platforms contain rows with `application_date` outside 2025, even though the downloaded dump files are all from 2025:

| Date range | TikTok rows | X rows |
|---|---|---|
| 2020 | 3 | 0 |
| 2023 | 10,776 | 0 |
| 2024-12 | 1,380,231 | 3 |
| **Total out-of-scope** | **1,391,010** | **3** |
| **% of dataset** | **0.14%** | **~0.00%** |

**Source:** B2 profiling script output; confirmed by official DSA Transparency Database dashboard documentation  
**Why this happens:** The DSA daily dump files are organised by *submission date* (when the platform uploaded the record to the Commission's database). The `application_date` field is platform self-reported and records when the moderation decision was actually applied. Platforms can and do submit records late — days, weeks, or months after the decision. This is a documented characteristic of the database, not a download or script error.  
**Official source confirming this:** DSA Transparency Database Dashboard documentation states: *"the date refers to the date of submission of the statement of reasons to the Database"* — confirming that dump file organisation and the dashboard's timeline charts use submission date, not `application_date`. URL: https://transparency.dsa.ec.europa.eu/dashboard  
**Decision taken:** Filter to `application_date ∈ [2025-01-01, 2025-12-31]` before analysis. 1,391,013 rows excluded (0.14% of TikTok dataset; 3 rows of X). Documented in `cleaning_decisions.md` as CD-20260529-01 (to be added).  
**Where it goes:**
- **Body §3.1** (Data Source & Scope): one sentence — "Records with an `application_date` outside the 2025 calendar year (n = 1,391,013; 0.14% of the dataset) were excluded, as these represent backdated submissions outside the defined study period."
- **Body §5.3** (Limitations): one sentence — the `application_date` is platform self-reported and unverifiable by the Commission; the 2020 and 2023 rows may represent genuine backlog, system migration artefacts, or platform-side data quality issues. The analysis cannot distinguish between these cases.  
**Status:** Resolved — filter to be applied in next pipeline step

---

## Entry 003 — TikTok monthly row counts decline sharply across 2025 (v1/v2 schema break effect)
**Date discovered:** 2026-06-01  
**What was found:** TikTok monthly row counts show a 35× decline from peak to year-end:

| Month | Rows |
|---|---|
| 2025-01 | 108,870,939 |
| 2025-02 | 155,621,404 |
| 2025-03 | 202,128,288 (peak) |
| 2025-06 | 77,126,737 |
| 2025-07 | 61,793,705 |
| 2025-12 | 3,093,951 |

v1 (Jan–Jun): 831,613,348 rows (83.24%); v2 (Jul–Dec): 167,465,929 rows (16.76%)  
**Source:** B2 profiling script output  
**Why this happens:** This is a known reporting behaviour change, not a real decline in moderation activity. The v2 schema (introduced July 1, 2025) changed how platforms are permitted to report aggregated and bulk automated decisions. TikTok restructured its submission pipeline accordingly. The row count drop across the schema break therefore reflects a *reporting methodology change*, not a genuine reduction in moderation volume.  
**Implication for analysis:** Any cross-version comparison of absolute row counts is invalid without explicit correction. RQ2 event study (Feb 23 election) sits entirely within v1 — no problem there. RQ1 cross-platform comparison must either (a) restrict to v1 only, or (b) use version-stratified reporting.  
**Where it goes:**
- **Appendix** (Data Coverage Table): full monthly row count table for both platforms — justifies the v1-only analytical decision and allows readers to verify
- **Body §3.3** (Research Design): one paragraph explaining the schema break effect on row counts and the resulting analytical constraint
- **Body §5.3** (Limitations): one sentence — v2 row counts are not directly comparable to v1 due to reporting methodology changes  
**Status:** Writing note — analytical decision (v1-only vs. both versions) still to be formally locked

---

## Entry 004 — Automation contrast between platforms is extreme and analytically central
**Date discovered:** 2026-06-01  
**What was found:**

| Flag | TikTok | X |
|---|---|---|
| `automated_detection = Yes` | **98.65%** | **0.00%** |
| `automated_decision = FULLY` | **95.01%** | **0.80%** |
| `automated_decision = NOT_AUTOMATED` | 4.99% | **99.20%** |
| `automated_decision = PARTIALLY` | 0.00% | 0.00% |

X has zero automated detections — every single moderated item on X was flagged by a human or external trusted flagger. TikTok operates near-total automation end to end.  
**Source:** B2 profiling script output  
**Implication:** This is the headline empirical finding for RQ1. The two platforms operate on fundamentally different moderation paradigms. This directly supports H1 (TikTok higher automation in visual-harm categories → granularity reduction) and sets up the broader platform comparison.  
**Where it goes:**
- **Body §4.1** (RQ1 Results — Cross-Platform Comparison): primary results table or Figure 1. Too central for appendix.
- **Body §2.4** (Theoretical Background — Algorithmic Governance): can be pre-announced as the empirical pattern the theory section is setting up  
**Status:** Writing note — 📌 KEEP as Figure/Table in body §4.1

---

## Entry 005 — AMAR reference values locked
**Date discovered:** 2026-06-01  
**What was found:** Official AMAR (Average Monthly Active Recipients, Art. 42(3) DSA) figures for Germany for 2025:

| Platform | Period | Date range | AMAR (DE) | api_version |
|---|---|---|---|---|
| TikTok | H1 | Jan 1 – Jun 30 | 25,700,000 | v1 |
| TikTok | H2 | Jul 1 – Dec 31 | 27,300,000 | v2 |
| X | Q1 | Jan 1 – Mar 31 | 15,598,407 | v1 |
| X | Q2 | Apr 1 – Jun 30 | 14,929,142 | v1 |
| X | H2 | Jul 1 – Dec 31 | 9,511,180 | v2 |

Note: TikTok periods are semi-annual; X periods are quarterly in H1 then semi-annual in H2. Period boundaries align with v1/v2 schema split.  
**Source:** TikTok_AMAR.rtf and X_AMAR.rtf (project notes); reference CSV `amar_reference.csv` created as canonical source  
**Implication:** All normalization calculations (decisions per 1,000 AMAR) must join against this reference table, not hardcode numbers. The exposé uses the term "MAU" but the DSA legal term is AMAR — the thesis must use AMAR consistently.  
**Where it goes:**
- **Appendix**: full AMAR reference table with legal basis and source notes
- **Body §3.4** (Normalization): mention figures in prose, cite appendix for full table  
**Status:** Resolved — `amar_reference.csv` created and verified 📌 KEEP in Appendix

---

## Entry 006 — X user base drops 39% across 2025
**Date discovered:** 2026-06-01  
**What was found:** X's German AMAR falls from 15,598,407 (Q1) to 9,511,180 (H2) — a 39% decline within the study year.  
**Source:** X_AMAR.rtf (project notes)  
**Implication:** Normalization per 1,000 AMAR is essential for X; raw row counts are misleading when the denominator is itself changing. Also worth noting in §4.1 or §5.3 as context — X's declining user base in Germany is itself a platform governance story.  
**Where it goes:**
- **Body §3.4** (Normalization): justification for why per-1,000-AMAR rather than raw counts
- **Body §4.1 or §5.3**: one sentence contextualising X's declining German reach  
**Status:** Writing note

---

## Entry 007 — Unit of analysis ambiguity (decision vs. content item)
**Date discovered:** 2026-06-01  
**What was found:** TikTok has ~999M rows vs. X's 183K. Even after normalization, the per-AMAR ratio is far larger than the canonical "~350× more moderation per user" figure cited in the exposé's literature review. The most likely explanation is that TikTok reports one row per content item flagged, while X may report more aggregated decisions — but this has not yet been confirmed against the DSA database field documentation.  
**Source:** Inference from profiling results + exposé literature review  
**Action needed:** Check DSA documentation or a sample TikTok row to confirm whether one row = one decision or one piece of content. Determine whether `decision_visibility` or `content_type` helps disambiguate. Declare the unit of analysis explicitly in §3.3.  
**Where it goes:**
- **Body §3.3** (Research Design): explicit declaration of unit of analysis
- **Body §5.3** (Limitations): if unit cannot be fully verified, acknowledge as a comparability constraint  
**Status:** ✅ Resolved — confirmed via official DSA documentation (Art. 17 DSA): one row = one SoR = one moderation decision on one piece of content. PUID is unique per row. Unit of analysis declared as: one Statement of Reasons (SoR) per content item moderated.

---

## Entry 009 — territorial_scope captures enforcement scope, not content origin
**Date discovered:** 2026-06-03  
**What was found:** The `territorial_scope` field in the DSA Transparency Database records the jurisdictions in which a moderation decision is *applied* (i.e. where content is restricted), not where the content was created, posted from, or what it was about. Since 100% of rows are multi-territorial, the DE filter captures all moderation decisions affecting the German information environment — including EU-wide enforcement actions that happen to include Germany — but cannot isolate content that originated in Germany or was specifically about the German snap election.  
**Source:** DSA database field documentation (Art. 17 DSA); confirmed by structural analysis of profiling output; consistent with Trujillo et al. (2025) and Shahi et al. (2025) who face the same constraint.  
**Implication:** The thesis cannot claim to analyse "German moderation decisions" or "election-related content" directly. The correct scope statement throughout is: "moderation decisions affecting the German information environment." This is a structural limitation of the DSA reporting framework shared by all empirical studies using this database — not a flaw specific to this thesis.  
**Framing fix applied in:** Supervisor email (sent 2026-06-03); to be applied consistently in all thesis sections.  
**Where it goes:**
- **Body §3.1** (Data Source): one sentence on territorial framing
- **Body §3.3** (Research Design): confirm inclusion of multilateral-scope decisions is intentional
- **Body §5.3** (Limitations): one paragraph — suggested draft: *"The DSA Transparency Database does not record the geographic origin of moderated content, nor whether content was thematically related to the German federal election. The `territorial_scope` field indicates the jurisdictions in which a moderation decision was applied, not where content originated. Consequently, the dataset captures all moderation decisions affecting the German information environment — including EU-wide enforcement actions — but cannot isolate decisions specifically targeting German-origin or election-related material. This is a structural constraint of the DSA reporting framework shared by all empirical studies using this database (cf. Trujillo et al., 2025; Shahi et al., 2025)."*  
**Status:** ✅ Resolved — framing corrected; limitation documented

---

## Entry 010 — Column selection post-hoc validation: 9-column choice defensible
**Date discovered:** 2026-06-03  
**What was found:** Three excluded columns were evaluated against actual TikTok sample data to assess whether their omission is a methodological gap. Results:

| Column | Assessment | Variance in data | Conclusion |
|---|---|---|---|
| `source_type` | Relevant in theory (proactive vs. reactive moderation) | Near-zero: 99.7% SOURCE_VOLUNTARY, 0.3% SOURCE_ARTICLE_16 | Not a serious gap — confirms TikTok is almost entirely proactive, but adds no analytical depth |
| `decision_ground` | Meaningful (ToS vs. illegal content) | Near-zero: 99.7% INCOMPATIBLE_CONTENT, 0.3% ILLEGAL_CONTENT | Borderline useful — could serve as robustness check; not having it is not a critical gap |
| `content_date` (moderation delay) | Theoretically strong — used by Drolsbach & Pröllochs and Trujillo et al. | Structurally broken: 89.8% of rows have content_date = application_date (zero delay); mean "delay" of 15 days driven by outliers (max: 3,452 days) | Omission justified by data quality failure — TikTok appears to batch-report content dates at moderation date, making delay analysis meaningless |

The three columns that were 100% missing in the original profiling (decision_monetary, end_date_account_restriction, account_type) were confirmed genuinely useless.  
**Source:** Sample file evaluation (separate chat session, 2026-06-03); consistent with data quality warnings in Groesch et al. (2026) and Trujillo et al. (2025).  
**Implication:** The 9-column selection is methodologically sound for the analytical moves required (automation rates, category distributions, temporal patterns). The moderation delay limitation is now citable as a data quality issue rather than a design oversight — which is a stronger methodological point.  
**Where it goes:**
- **Body §3.2** (Variables / Operationalization): brief note on why delay analysis is not included, citing the content_date data quality issue
- **Body §5.3** (Limitations): one sentence — moderation delay analysis was not feasible due to systematic batch-reporting of `content_date` values at the moderation date (cf. Trujillo et al., 2025; Groesch et al., 2026)
- **Body §3.3** (Research Design): optionally note that `decision_ground` was evaluated but near-zero variance limited its analytical value  
**Status:** ✅ Resolved — column selection validated; limitations documented

---

## Open items tracker

| # | Item | Priority | Blocking what |
|---|---|---|---|
| 1 | ~~Verify unit of analysis~~ | ~~High~~ | ✅ Done — Entry 007 / Entry 008 |
| 2 | ~~Apply `application_date` 2025 filter~~ | ~~High~~ | ✅ Done — Entry 002 / Entry 008 |
| 3 | Lock RQ1 scope: v1-only or both versions — Entry 003 | High | RQ1 — awaiting Prof. Trier reply |
| 4 | ~~Add CD-20260529-01 to `cleaning_decisions.md`~~ | ~~Medium~~ | ✅ Done — CD-20260602-01 |
| 5 | Update `data_dictionary.md` metadata header (rows, dates) | Low | Documentation completeness |
| 6 | Lock RQ2 event window (baseline / event / post periods) | High | RQ2 — awaiting Prof. Trier reply |
| 7 | Framing fix: replace "German decisions" with "decisions affecting German information environment" throughout all thesis drafts | Medium | Writing consistency |

---

*This log is updated every session a new finding is made. Do not delete entries — mark them Resolved or superseded with a note.*
