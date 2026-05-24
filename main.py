rom __future__ import annotations

import os
from typing import List, Dict

import pandas as pd
import plotly.graph_objects as go
import requests
from jinja2 import Template


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = "output"
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "ecb_banking_dashboard.html")

START_DATE = "2023-01-01"
END_DATE = "2026-12-31"

ECB_API_BASE = "https://data-api.ecb.europa.eu/service/data"


# ============================================================
# DATA (VALID SDMX SERIES)
# ============================================================

METRICS: List[Dict] = [
    # CET1
    {"name": "CET1 Ratio", "country": "Italy",
     "series_key": "SUP/Q.IT.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C"},
    {"name": "CET1 Ratio", "country": "Spain",
     "series_key": "SUP/Q.ES.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C"},

    # LCR
    {"name": "Liquidity Coverage Ratio", "country": "Italy",
     "series_key": "SUP/Q.IT.W0._Z.I3017._T.SII._Z._Z._Z.PCT.C"},
    {"name": "Liquidity Coverage Ratio", "country": "Spain",
     "series_key": "SUP/Q.ES.W0._Z.I3017._T.SII._Z._Z._Z.PCT.C"},

    # NPL
    {"name": "Non Performing Loans Ratio", "country": "Italy",
     "series_key": "SUP/Q.IT.W0._Z.I7000._T.SII._Z._Z._Z.PCT.C"},
    {"name": "Non Performing Loans Ratio", "country": "Spain",
     "series_key": "SUP/Q.ES.W0._Z.I7000._T.SII._Z._Z._Z.PCT.C"},
]


# ============================================================
# ECB API
# ============================================================

def fetch_ecb_series(series_key: str) -> pd.DataFrame:
    """
    Fetch ECB SDMX series and return a clean dataframe.
    """

    url = f"{ECB_API_BASE}/{series_key}"

    params = {
        "format": "sdmx-json",
        "startPeriod": START_DATE,
        "endPeriod": END_DATE
    }

    headers = {"Accept": "application/json"}

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()

    try:
        series = payload["dataSets"][0]["series"]
        observations = next(iter(series.values()))["observations"]
        dimensions = payload["structure"]["dimensions"]["observation"][0]["values"]

    except (KeyError, IndexError):
        raise ValueError(f"No data for series: {series_key}")

    records = []

    for index, value in observations.items():
        period = dimensions[int(index)]["id"]
        records.append(
            {
                "date": period,
                "value": value[0] if value else None
            }
        )

    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["date"] = pd.PeriodIndex(df["date"], freq="Q").to_timestamp()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df.sort_values("date")


# ============================================================
# DATA COLLECTION
# ============================================================

def collect_all_data() -> pd.DataFrame:
    """
    Collect all metrics into a single dataframe.
    """

    all_frames: List[pd.DataFrame] = []

    for metric in METRICS:

        print(f"Downloading {metric['name']} for {metric['country']}...")

        try:
            df = fetch_ecb_series(metric["series_key"])

            if df.empty:
                print(f"No data found for {metric['series_key']}")
                continue

            df["country"] = metric["country"]
            df["metric"] = metric["name"]

            all_frames.append(df)

        except Exception as exc:
            print(f"ERROR -> {metric['country']} | {metric['name']}: {exc}")

    if not all_frames:
        raise RuntimeError("No data downloaded from ECB API")

    return pd.concat(all_frames, ignore_index=True)


# ============================================================
# CHARTS
# ============================================================

def build_plot(df: pd.DataFrame, metric_name: str) -> str:
    """
    Build interactive Plotly chart.
    """

    metric_df = df[df["metric"] == metric_name]

    fig = go.Figure()

    for country in metric_df["country"].unique():

        country_df = metric_df[metric_df["country"] == country]

        fig.add_trace(
            go.Scatter(
                x=country_df["date"],
                y=country_df["value"],
                mode="lines+markers",
                name=country
            )
        )

    fig.update_layout(
        title=metric_name,
        template="plotly_white",
        height=500,
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Percentage",
        legend_title="Country"
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


# ============================================================
# HTML TEMPLATE
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ECB Banking Dashboard by Luca Bacciarelli</title>

    <style>
        body {
            font-family: Arial;
            margin: 40px;
            background: #f4f6f9;
        }
        .chart {
            background: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>

<h1>ECB Banking Dashboard</h1>

<p>Italy vs Spain | 2023 - 2026</p>

{% for chart in charts %}
<div class="chart">
    {{ chart | safe }}
</div>
{% endfor %}

</body>
</html>
"""


def generate_html_report(charts: List[str]) -> None:

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    template = Template(HTML_TEMPLATE)
    html = template.render(charts=charts)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML generated: {OUTPUT_HTML}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("Starting ECB Banking Dashboard...")

    df = collect_all_data()

    charts = []

    for metric in sorted(set(df["metric"])):
        charts.append(build_plot(df, metric))

    generate_html_report(charts)

    print("Done.")


if __name__ == "__main__":
    main()
