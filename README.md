# GCF Project Evaluation Pipeline

**An open-source, interactive data pipeline for extracting, analysing, and communicating findings from the Green Climate Fund project portfolio.**

---

## Why This Exists

The [Green Climate Fund](https://www.greenclimate.fund/) makes its full project database publicly available through an open API — but raw API data is not analysis. This pipeline bridges that gap: it turns JSON records into structured tables, quantitative indicators, publication-quality charts, and auto-drafted narratives, all within a Jupyter notebook you can reopen and re-run as the portfolio evolves.

It was built for **evaluation professionals and researchers** who need to answer specific questions about the GCF portfolio — geographic reach, private sector engagement, financial concentration, implementation progress — without starting from scratch each time.

---

## Who Will Find This Useful

| Audience | Use case |
|---|---|
| **Independent evaluators** | Rapid portfolio overview and indicator generation for evaluation briefs |
| **Academic researchers** | Reproducible dataset extraction for climate finance studies |
| **MDB / development finance analysts** | Benchmarking GCF against other climate funds |
| **Journalists & policy advocates** | Fact-checking GCF commitments and country-level flows |
| **GCF staff and AEs** | Quick sense-checks on portfolio composition and trends |

---

## What It Does

```
API  ──►  Cache  ──►  Tabulation  ──►  Evaluation Q&A  ──►  FT-Style Charts  ──►  Narrative Report
          (parquet)   (any dimension)   (duplicate per EQ)   (reusable theme)     (markdown + Excel)
```

1. **Fetch & cache** — Paginates the full GCF projects API, saves to Parquet. Subsequent sessions load from cache in under a second. Set `FORCE_REFRESH = True` to re-pull.

2. **Data inventory** — Automatically catalogues every field: data type, completeness rate, unique values, sample. Lets you understand what indicators are actually available before writing analysis code.

3. **Portfolio tabulation** — One-function cross-tabs on any dimension: region, sector, accredited entity, project status, approval year. Produces count + total/average financing + portfolio share in a single call.

4. **Evaluation question template** — Each evaluation question gets its own notebook cell. Define your filter logic, specify your indicators, get a formatted summary table. Designed to be duplicated and adapted.

5. **Financial Times–style visualisations** — A lightweight chart theme replicating the FT's visual identity: salmon `#FFF1E5` background, deep blue `#0F5499` and claret `#990F3D` palette, clean spines, source attribution. Includes horizontal bar, grouped bar, and small-multiples chart types out of the box.

6. **Narrative generation** — Auto-drafts a structured findings summary (portfolio scale, financial profile, geographic distribution, implementation status) as Markdown. Intended as a first-draft scaffold for evaluation reports.

7. **Export** — Saves charts as high-resolution PNG (220 dpi), narratives as `.md`, and full processed data as a multi-sheet Excel workbook.

---

## Getting Started

### Requirements

```bash
pip install requests pandas numpy matplotlib openpyxl
# or, if using Anaconda:
conda install requests pandas numpy matplotlib openpyxl
```

Python 3.9+ recommended. No API key required — the GCF projects API is fully open.

### Run

Open `gcf_pipeline.ipynb` in Jupyter or VS Code and run cells sequentially. On first run, Section 1 fetches data from the API and caches it locally. All subsequent sessions load from cache.

```
gcf_pipeline.ipynb        ← Main pipeline (start here)
gcf_psf_risk_workflow.py  ← Standalone script for Private Sector Facility risk analysis
gcf_cache/                ← Auto-created: parquet data cache
gcf_output/               ← Auto-created: charts, narratives, Excel exports
```

### Fetch fresh data

In the configuration cell, set:

```python
FORCE_REFRESH = True
```

---

## Pipeline Structure

```
gcf_pipeline.ipynb
│
├── Setup               API config, output paths, pandas display options
├── Section 1           Fetch & cache (fetch_all_pages → parquet)
├── Section 2           Data inventory (field catalogue, auto-detect columns)
├── Section 3           Portfolio tabulation (region / sector / status / entity / year)
├── Section 4           Evaluation questions (EQ template cells — duplicate per question)
│   ├── EQ1 template    Geographic reach to vulnerable countries
│   └── EQ2 template    Private Sector Facility scale and risk profile
├── Section 5           FT-style visualizations
│   ├── Chart 1         Horizontal bar — top recipients by commitment
│   ├── Chart 2         Grouped bar — approvals by year × sector
│   └── Chart 3         Small multiples — status distribution by region
└── Section 6           Narrative generation + Excel export
```

---

## Data Source

**API:** `http://api.gcfund.org/v1/projects`
**License:** Public / open access. No authentication required.
**Coverage:** All GCF-approved projects, updated periodically by the GCF Secretariat.

---

## Visualisation Style

Charts follow the [Financial Times](https://www.ft.com/) visual language:

| Element | Value |
|---|---|
| Background | `#FFF1E5` (FT salmon) |
| Primary colour | `#0F5499` (FT deep blue) |
| Accent colours | `#990F3D`, `#FF8833`, `#0D7680` |
| Grid | Horizontal only, `#E0D5C9` |
| Spines | Bottom only |
| Typography | Arial / system sans-serif |

The `ft_base()` function in Section 5 sets all of this up. Call it to start any new chart.

---

## Extending the Pipeline

**Add an evaluation question:**
Duplicate any EQ cell in Section 4. Change the filter logic, add your indicators to the `indicators` dict, and call `portfolio_table()` on your filtered dataframe.

**Add a chart type:**
Call `fig, ax = ft_base(title='...', subtitle='...')` and use standard matplotlib on the returned `ax`. The theme is applied automatically.

**Add new data fields:**
If the API returns fields not auto-detected by `detect_col()`, add them to the `COL` dictionary in Section 2 manually.

---

## Contributing

Pull requests welcome. If you find an issue with the API pagination logic, field normalisation, or chart rendering, please open an issue with a minimal reproducible example.

---

## Acknowledgements

Built against the GCF public API. The Financial Times chart style is reproduced for research and non-commercial use; the FT's visual identity remains their own.

---

*Pipeline developed for evaluation and research use. Not an official GCF product.*
