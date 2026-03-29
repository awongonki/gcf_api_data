#!/usr/bin/env python3
"""
GCF Private Sector Risk Assessment Pipeline.

1) Fetch GCF projects API
2) Filter for private sector (Division == 'PSF' or financier head)
3) Compute quantitative risk metrics
4) Generate FT-style charts + narrative report
5) Advisory from Fed/USAID/IMF perspectives
"""
import os
import json
from typing import List, Dict
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import click

DEFAULT_API_URL = "http://api.gcfund.org/v1/projects"

def load_config():
    cfg = {}
    cfg["api_url"] = os.getenv("GCF_API_URL", DEFAULT_API_URL)
    cfg["api_key"] = os.getenv("GCF_API_KEY", "")
    cfg["out_dir"] = os.getenv("GCF_OUT_DIR", "gcf_risk_output")
    os.makedirs(cfg["out_dir"], exist_ok=True)
    return cfg

def get_headers(api_key: str):
    h = {"Accept": "application/json"}
    if api_key:
        h["Authorization"] = f"Bearer {api_key}"
    return h

def fetch_all(api_url: str, headers: Dict[str, str]) -> List[dict]:
    records = []
    url = api_url
    while url:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("projects") or data.get("data") or data.get("items") or data.get("results") or []
        records.extend(items)
        url = data.get("next") or data.get("nextPage") or None
        if not url:
            break
    return records

def normalize(records: List[dict]) -> pd.DataFrame:
    df = pd.json_normalize(records, sep="_")
    df.columns = [c.lower().replace(".", "_") for c in df.columns]
    return df

def filter_private_sector(df: pd.DataFrame) -> pd.DataFrame:
    # Filter by Division == 'PSF' (Private Sector Facility)
    if "division" in df.columns:
        psf_df = df[df["division"].str.upper() == "PSF"]
    else:
        psf_df = df  # fallback if no division field
    
    # Alternatively, filter by financier head (assuming 'financier' or 'financing_head' field)
    # Adjust based on actual field name; here assuming 'financier_head'
    if "financier_head" in psf_df.columns:
        psf_df = psf_df[psf_df["financier_head"].notna()]
    
    return psf_df

def compute_risk_metrics(df: pd.DataFrame) -> Dict:
    out = {}
    out["project_count"] = len(df)
    out["country_count"] = int(df["country"].nunique()) if "country" in df else 0
    out["status_distribution"] = df["status"].value_counts(dropna=False).to_dict() if "status" in df else {}
    
    # Financial metrics
    money_cols = [c for c in df.columns if "commitment" in c or "amount" in c or "funded" in c]
    if money_cols:
        col = money_cols[0]
        df[col] = pd.to_numeric(df[col], errors="coerce")
        out["money_field"] = col
        out["total_amount"] = float(df[col].sum(skipna=True))
        out["median_amount"] = float(df[col].median(skipna=True))
        out["max_amount"] = float(df[col].max(skipna=True))
        out["min_amount"] = float(df[col].min(skipna=True))
        
        # Risk indicators
        out["exposure_concentration"] = float((df[col] / df[col].sum()).max())  # Largest project %
        out["diversification_index"] = float(df["country"].nunique() / len(df)) if "country" in df else 0  # Country diversity
        out["volatility_proxy"] = float(df[col].std() / df[col].mean()) if df[col].mean() > 0 else 0  # Coefficient of variation
    
    # Qualitative risk (if fields exist)
    if "risk_level" in df.columns:
        out["risk_distribution"] = df["risk_level"].value_counts(dropna=False).to_dict()
    
    return out

def save_artifacts(df: pd.DataFrame, cfg: Dict):
    base = cfg["out_dir"]
    df.to_csv(os.path.join(base, "gcf_psf_projects.csv"), index=False, encoding="utf-8")
    df.to_parquet(os.path.join(base, "gcf_psf_projects.parquet"), index=False)
    return os.path.join(base, "gcf_psf_projects.csv")

def make_risk_chart(df: pd.DataFrame, cfg: Dict) -> str:
    if "country" not in df.columns:
        return ""
    money_col = next((c for c in df.columns if "commitment" in c or "amount" in c), None)
    if not money_col:
        return ""
    df[money_col] = pd.to_numeric(df[money_col], errors="coerce").fillna(0)
    top = df.groupby("country", as_index=False)[money_col].sum().nlargest(10, money_col)
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    sns.barplot(data=top, x=money_col, y="country", palette="Reds")
    plt.title("Top 10 Countries by PSF Commitment Amount (Risk Exposure)")
    plt.tight_layout()
    out_fn = os.path.join(cfg["out_dir"], "gcf_psf_risk_exposure.png")
    plt.savefig(out_fn, dpi=220)
    plt.close()
    return out_fn

def narrative(metrics: Dict, chart_path: str, cfg: Dict):
    tpl = Template(
        """GCF Private Sector Facility (PSF) Risk Assessment Report
Generated on {{ now }}.

Quantitative Overview:
- Total PSF projects: {{ metrics.project_count }}
- Countries covered: {{ metrics.country_count }}
- Status breakdown:
{% for k,v in metrics.status_distribution.items() -%}
  - {{ k }}: {{ v }}
{% endfor %}
{% if metrics.money_field %}
Financial Metrics:
- Money field: {{ metrics.money_field }}
- Total amount: {{ metrics.total_amount | round(2) }}
- Median amount: {{ metrics.median_amount | round(2) }}
- Max amount: {{ metrics.max_amount | round(2) }}
- Min amount: {{ metrics.min_amount | round(2) }}

Risk Indicators:
- Exposure concentration (largest project %): {{ metrics.exposure_concentration | round(4) }}
- Diversification index (country diversity): {{ metrics.diversification_index | round(4) }}
- Volatility proxy (coefficient of variation): {{ metrics.volatility_proxy | round(4) }}
{% if metrics.risk_distribution %}
- Risk level distribution:
{% for k,v in metrics.risk_distribution.items() -%}
  - {{ k }}: {{ v }}
{% endfor %}
{% endif %}

Chart: {{ chart_path }}

Advisory from Quantitative Risk Analyst Perspectives:

**Federal Reserve (Fed) Perspective (Macro-Financial Stability):**
As a central banker focused on systemic risk, I advise monitoring the PSF portfolio for concentration risks. With exposure concentration at {{ metrics.exposure_concentration | round(4) }}, ensure no single project jeopardizes broader financial stability. Diversify across countries and sectors to mitigate contagion. Recommend stress-testing against global shocks (e.g., interest rate hikes, currency volatility). If volatility proxy exceeds 1.0, consider hedging instruments or phased disbursements.

**USAID Perspective (Development Impact & Sustainability):**
From a development economist viewpoint, prioritize alignment with sustainable development goals. The diversification index of {{ metrics.diversification_index | round(4) }} indicates geographic spread, but assess qualitative risks like local governance and environmental impact. Advise integrating risk-adjusted returns: projects with higher median amounts ({{ metrics.median_amount | round(2) }}) should demonstrate clear poverty reduction or climate resilience outcomes. Use USAID's risk frameworks to evaluate co-financing leverage and exit strategies for private sector involvement.

**IMF Perspective (Fiscal & Economic Policy):**
As an IMF economist, focus on fiscal sustainability and macroeconomic implications. Total PSF commitments of {{ metrics.total_amount | round(2) }} should be evaluated against national debt burdens in recipient countries. High volatility ({{ metrics.volatility_proxy | round(4) }}) signals potential fiscal risks; recommend debt sustainability analyses and conditionalities on disbursements. Advise on crowding-out effects: ensure GCF funding complements rather than substitutes domestic private investment. Monitor for spillover effects on exchange rates and inflation in vulnerable economies.

Recommendations:
- Enhance data granularity for risk modeling (e.g., add default probabilities, recovery rates).
- Implement portfolio optimization to balance risk-return.
- Regular scenario analysis for climate-related shocks.
- Collaborate with private financiers for shared risk assessments.
"""
    )
    out = tpl.render(metrics=metrics, chart_path=chart_path or "N/A", now=pd.Timestamp.now())
    path = os.path.join(cfg["out_dir"], "gcf_psf_risk_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return path

@click.command()
@click.option("--run-once", is_flag=True, default=False, help="Run once and exit.")
def main(run_once):
    cfg = load_config()
    headers = get_headers(cfg["api_key"])
    print("Fetching data from", cfg["api_url"])
    rows = fetch_all(cfg["api_url"], headers)
    print("Records fetched:", len(rows))
    if not rows:
        raise SystemExit("No records.")

    df = normalize(rows)
    psf_df = filter_private_sector(df)
    print("PSF projects filtered:", len(psf_df))
    if psf_df.empty:
        raise SystemExit("No PSF projects found.")

    metrics = compute_risk_metrics(psf_df)
    csv_file = save_artifacts(psf_df, cfg)
    chart = make_risk_chart(psf_df, cfg)
    report_file = narrative(metrics, chart or "N/A", cfg)

    print("Saved CSV:", csv_file)
    print("Saved chart:", chart)
    print("Saved report:", report_file)
    print("Done.")

if __name__ == "__main__":
    main()