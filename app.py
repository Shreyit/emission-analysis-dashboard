"""
Emission Trend Analysis - Flask Web Application
Uses OWID data for CO2 emissions analysis
"""

import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import simple data module
from data_utils import (
    get_data,
    get_all_countries,
    get_country_summary,
    calculate_trend_stats,
    get_comparison_data,
    get_emission_sources,
)

# Import AI service
from ai_service import (
    generate_emissions_insight,
    generate_comparison_insight,
    generate_climate_reflection,
    generate_sources_insight,
)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-emission-analysis")

# Pre-load data
_data = get_data()


@app.route("/")
def index():
    """Main dashboard page"""
    country = request.args.get("country", "EGY")
    countries_list = get_all_countries(_data)
    countries_dict = {c["iso"]: c["name"] for c in countries_list}
    return render_template(
        "index.html",
        default_country=country,
        countries=countries_list,
        countries_dict=countries_dict,
    )


@app.route("/api/countries")
def api_countries():
    """Get all available countries"""
    return jsonify(get_all_countries(_data))


@app.route("/api/summary/<country_code>")
def api_summary(country_code):
    """Get country summary data"""
    summary = get_country_summary(country_code.upper(), df=_data)
    return jsonify(summary)


@app.route("/api/trend/<country_code>")
def api_trend(country_code):
    """Get trend data for a country"""
    country_code = country_code.upper()
    mode = request.args.get("mode", "co2")

    if mode == "ghg":
        total_metric = "total_ghg_excluding_lucf"
        per_capita_metric = "ghg_excluding_lucf_per_capita"
    else:
        total_metric = "co2"
        per_capita_metric = "co2_per_capita"

    total_trend = calculate_trend_stats(country_code, total_metric, _data)
    per_capita_trend = calculate_trend_stats(country_code, per_capita_metric, _data)
    return jsonify({"total": total_trend, "per_capita": per_capita_trend})


@app.route("/api/comparison/<country_code>")
def api_comparison(country_code):
    """Get comparison data for a country.
    Query param ?tier=peers|regional|responsibility
    Query param ?year=2023 (default)
    """
    tier = request.args.get("tier", None)
    year = request.args.get("year", 2023, type=int)
    comp_data = get_comparison_data(
        country_code.upper(), df=_data, tier=tier, year=year
    )
    return jsonify(comp_data)


@app.route("/api/emission-sources/<country_code>")
def api_emission_sources(country_code):
    """Get emission sources breakdown"""
    sources = get_emission_sources(country_code.upper(), df=_data)
    return jsonify(sources)


@app.route("/api/ai/trend/<country_code>", methods=["GET", "POST"])
def api_ai_trend(country_code):
    """Get AI-generated emissions trend insight"""
    country_code = country_code.upper()
    phase_context = {}
    if request.method == "POST":
        phase_context = request.get_json() or {}
    summary = get_country_summary(country_code, df=_data)
    trend = calculate_trend_stats(country_code, "co2", _data)
    country_name = summary.get("country_name", country_code)
    insight = generate_emissions_insight(
        country_name, trend, summary, phase_context=phase_context
    )
    return jsonify({"insight": insight})


@app.route("/api/ai/comparison/<country_code>")
def api_ai_comparison(country_code):
    """Get AI-generated comparison insight"""
    country_code = country_code.upper()
    tier = request.args.get("tier", None)
    comp_data = get_comparison_data(country_code, df=_data, tier=tier)
    summary = get_country_summary(country_code, df=_data)
    country_name = summary.get("country_name", country_code)
    insight = generate_comparison_insight(country_name, comp_data)
    return jsonify({"insight": insight})


@app.route("/api/ai/sources/<country_code>")
def api_ai_sources(country_code):
    """Get AI-generated sources insight"""
    country_code = country_code.upper()
    mode = request.args.get("mode", "co2")
    sources = get_emission_sources(country_code, df=_data)
    summary = get_country_summary(country_code, df=_data)
    country_name = summary.get("country_name", country_code)
    insight = generate_sources_insight(country_name, sources, mode)
    return jsonify({"insight": insight})


@app.route("/api/ai/reflection/<country_code>")
def api_ai_reflection(country_code):
    """Get AI-generated climate justice reflection"""
    country_code = country_code.upper()
    summary = get_country_summary(country_code, df=_data)
    comparisons = {
        "EGY": ["IND", "SAU", "WLD"],
        "IND": ["EGY", "CHN", "USA", "WLD"],
        "SAU": ["EGY", "ARE", "WLD"],
    }
    comp_list = comparisons.get(country_code, ["WLD"])
    comp_data = get_comparison_data(country_code, comp_list, _data)
    country_name = summary.get("country_name", country_code)
    reflection = generate_climate_reflection(country_name, summary, comp_data)
    return jsonify({"reflection": reflection})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
