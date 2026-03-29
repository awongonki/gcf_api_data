# GCF Project Evaluation Pipeline

**An open-source, interactive data pipeline for extracting, analysing, and communicating quantitative risk findings from the Green Climate Fund project portfolio.**

---

## Why This Exists

The [Green Climate Fund](https://www.greenclimate.fund/) makes its full project database publicly available through an open API — but raw API data is not analysis. This pipeline bridges that gap: it turns nested JSON records into structured risk tables, quantitative indicators, publication-quality charts, and auto-drafted narratives, all within a Jupyter notebook you can reopen and re-run as the portfolio evolves.

It was built by an **evaluation quant specialist** working on GCF portfolio assessment, applying frameworks familiar to IMF economists, development finance analysts, and institutional risk practitioners — concentration metrics, instrument structure analysis, at-risk classification, vintage cohort decomposition, and leverage distribution.

---

## Who Will Find This Useful

| Audience | Use case |
|---|---|
| **Evaluation quant specialists** | IMF-style portfolio risk indicators for independent evaluations and PIRs |
| **Development finance researchers** | Reproducible climate finance dataset with instrument-level granularity |
| **MDB / DFI risk analysts** | Concentration, leverage, and repayment exposure benchmarking |
| **Academic researchers** | Longitudinal panel of GCF approvals with financing structure data |
| **Journalists & policy advocates** | Fact-checking GCF commitments, cancellation rates, country-level flows |
| **GCF staff and accredited entities** | Quick portfolio sense-checks, instrument mix analysis |

---

## What It Does

```
API (open, no key)
  └─► Parquet cache (one fetch; reloads in <1s)
        └─► Data inventory (field catalogue, nested field unnesting)
              └─► Portfolio tabulation (any dimension, one function call)
                    └─► Risk analysis (5 EQ cells — duplicate to extend)
                          └─► FT-style charts (reusable theme)
                                └─► Narrative + Excel export
```

### Confirmed API fields (live data)

| Category | Fields |
|---|---|
| Identity | `ApprovedRef`, `ProjectsID`, `ProjectName`, `BoardMeeting` |
| Classification | `Theme`, `Sector`, `Size`, `RiskCategory`, `Status` |
| Financing | `TotalGCFFunding`, `TotalCoFinancing`, `TotalValue` |
| Timing | `ApprovalDate`, `DateImplementationStart`, `DateClosing`, `DurationMonths` |
| Impact | `LifeTimeCO2`, `DirectBeneficiaries`, `IndirectBeneficiaries` |
| Nested | `Countries[]` → CountryName, Region, LDCs, SIDS |
| Nested | `Entities[]` → Name, Acronym, Access (Direct/International), Type |
| Nested | `Funding[]` → **Instrument, Source, BudgetUSDeq, Currency** per line item |
| Nested | `Disbursements[]` → AmountDisbursed, DateEffective |

The `Funding[]` field is the key for instrument-level risk analysis — each project carries multiple rows with `Instrument` (Grant, Senior Loan, Subordinated Loan, Equity, Guarantee, Reimbursable Grant, Results-Based Payment) split by `Source` (GCF vs Co-Financing).

---

## Portfolio Risk Framework (Section 4)

Five evaluation questions grounded in quantitative risk methodology:

| EQ | Question | Key Metrics |
|---|---|---|
| **EQ1** | How concentrated is the portfolio? | HHI by country/region/entity, Gini coefficient, effective-N, top-1/5/10 tail exposure |
| **EQ2** | What is the instrument structure and repayment risk? | Grant vs loan vs equity vs guarantee mix by sector; debt exposure by region |
| **EQ3** | Which projects are at risk or failing? | Cancellation rate, portfolio-at-risk (USD), overdue active projects, duration overrun |
| **EQ4** | How do approval-year cohorts compare? | Vintage analysis: size, leverage, cancellation %, private %, high-risk %; instrument mix by year |
| **EQ5** | Is co-financing leverage stable or driven by outliers? | Median/CoV, outlier count, crowding-in by instrument and region |

---

## Getting Started

### Requirements

```bash
pip install requests pandas numpy matplotlib openpyxl
# or Anaconda:
conda install requests pandas numpy matplotlib openpyxl
```

Python 3.9+. **No API key required** — the GCF projects API is fully open.

### Run

Open `gcf_pipeline.ipynb` in Jupyter or VS Code and run cells top to bottom. Section 1 fetches ~354 projects from the API and caches them locally. All subsequent sessions load from cache instantly.

```
gcf_pipeline.ipynb        ← Main pipeline (start here)
gcf_psf_risk_workflow.py  ← Standalone PSF risk script
gcf_cache/                ← Auto-created: parquet data cache
gcf_output/               ← Auto-created: charts (PNG), narratives (MD), Excel
```

Set `FORCE_REFRESH = True` in the configuration cell to re-fetch from the API.

---

## Notebook Structure

```
gcf_pipeline.ipynb
│
├── Setup               Config, paths, display options
├── Section 1           Fetch & cache (single API call → parquet)
├── Section 2           Data inventory + unnest Countries[], Entities[], add derived cols
├── Section 3           Portfolio tabulation — region, theme, sector, status, size,
│                       risk category, entity, access modality, LDC/SIDS, annual trend
├── Section 4           Portfolio Risk Analysis
│   ├── Risk Setup      Explode Funding[] → instrument-level table; HHI/Gini helpers
│   ├── Risk EQ1        Concentration risk
│   ├── Risk EQ2        Instrument structure & repayment risk
│   ├── Risk EQ3        At-risk / implementation failures
│   ├── Risk EQ4        Vintage cohort analysis
│   ├── Risk EQ5        Co-financing leverage distribution
│   └── Template        Blank EQ cell to duplicate
├── Section 5           FT-style visualisations
│   ├── Chart 1         Horizontal bar — top 15 countries by GCF commitment
│   ├── Chart 2         Stacked bar — approvals by year × theme
│   ├── Chart 3         Scatter — project size vs leverage (by theme)
│   └── Chart 4         Horizontal stacked — LDC / SIDS / Other by region
└── Section 6           Narrative generation + multi-sheet Excel export
```

---

## Visualisation Style

Charts use the [Financial Times](https://www.ft.com/) visual identity:

| Element | Value |
|---|---|
| Background | `#FFF1E5` (FT salmon) |
| Primary | `#0F5499` (FT deep blue) |
| Accents | `#990F3D` · `#FF8833` · `#0D7680` |
| Grid | Horizontal lines only, `#E0D5C9` |
| Spines | Bottom only |
| Font | Arial / system sans-serif |
| Resolution | 220 dpi PNG output |

`ft_base(title, subtitle)` returns a pre-styled `(fig, ax)`. All chart code builds on top of it.

---

## Extending the Pipeline

**Add a risk question:** Duplicate the template cell at the bottom of Section 4. Filter `df`, define your indicators dict, call `portfolio_table()` or write custom aggregations.

**Add a chart:** Call `fig, ax = ft_base(title='...', subtitle='...')` and use standard matplotlib on `ax`.

**Instrument-level analysis:** Use `gcf_fund` (GCF rows only) or `cofin_df` (co-financing rows) — both are built in the Risk Setup cell from the `Funding[]` nested field.

---

## Data Source

**API:** `http://api.gcfund.org/v1/projects`
**Access:** Public. No authentication or API key required.
**Coverage:** All GCF-approved projects (Funding Proposals), updated by the GCF Secretariat.

---

## Contributing

Pull requests welcome. If you find issues with field parsing, nested unnesting, or chart rendering, please open an issue with a minimal reproducible example.

---

## Acknowledgements

Built against the GCF public API. The Financial Times chart style is reproduced for research and non-commercial use; the FT's visual identity is their own.

---

*Pipeline developed for evaluation and research use. Not an official GCF product.*
