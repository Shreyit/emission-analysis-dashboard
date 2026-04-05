"""
AI Service Module - OpenRouter Integration
Uses free tier models via OpenRouter API
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip()  # Remove any whitespace

# Model to use (free tier)
DEFAULT_MODEL = "liquid/lfm-2.5-1.2b-instruct-20260120:free"

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 2.0  # seconds between requests


def generate_content(
    prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.7
) -> str:
    """Generate content using OpenRouter API"""

    if not OPENROUTER_API_KEY:
        return "Error: No API key configured"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    global last_request_time
    elapsed = time.time() - last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=temperature,
        )
        last_request_time = time.time()
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def generate_emissions_insight(
    country_name: str, trend_data: dict, summary_data: dict, phase_context: dict = None
) -> str:
    """Generate AI insight for emissions trend"""

    phase_block = ""
    if phase_context:
        phase_block = f"""FOCUS: Analyse specifically the {phase_context.get("phase", "full")} period ({phase_context.get("years", "")}).
CAGR during this period: {phase_context.get("cagr", "N/A")}/yr.
Key driver: {phase_context.get("driver", "N/A")}.
Explain what caused this specific trend, what the data shows within this period,
and what it implies for Egypt's emissions trajectory. Be specific to this period,
not the full 2000-2023 range.

"""

    prompt = f"""{phase_block}Analyze the CO2 emissions trend for {country_name}:

TREND DATA:
- Years: {trend_data.get("years", [])}
- CO2 Values (Mt): {[round(v, 1) for v in trend_data.get("values", [])]}
- Overall change: {trend_data.get("overall_change_pct", "N/A")}%
- Trend direction: {trend_data.get("trend_direction", "N/A")}

SUMMARY:
- Total CO2: {summary_data.get("co2_total", "N/A")} Mt
- Per capita CO2: {summary_data.get("co2_per_capita", "N/A")} tonnes
- Share of global: {summary_data.get("share_global_co2", "N/A")}%

Provide a concise analysis (150-200 words) covering:
1. Key trends observed
2. Possible drivers (economic, policy, events)
3. What this means for the country's climate responsibility

Use only the data provided. Be specific with numbers."""

    return generate_content(prompt)


def generate_comparison_insight(country_name: str, comparison_data: dict) -> str:
    """Generate AI insight for country comparison"""

    countries_info = []
    for c in comparison_data.get("countries", []):
        countries_info.append(
            f"- {c['name']}: {c.get('co2_per_capita', 'N/A')} t/capita"
        )

    countries_str = "\n".join(countries_info)

    prompt = f"""Compare per capita CO2 emissions for {country_name}:

COUNTRIES:
{countries_str}

GLOBAL AVERAGE: {comparison_data.get("global_stats", {}).get("co2_per_capita", "N/A")} t/capita

Provide a concise analysis (150-200 words) covering:
1. How {country_name} compares to other countries
2. Carbon inequality implications
3. Climate responsibility considerations

Be specific with numbers and comparisons."""

    return generate_content(prompt)


def generate_climate_reflection(
    country_name: str, summary_data: dict, comparison_data: dict
) -> str:
    """Generate climate justice reflection (200-300 words)"""

    prompt = f"""Write a climate justice reflection (200-300 words) for {country_name}:

KEY DATA:
- Total CO2 emissions: {summary_data.get("co2_total", "N/A")} Mt
- Per capita emissions: {summary_data.get("co2_per_capita", "N/A")} t
- Share of global emissions: {summary_data.get("share_global_co2", "N/A")}%
- Global average per capita: {summary_data.get("global_co2_per_capita", "N/A")} t
- vs Global average: {summary_data.get("vs_global_per_capita", "N/A")}%
- Population: {summary_data.get("population", "N/A"):,.0f}

Address:
1. What role should {country_name} play in global climate mitigation?
2. How does its development level affect responsibility?
3. What obligations do higher emitters have?

Use evidence from the data. Be balanced and nuanced."""

    return generate_content(prompt, temperature=0.8)


def generate_sources_insight(
    country_name: str, sources_data: dict, mode: str = "co2"
) -> str:
    """Generate insight for emission sources breakdown"""

    mode_label = "GHG (CO₂e)" if mode == "non-co2" else "CO₂"

    if mode == "non-co2":
        total_co2 = sources_data.get("total_co2", 0)
        co2_sources = sum(
            [
                sources_data.get("gas_co2", 0),
                sources_data.get("oil_co2", 0),
                sources_data.get("coal_co2", 0),
                sources_data.get("cement_co2", 0),
                sources_data.get("flaring_co2", 0),
            ]
        )
        total_ghg = sources_data.get("total_ghg_excluding_lucf", 0)
        non_co2 = max(0, total_ghg - co2_sources)
        methane = sources_data.get("methane", 0)
        nitrous_oxide = sources_data.get("nitrous_oxide", 0)

        sources_list = []
        if sources_data.get("gas_co2"):
            sources_list.append(f"- Gas: {sources_data.get('gas_co2', 0):.1f} Mt")
        if sources_data.get("oil_co2"):
            sources_list.append(f"- Oil: {sources_data.get('oil_co2', 0):.1f} Mt")
        if sources_data.get("coal_co2"):
            sources_list.append(f"- Coal: {sources_data.get('coal_co2', 0):.1f} Mt")
        if sources_data.get("cement_co2"):
            sources_list.append(f"- Cement: {sources_data.get('cement_co2', 0):.1f} Mt")
        if sources_data.get("flaring_co2"):
            sources_list.append(
                f"- Flaring: {sources_data.get('flaring_co2', 0):.1f} Mt"
            )
        if methane > 0:
            sources_list.append(f"- Methane (CH₄): {methane:.1f} Mt CO₂e")
        if nitrous_oxide > 0:
            sources_list.append(f"- N₂O: {nitrous_oxide:.1f} Mt CO₂e")

        sources_str = "\n".join(sources_list) if sources_list else "Data not available"

        prompt = f"""Analyze the GHG emissions for {country_name} (Total: {total_ghg:.1f} Mt CO₂e):

SOURCES (CO₂ sources: {co2_sources:.1f} Mt, Non-CO₂: {non_co2:.1f} Mt):
{sources_str}

Provide a concise analysis (150-200 words) covering:
1. Share of CO₂ vs non-CO₂ greenhouse gases
2. Role of methane (CH₄) and nitrous oxide (N₂O) in total emissions
3. What this reveals about the energy and agricultural sectors
4. Implications for climate mitigation strategies

Be specific with percentages and sources."""
    else:
        sources_list = []
        total = sources_data.get("total_co2", 0)
        if sources_data.get("gas_co2"):
            sources_list.append(
                f"- Gas: {sources_data.get('gas_co2', 0):.1f} Mt ({sources_data.get('gas_co2', 0) / total * 100:.1f}%)"
            )
        if sources_data.get("oil_co2"):
            sources_list.append(
                f"- Oil: {sources_data.get('oil_co2', 0):.1f} Mt ({sources_data.get('oil_co2', 0) / total * 100:.1f}%)"
            )
        if sources_data.get("coal_co2"):
            sources_list.append(
                f"- Coal: {sources_data.get('coal_co2', 0):.1f} Mt ({sources_data.get('coal_co2', 0) / total * 100:.1f}%)"
            )
        if sources_data.get("cement_co2"):
            sources_list.append(f"- Cement: {sources_data.get('cement_co2', 0):.1f} Mt")
        if sources_data.get("flaring_co2"):
            sources_list.append(
                f"- Flaring: {sources_data.get('flaring_co2', 0):.1f} Mt"
            )

        sources_str = "\n".join(sources_list) if sources_list else "Data not available"

        prompt = f"""Analyze the CO₂ emission sources for {country_name} (Total: {total:.1f} Mt):

SOURCES:
{sources_str}

Provide a concise analysis (150-200 words) covering:
1. Dominant emission sources (what fuel mix?)
2. What this reveals about the energy economy
3. Implications for decarbonization strategies

Be specific with percentages and sources."""

    return generate_content(prompt)
