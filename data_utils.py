"""
Simple Data Module for Flask App
Loads cached OWID data and provides basic analysis functions
"""

import os
import json
import time
import urllib.request
import pandas as pd
import numpy as np

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "cache")
OWID_CACHE = os.path.join(CACHE_DIR, "owid_emissions.csv")
NOMINAL_GDP_CACHE = os.path.join(CACHE_DIR, "worldbank_gdp_per_capita_nominal.csv")


# ── World Bank nominal GDP per capita (current US$) ──
_nominal_gdp_df = None


def load_nominal_gdp_per_capita():
    """Load (and download if missing/stale) nominal GDP per capita from World Bank.
    Indicator: NY.GDP.PCAP.CD (GDP per capita, current US$).
    Cached as CSV; refreshed if older than 30 days.
    """
    global _nominal_gdp_df
    if _nominal_gdp_df is not None:
        return _nominal_gdp_df

    need_download = True
    if os.path.exists(NOMINAL_GDP_CACHE):
        age_days = (time.time() - os.path.getmtime(NOMINAL_GDP_CACHE)) / 86400
        if age_days < 30:
            need_download = False

    if need_download:
        try:
            url = (
                "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD"
                "?date=2001:2023&format=json&per_page=20000"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = json.loads(resp.read().decode())

            rows = []
            for entry in raw[1]:
                if entry["value"] is not None:
                    rows.append(
                        {
                            "iso_code": entry["countryiso3code"],
                            "country": entry["country"]["value"],
                            "year": int(entry["date"]),
                            "gdp_per_capita_nominal": round(entry["value"]),
                        }
                    )
            wb_df = pd.DataFrame(rows)
            os.makedirs(CACHE_DIR, exist_ok=True)
            wb_df.to_csv(NOMINAL_GDP_CACHE, index=False)
            print(f"[data_utils] Downloaded {len(wb_df)} nominal GDP rows from World Bank")
        except Exception as e:
            print(f"[data_utils] World Bank download failed: {e}")
            if not os.path.exists(NOMINAL_GDP_CACHE):
                _nominal_gdp_df = pd.DataFrame(
                    columns=["iso_code", "country", "year", "gdp_per_capita_nominal"]
                )
                return _nominal_gdp_df

    _nominal_gdp_df = pd.read_csv(NOMINAL_GDP_CACHE)
    return _nominal_gdp_df


def get_nominal_gdp_pc(iso_code, year=2023):
    """Return nominal GDP per capita for a country/year, falling back to previous year."""
    wb = load_nominal_gdp_per_capita()
    if wb.empty:
        return None
    row = wb[(wb["iso_code"] == iso_code) & (wb["year"] == year)]
    if not row.empty:
        return int(row.iloc[0]["gdp_per_capita_nominal"])
    # Fallback: try year-1
    row = wb[(wb["iso_code"] == iso_code) & (wb["year"] == year - 1)]
    if not row.empty:
        return int(row.iloc[0]["gdp_per_capita_nominal"])
    return None

# Year range
START_YEAR = 2001
END_YEAR = 2023

# Country mappings
# HDI cache path
HDI_CACHE = os.path.join(CACHE_DIR, "undp_hdi_scores.csv")
_hdi_df = None


def load_hdi_data():
    """Load (and download if missing/stale) HDI scores from UNDP HDR Data API.
    Endpoint: https://hdrdata.org/api/CompositeIndices/query
    Cached as CSV; refreshed if older than 30 days.
    """
    global _hdi_df
    if _hdi_df is not None:
        return _hdi_df

    need_download = True
    if os.path.exists(HDI_CACHE):
        age_days = (time.time() - os.path.getmtime(HDI_CACHE)) / 86400
        if age_days < 30:
            need_download = False

    if need_download:
        try:
            api_key = os.environ.get("HDR_API_KEY", "")
            if not api_key:
                # Try loading from .env file directly
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                if os.path.exists(env_path):
                    with open(env_path) as f:
                        for line in f:
                            if line.strip().startswith("HDR_API_KEY="):
                                api_key = line.strip().split("=", 1)[1]
                                break
            if not api_key:
                print("[data_utils] HDR_API_KEY not found, using cached HDI data")
                if os.path.exists(HDI_CACHE):
                    need_download = False
                else:
                    _hdi_df = pd.DataFrame(columns=["iso_code", "hdi"])
                    return _hdi_df

            if need_download:
                url = (
                    f"https://hdrdata.org/api/CompositeIndices/query"
                    f"?apikey={api_key}&year=2023&indicator=hdi"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = json.loads(resp.read().decode())

                rows = []
                for entry in raw:
                    iso = entry["country"].split(" - ")[0].strip()
                    val = entry.get("value")
                    if iso and val:
                        rows.append({"iso_code": iso, "hdi": float(val)})
                hdi_df = pd.DataFrame(rows)
                os.makedirs(CACHE_DIR, exist_ok=True)
                hdi_df.to_csv(HDI_CACHE, index=False)
                print(f"[data_utils] Downloaded {len(hdi_df)} HDI scores from UNDP HDR")
        except Exception as e:
            print(f"[data_utils] HDI download failed: {e}")
            if not os.path.exists(HDI_CACHE):
                _hdi_df = pd.DataFrame(columns=["iso_code", "hdi"])
                return _hdi_df

    _hdi_df = pd.read_csv(HDI_CACHE)
    return _hdi_df


def get_hdi_score(iso_code):
    """Return HDI score for a country ISO code."""
    hdi = load_hdi_data()
    if hdi.empty:
        return None
    row = hdi[hdi["iso_code"] == iso_code]
    if not row.empty:
        return float(row.iloc[0]["hdi"])
    return None

TIER_COMPARISONS = {
    "EGY": {
        "peers": ["IND", "MAR", "PAK", "IDN"],
        "regional": ["SAU", "ZAF", "IRN", "IRQ", "Africa"],
        "responsibility": ["USA", "CHN", "DEU"],
    },
    "IND": {
        "peers": ["EGY", "IDN", "PAK", "BGD"],
        "regional": ["BGD", "NPL", "LKA", "Asia"],
        "responsibility": ["USA", "DEU", "JPN"],
    },
    "SAU": {
        "peers": ["EGY", "ARE", "KWT", "QAT"],
        "regional": ["EGY", "IRN", "IRQ", "Middle East"],
        "responsibility": ["USA", "DEU", "AUS"],
    },
}


def load_data():
    """Load cached OWID data"""
    if os.path.exists(OWID_CACHE):
        return pd.read_csv(OWID_CACHE)
    return None


def get_country_data(df, country_code, year_range=None):
    """Get data for a specific country"""
    if year_range is None:
        year_range = (START_YEAR, END_YEAR)

    if df is None:
        df = load_data()

    data = df[(df["iso_code"] == country_code) | (df["country"] == country_code)].copy()

    data = data[
        (data["year"] >= year_range[0]) & (data["year"] <= year_range[1])
    ].sort_values("year")

    return data


def get_all_countries(df=None):
    """Get list of all countries"""
    if df is None:
        df = load_data()

    if df is None:
        return []

    # Get 2022 GDP data as fallback for countries missing 2023 GDP
    gdp_2022 = df[df["year"] == 2022][["iso_code", "gdp"]].drop_duplicates("iso_code")
    gdp_2022_map = dict(zip(gdp_2022["iso_code"], gdp_2022["gdp"]))

    countries = (
        df[
            (df["year"] == END_YEAR)
            & (df["iso_code"].notna())
            & (df["iso_code"].str.len() == 3)
        ][
            [
                "country",
                "iso_code",
                "gdp",
                "co2",
                "co2_per_capita",
                "share_global_co2",
                "total_ghg_excluding_lucf",
                "ghg_excluding_lucf_per_capita",
                "population",
            ]
        ]
        .drop_duplicates()
        .sort_values("country")
    )

    result = []
    for _, r in countries.iterrows():
        gdp = r["gdp"] if pd.notna(r["gdp"]) else None
        if gdp is None and r["iso_code"] in gdp_2022_map:
            gdp = gdp_2022_map[r["iso_code"]]

        result.append(
            {
                "name": r["country"],
                "iso": r["iso_code"],
                "gdp": float(gdp) if gdp is not None else None,
                "co2": float(r["co2"]) if pd.notna(r["co2"]) else None,
                "co2_per_capita": float(r["co2_per_capita"])
                if pd.notna(r["co2_per_capita"])
                else None,
                "share_global_co2": float(r["share_global_co2"])
                if pd.notna(r["share_global_co2"])
                else None,
                "ghg": float(r["total_ghg_excluding_lucf"])
                if pd.notna(r["total_ghg_excluding_lucf"])
                else None,
                "ghg_per_capita": float(r["ghg_excluding_lucf_per_capita"])
                if pd.notna(r["ghg_excluding_lucf_per_capita"])
                else None,
                "population": float(r["population"])
                if pd.notna(r["population"])
                else None,
            }
        )

    return result


def get_country_summary(country_code, year=None, df=None):
    """Get summary statistics for a country"""
    if df is None:
        df = load_data()

    data = get_country_data(df, country_code)

    if data.empty:
        return {}

    if year is None:
        year = END_YEAR

    row = data[data["year"] == year]
    if row.empty:
        row = data.iloc[-1:]
        year = int(row["year"].values[0])

    if row.empty:
        return {}

    r = row.iloc[0]

    # Get global stats
    global_data = df[(df["country"] == "World") & (df["year"] == year)]
    global_row = global_data.iloc[0] if not global_data.empty else None

    # Calculate change since 2005
    base_year_data = data[data["year"] == START_YEAR]
    base_co2 = (
        base_year_data["co2"].values[0]
        if not base_year_data.empty and pd.notna(base_year_data["co2"].values[0])
        else None
    )
    current_co2 = float(r["co2"]) if pd.notna(r.get("co2")) else None
    co2_change = (
        ((current_co2 - base_co2) / base_co2 * 100) if base_co2 and current_co2 else 0
    )

    # Calculate global rank
    year_data = df[df["year"] == year].copy()
    year_data = year_data[
        year_data["iso_code"].notna() & (year_data["iso_code"].str.len() == 3)
    ]
    year_data = year_data[pd.notna(year_data["co2"])].sort_values(
        "co2", ascending=False
    )
    year_data["rank"] = range(1, len(year_data) + 1)
    global_rank = (
        int(year_data[year_data["iso_code"] == country_code]["rank"].values[0])
        if not year_data[year_data["iso_code"] == country_code].empty
        else None
    )

    summary = {
        "country_code": country_code,
        "country_name": r["country"],
        "year": year,
        "co2_total": current_co2,
        "co2_per_capita": float(r["co2_per_capita"])
        if pd.notna(r.get("co2_per_capita"))
        else None,
        "share_global_co2": float(r["share_global_co2"])
        if pd.notna(r.get("share_global_co2"))
        else None,
        "ghg_total": float(r["total_ghg_excluding_lucf"])
        if pd.notna(r.get("total_ghg_excluding_lucf"))
        else None,
        "ghg_per_capita": float(r["ghg_excluding_lucf_per_capita"])
        if pd.notna(r.get("ghg_excluding_lucf_per_capita"))
        else None,
        "gdp": float(r["gdp"]) if pd.notna(r.get("gdp")) else None,
        "population": float(r["population"]) if pd.notna(r.get("population")) else None,
        "global_co2_total": float(global_row["co2"])
        if global_row is not None and pd.notna(global_row.get("co2"))
        else None,
        "global_co2_per_capita": float(global_row["co2_per_capita"])
        if global_row is not None and pd.notna(global_row.get("co2_per_capita"))
        else None,
        "co2_change": round(co2_change, 2),
        "global_rank": global_rank,
    }

    if summary["co2_per_capita"] and summary["global_co2_per_capita"]:
        diff = summary["co2_per_capita"] - summary["global_co2_per_capita"]
        summary["vs_global_per_capita"] = diff / summary["global_co2_per_capita"] * 100

    # GDP per capita — use World Bank nominal (current US$)
    nominal_pc = get_nominal_gdp_pc(country_code, year)
    if nominal_pc is not None:
        summary["gdp_per_capita"] = nominal_pc
    elif summary["gdp"] and summary["population"] and summary["gdp"] > 0:
        # Fallback to OWID PPP GDP / population
        summary["gdp_per_capita"] = round(summary["gdp"] / summary["population"])
    else:
        summary["gdp_per_capita"] = None

    # Use cumulative_co2 from OWID data if available, otherwise calculate
    if pd.notna(r.get("cumulative_co2")):
        summary["co2_cumulative"] = float(r["cumulative_co2"])
    else:
        cumulative = data["co2"].fillna(0).sum()
        summary["co2_cumulative"] = round(cumulative, 2)

    return summary


def calculate_trend_stats(country_code, metric="co2", df=None):
    """Calculate trend statistics"""
    if df is None:
        df = load_data()

    data = get_country_data(df, country_code)

    if data.empty:
        return {}

    values = data[metric].fillna(0).values
    years = data["year"].values

    # Linear regression
    if len(values) > 1:
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        slope = coeffs[0]
        trend = "increasing" if slope > 0 else "decreasing"
    else:
        slope = 0
        trend = "stable"

    # Overall change
    if len(values) >= 2 and values[0] != 0:
        overall = ((values[-1] - values[0]) / values[0]) * 100
    else:
        overall = 0

    return {
        "years": [int(y) for y in years],
        "values": [float(v) for v in values],
        "overall_change_pct": float(overall),
        "trend_direction": trend,
    }


def get_comparison_data(
    country_code, comparison_codes=None, df=None, tier=None, year=None
):
    """Get comparison data for multiple countries.
    If tier is provided, looks up the tier in TIER_COMPARISONS.
    If year is provided, returns data for that specific year.
    """
    if df is None:
        df = load_data()

    if year is None:
        year = END_YEAR

    if tier:
        tier_map = TIER_COMPARISONS.get(country_code, {})
        comparison_codes = tier_map.get(tier, tier_map.get("peers", []))

    if comparison_codes is None:
        comparison_codes = []

    all_codes = [country_code] + comparison_codes
    countries = []

    world_row = (
        df[(df["country"] == "World") & (df["year"] == year)].iloc[-1]
        if not df[(df["country"] == "World") & (df["year"] == year)].empty
        else None
    )
    world_co2 = (
        float(world_row["co2"])
        if world_row is not None and pd.notna(world_row.get("co2"))
        else None
    )

    for code in all_codes:
        data = get_country_data(df, code)

        if not data.empty:
            year_data = data[data["year"] == year]

            if year_data.empty:
                year_data = data.iloc[[-1]]

            co2_row = year_data.iloc[-1]

            gdp_data = data[(data["gdp"].notna()) & (data["gdp"] > 0)]
            gdp_year_data = gdp_data[gdp_data["year"] == year]
            gdp_row = (
                gdp_year_data.iloc[-1]
                if not gdp_year_data.empty
                else (gdp_data.iloc[-1] if not gdp_data.empty else None)
            )

            co2_val = float(co2_row["co2"]) if pd.notna(co2_row.get("co2")) else 0
            gdp_val = float(gdp_row["gdp"]) if gdp_row is not None else 0
            population_val = (
                float(co2_row["population"])
                if pd.notna(co2_row.get("population"))
                else 0
            )

            carbon_intensity = (co2_val / (gdp_val / 1e9)) if gdp_val > 0 else None

            share = co2_row.get("share_global_co2")
            share_global = float(share) if pd.notna(share) else None

            pc = co2_row.get("co2_per_capita")
            co2_per_capita = float(pc) if pd.notna(pc) else 0

            hdi_adjusted = None
            hdi_score = get_hdi_score(code)
            if co2_per_capita and hdi_score:
                hdi_adjusted = round(co2_per_capita / hdi_score, 3)

            ghg_val = (
                float(co2_row["total_ghg_excluding_lucf"])
                if pd.notna(co2_row.get("total_ghg_excluding_lucf"))
                else 0
            )
            ghg_pc = co2_row.get("ghg_excluding_lucf_per_capita")
            ghg_per_capita = float(ghg_pc) if pd.notna(ghg_pc) else 0

            # Use World Bank nominal GDP per capita (current US$)
            iso = co2_row.get("iso_code", code)
            gdp_per_capita_val = get_nominal_gdp_pc(iso if iso and len(str(iso)) == 3 else code, year)

            countries.append(
                {
                    "code": code,
                    "name": co2_row["country"],
                    "year": int(co2_row["year"])
                    if pd.notna(co2_row.get("year"))
                    else year,
                    "co2": co2_val,
                    "co2_per_capita": co2_per_capita,
                    "share_global_co2": share_global,
                    "ghg": ghg_val,
                    "ghg_per_capita": ghg_per_capita,
                    "hdi": get_hdi_score(code),
                    "hdi_adjusted": hdi_adjusted,
                    "gdp": gdp_val if gdp_val > 0 else None,
                    "gdp_per_capita": gdp_per_capita_val,
                    "population": population_val if population_val > 0 else None,
                    "carbon_intensity": round(carbon_intensity, 3)
                    if carbon_intensity
                    else None,
                    "all_years": data["year"].tolist(),
                    "all_co2": data["co2"].fillna(0).tolist(),
                    "all_co2_per_capita": data["co2_per_capita"].fillna(0).tolist(),
                }
            )

    return {
        "primary_country": country_code,
        "comparison_countries": comparison_codes,
        "tier": tier,
        "year": year,
        "countries": countries,
    }


def get_emission_sources(country_code, year=None, df=None):
    """Get emission sources breakdown"""
    if df is None:
        df = load_data()

    if year is None:
        year = END_YEAR

    data = get_country_data(df, country_code)

    if data.empty:
        return {}

    row = data[data["year"] == year]
    if row.empty:
        row = data.iloc[-1]

    r = row.iloc[0]

    def build_row_dict(r_row):
        return {
            "year": int(r_row["year"]),
            "total_co2": float(r_row["co2"]) if pd.notna(r_row.get("co2")) else 0,
            "coal_co2": float(r_row["coal_co2"]) if pd.notna(r_row.get("coal_co2")) else 0,
            "oil_co2": float(r_row["oil_co2"]) if pd.notna(r_row.get("oil_co2")) else 0,
            "gas_co2": float(r_row["gas_co2"]) if pd.notna(r_row.get("gas_co2")) else 0,
            "cement_co2": float(r_row["cement_co2"]) if pd.notna(r_row.get("cement_co2")) else 0,
            "flaring_co2": float(r_row["flaring_co2"]) if pd.notna(r_row.get("flaring_co2")) else 0,
            "total_ghg_excluding_lucf": float(r_row["total_ghg_excluding_lucf"])
            if pd.notna(r_row.get("total_ghg_excluding_lucf"))
            else 0,
            "methane": float(r_row["methane"]) if pd.notna(r_row.get("methane")) else 0,
            "nitrous_oxide": float(r_row["nitrous_oxide"])
            if pd.notna(r_row.get("nitrous_oxide"))
            else 0,
            "land_use_change_co2": float(r_row["land_use_change_co2"])
            if pd.notna(r_row.get("land_use_change_co2"))
            else 0,
        }

    latest_data = build_row_dict(r)
    latest_data["country_code"] = country_code
    
    historical = []
    # Filter for the relevant years
    hist_data = data[(data["year"] >= START_YEAR) & (data["year"] <= (year if year != END_YEAR else END_YEAR))]
    for _, h_row in hist_data.iterrows():
        historical.append(build_row_dict(h_row))
    
    latest_data["historical"] = historical
    return latest_data


# Global data cache for Flask app
_data = None


def get_data():
    """Get cached data frame (singleton)"""
    global _data
    if _data is None:
        _data = load_data()
    return _data
