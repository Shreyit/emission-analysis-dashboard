"""
Simple Data Module for Flask App
Loads cached OWID data and provides basic analysis functions
"""

import os
import json
import pandas as pd
import numpy as np

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "cache")
OWID_CACHE = os.path.join(CACHE_DIR, "owid_emissions.csv")

# Year range
START_YEAR = 2001
END_YEAR = 2023

# Country mappings
HDI_SCORES = {
    "EGY": 0.731,
    "IND": 0.645,
    "MAR": 0.683,
    "PAK": 0.540,
    "IDN": 0.713,
    "SAU": 0.875,
    "ZAF": 0.709,
    "IRN": 0.788,
    "IRQ": 0.685,
    "USA": 0.926,
    "CHN": 0.768,
    "DEU": 0.950,
    "BGD": 0.661,
    "NPL": 0.667,
    "LKA": 0.780,
    "ARE": 0.911,
    "KWT": 0.869,
    "QAT": 0.855,
    "JPN": 0.920,
    "AUS": 0.946,
    "GBR": 0.940,
    "FRA": 0.910,
    "TUR": 0.838,
    "BRA": 0.760,
    "RUS": 0.822,
    "CAN": 0.935,
    "NGA": 0.548,
    "WLD": 0.780,
}

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

    # Calculate gdp_per_capita — use latest year with GDP if current year is NaN
    # OWID uses PPP, but we want nominal USD for display
    # Add hardcoded nominal GDP per capita for key countries (World Bank current USD)
    nominal_gdp_per_capita_fallback = {
        "EGY": {2022: 4233, 2023: 3457},  # Egypt nominal USD
        "IND": {2022: 2388, 2023: 2484},
        "SAU": {2022: 30436, 2023: 32586},
    }

    # Check if we have a fallback for this country
    country_fallback = nominal_gdp_per_capita_fallback.get(country_code, {})

    if summary["gdp"] and summary["population"] and summary["gdp"] > 0:
        # Use OWID GDP/pop for now - shows PPP value
        summary["gdp_per_capita"] = summary["gdp"] / summary["population"]
    elif pd.notna(r.get("gdp_per_capita")):
        summary["gdp_per_capita"] = float(r["gdp_per_capita"])
    else:
        gdp_data = data[data["gdp"].notna() & (data["gdp"] > 0)]
        if not gdp_data.empty:
            latest_gdp_row = gdp_data.iloc[-1]
            summary["gdp"] = float(latest_gdp_row["gdp"])
            summary["year"] = int(latest_gdp_row["year"])
            if summary["population"] and summary["population"] > 0:
                summary["gdp_per_capita"] = summary["gdp"] / summary["population"]
        else:
            summary["gdp_per_capita"] = None

    # Override with nominal USD value if available in fallback
    if summary.get("year") and country_code in nominal_gdp_per_capita_fallback:
        year = int(summary.get("year", 2022))
        # Use 2023 value if available, otherwise fall back to 2022
        if 2023 in country_fallback:
            summary["gdp_per_capita"] = country_fallback[2023]
            summary["gdp_per_capita_year"] = 2023
        elif year in country_fallback:
            summary["gdp_per_capita"] = country_fallback[year]
            summary["gdp_per_capita_year"] = year

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
            if co2_per_capita and code in HDI_SCORES:
                hdi_adjusted = round(co2_per_capita / HDI_SCORES[code], 3)

            ghg_val = (
                float(co2_row["total_ghg_excluding_lucf"])
                if pd.notna(co2_row.get("total_ghg_excluding_lucf"))
                else 0
            )
            ghg_pc = co2_row.get("ghg_excluding_lucf_per_capita")
            ghg_per_capita = float(ghg_pc) if pd.notna(ghg_pc) else 0

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
                    "hdi": HDI_SCORES.get(code),
                    "hdi_adjusted": hdi_adjusted,
                    "gdp": gdp_val if gdp_val > 0 else None,
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

    return {
        "country_code": country_code,
        "year": int(r["year"]),
        "total_co2": float(r["co2"]) if pd.notna(r.get("co2")) else 0,
        "coal_co2": float(r["coal_co2"]) if pd.notna(r.get("coal_co2")) else 0,
        "oil_co2": float(r["oil_co2"]) if pd.notna(r.get("oil_co2")) else 0,
        "gas_co2": float(r["gas_co2"]) if pd.notna(r.get("gas_co2")) else 0,
        "cement_co2": float(r["cement_co2"]) if pd.notna(r.get("cement_co2")) else 0,
        "flaring_co2": float(r["flaring_co2"]) if pd.notna(r.get("flaring_co2")) else 0,
        "total_ghg_excluding_lucf": float(r["total_ghg_excluding_lucf"])
        if pd.notna(r.get("total_ghg_excluding_lucf"))
        else 0,
        "methane": float(r["methane"]) if pd.notna(r.get("methane")) else 0,
        "nitrous_oxide": float(r["nitrous_oxide"])
        if pd.notna(r.get("nitrous_oxide"))
        else 0,
        "land_use_change_co2": float(r["land_use_change_co2"])
        if pd.notna(r.get("land_use_change_co2"))
        else 0,
    }


# Global data cache for Flask app
_data = None


def get_data():
    """Get cached data frame (singleton)"""
    global _data
    if _data is None:
        _data = load_data()
    return _data
