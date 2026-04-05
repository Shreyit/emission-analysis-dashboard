# Code Explanation Document

## Emission Trend Analysis - Backend Code Walkthrough

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Data Source: OWID Dataset](#2-data-source-owid-dataset)
3. [Module 1: fetch_data.ipynb](#3-module-1-fetch_dataipynb)
4. [Module 2: analysis.ipynb](#4-module-2-analysisipynb)
5. [Module 3: countries.ipynb](#5-module-3-countriesipynb)
6. [Data Flow Diagram](#6-data-flow-diagram)
7. [Key Variables for Dashboard](#7-key-variables-for-dashboard)
8. [Robustness Features](#8-robustness-features)
9. [Recommendations for Enhancement](#9-recommendations-for-enhancement)
10. [Flask API Architecture](#10-flask-api-architecture)
11. [AI Service Integration](#11-ai-service-integration)
12. [Frontend Logic & Visualizations](#12-frontend-logic--visualizations)
13. [CO2/GHG Toggle Logic](#13-co2ghg-toggle-logic)
14. [Year Filter Implementation](#14-year-filter-implementation)
15. [Tier Comparison System](#15-tier-comparison-system)
16. [Color System & Theming](#16-color-system--theming)
17. [Global Context Panel](#17-global-context-panel)

---

## 1. Project Overview

This project analyzes CO₂ emissions trends for countries worldwide using data from OWID (Our World in Data). The backend consists of three Jupyter notebooks that form a modular data pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│   │fetch_data    │───▶│  analysis    │───▶│ countries    ││
│   │  .ipynb      │    │  .ipynb      │    │  .ipynb      ││
│   └──────────────┘    └──────────────┘    └──────────────┘│
│         │                   │                    │         │
│         ▼                   ▼                    ▼         │
│   OWID GitHub CSV      Statistical          Configuration  │
│   + Local Cache        Calculations         & Metadata     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Purpose:** Provide data fetching, statistical analysis, and country configuration for an interactive Voila dashboard analyzing CO₂ emissions and climate justice.

---

## 2. Data Source: OWID Dataset

### What is OWID?

[Our World in Data (OWID)](https://github.com/owid/co2-data) aggregates CO₂ and greenhouse gas data from multiple authoritative sources:

| Source | Data Provided |
|--------|---------------|
| **Global Carbon Project** | CO₂ emissions (fossil fuels, industry) |
| **UNFCCC** | Greenhouse gas inventories |
| **World Bank** | Economic data (GDP, population) |
| **BP Statistical Review** | Energy consumption data |

### Dataset Structure

| Property | Value |
|----------|-------|
| Total Rows | ~50,000+ |
| Year Range | 1750 - 2023 |
| Countries/Regions | 200+ |
| Total Columns | ~80 variables |

### Key Variable Categories

#### A. Core Emissions Metrics (PRIMARY)
| Variable | Description | Unit | Dashboard Use |
|----------|-------------|------|---------------|
| `co2` | Total CO₂ emissions | Million tonnes (Mt) | Line chart, metric card |
| `co2_per_capita` | Per person emissions | Tonnes/person | Comparison chart, metric |
| `co2_growth_abs` | Absolute YoY change | Mt | Year-over-year analysis |
| `co2_growth_prct` | Percentage YoY change | % | Period comparison |
| `share_global_co2` | Share of world total | % | Global context |

#### B. Emissions by Source (SECONDARY)
| Variable | Description | Dashboard Use |
|----------|-------------|---------------|
| `coal_co2` | CO₂ from coal combustion | Stacked area chart |
| `oil_co2` | CO₂ from oil combustion | Source breakdown |
| `gas_co2` | CO₂ from gas combustion | Source breakdown |
| `cement_co2` | CO₂ from cement production | Industry analysis |
| `flaring_co2` | CO₂ from gas flaring | Energy sector |

#### C. Consumption-Based Metrics (ADVANCED)
| Variable | Description | Use Case |
|----------|-------------|----------|
| `consumption_co2` | Emissions from consumption (includes trade) | Climate justice analysis |
| `consumption_co2_per_capita` | Consumption-based per capita | Inequality analysis |
| `trade_co2` | Net CO₂ from trade | Shows who imports emissions |

**Why consumption-based matters:** If Egypt imports goods manufactured in China, those emissions count toward China's production-based CO₂ but Egypt's consumption-based CO₂. This is crucial for climate justice arguments.

#### D. Greenhouse Gases (Beyond CO₂)
| Variable | Description |
|----------|-------------|
| `methane` (CH₄) | Agricultural, fossil fuel emissions |
| `nitrous_oxide` (N₂O) | Agricultural, industrial |
| `total_ghg` | All greenhouse gases combined (CO₂e) |
| `ghg_per_capita` | Total GHG per capita |

#### E. Economic & Energy
| Variable | Description | Dashboard Use |
|----------|-------------|---------------|
| `gdp` | Gross Domestic Product (USD) | Economic context |
| `population` | Total population | Scale normalization |
| `primary_energy_consumption` | Total energy use (kWh) | Development indicator |
| `co2_per_gdp` | Emissions intensity | Economic efficiency |
| `energy_per_capita` | Energy per person | Development level |

#### F. Land Use Change (Important for Developing Nations)
| Variable | Description | Significance |
|----------|-------------|---------------|
| `co2_including_luc` | CO₂ including land use change | Full picture |
| `land_use_change_co2` | Deforestation, land use | Often negative for ag. countries |
| `cumulative_co2` | Total historical emissions | Historical responsibility |

#### G. Temperature Impact (For AI Context)
| Variable | Description |
|----------|-------------|
| `temperature_change_from_co2` | Warming contribution from CO₂ |
| `temperature_change_from_ch4` | Warming from methane |
| `total_ghg_excluding_lucf` | GHG excluding land use |

---

## 3. Module 1: fetch_data.ipynb

### Purpose
Handles all data fetching operations from OWID GitHub repository with local caching.

### Architecture

```python
class DataFetcher:
    """
    Main data fetching class for emission analysis
    
    Responsibilities:
    1. Fetch data from OWID GitHub
    2. Cache data locally to CSV
    3. Filter by country and year range
    4. Export data to JSON format
    """
```

### Configuration Constants

```python
OWID_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
START_YEAR = 2005
END_YEAR = 2024
CACHE_DIR = "data/cache/"
```

**Why these years?** 2005 onwards provides consistent data for most countries, including pre/post Arab Spring analysis.

### Key Methods Explained

#### `__init__(use_cache=True)`
```python
def __init__(self, use_cache=True):
    self.use_cache = use_cache  # Toggle caching on/off
    self.owid_df = None       # Store full dataset in memory
```

**Design choice:** Cache is on by default for performance. Set `use_cache=False` to always fetch fresh data.

#### `fetch_owid_data(force_refresh=False)` - The Core Method

```
┌─────────────────────────────────────────────────────────────┐
│                    FETCH DATA FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   START ──▶ Check: use_cache AND cache exists?              │
│                    │                                        │
│         ┌──────────┴──────────┐                            │
│         │ Yes                  │ No                         │
│         ▼                     ▼                            │
│   Load from CSV         Fetch from GitHub                   │
│   (fast, offline)       (requires internet)                │
│         │                     │                             │
│         └──────────┬──────────┘                            │
│                    ▼                                        │
│            Save to cache                                    │
│            (CSV file)                                       │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────┐                               │
│         │ Return DataFrame │                              │
│         │ (ready for use)  │                              │
│         └─────────────────┘                               │
│                                                              │
│   ERROR ──▶ Fallback to cache ──▶ Warn user                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Caching:** Reduces API calls, enables offline use
- **Force refresh:** `force_refresh=True` bypasses cache
- **Error handling:** Falls back to cached data if GitHub fails
- **Memory efficiency:** Stores DataFrame in `self.owid_df`

#### `get_country_data_owid(country_code, year_range=None)` - Filtering

```python
def get_country_data_owid(self, country_code, year_range=None):
    # Dual identification method
    country_data = self.owid_df[
        (self.owid_df["iso_code"] == country_code)   # Match by ISO code
        | (self.owid_df["country"] == country_code)   # OR by country name
    ]
    
    # Apply year filter
    country_data = country_data[
        (country_data["year"] >= year_range[0])
        & (country_data["year"] <= year_range[1])
    ]
    
    return country_data.sort_values("year")
```

**Why dual matching?** OWID data has both `iso_code` and `country` columns. Some entries match better with one or the other.

#### `get_all_countries_owid(year=None)` - Country Discovery

```python
def get_all_countries_owid(self, year=None):
    # Filter for valid countries (have 3-letter ISO codes)
    country_iso = self.owid_df[
        (self.owid_df["year"] == year)            # Must have data for this year
        & (self.owid_df["iso_code"].notna())      # Must have ISO code
        & (self.owid_df["iso_code"].str.len() == 3)  # Must be 3 chars
    ]
    return country_iso.sort_values("country").to_dict("records")
```

**Why 3-character filter?** Excludes aggregate regions like "Africa", "Europe" (they have different naming conventions).

#### `get_comparison_data()` - Multi-Country Data

```python
def get_comparison_data(self, primary_country, comparison_countries, year_range):
    """
    Returns chart-ready dictionary for multiple countries
    Structure optimized for Plotly visualization
    """
    return {
        "EGY": {
            "year": [2005, 2006, ..., 2023],           # X-axis
            "co2": [158.0, 162.5, ..., 249.0],         # Line 1
            "co2_per_capita": [2.3, 2.35, ...],         # Line 2
            "share_global_co2": [0.5, 0.52, ...],        # Pie chart
            "gdp": [...],                               # Scatter X
            "population": [...]                         # Normalization
        },
        "IND": {...},
        "WLD": {...}  # World average
    }
```

#### `get_global_stats(year)` - World Aggregate

```python
def get_global_stats(self, year):
    # Special case: World aggregate row
    global_data = self.owid_df[
        (self.owid_df["country"] == "World") & 
        (self.owid_df["year"] == year)
    ]
```

**Important:** OWID includes a global aggregate with `country = "World"`. This is used for comparison benchmarks.

### Error Handling Strategy

```python
try:
    self.owid_df = pd.read_csv(OWID_URL)
except Exception as e:
    print(f"Error fetching: {e}")
    # Fallback: try cached data even if force_refresh=True
    if os.path.exists(cache_file):
        self.owid_df = pd.read_csv(cache_file)
        print("Recovered from cache")
    else:
        raise  # No data available at all
```

---

## 4. Module 2: analysis.ipynb

### Purpose
Performs statistical calculations and generates metrics for visualization.

### Architecture

```python
class EmissionAnalyzer:
    """
    Statistical analysis for emission data
    
    Capabilities:
    1. Trend analysis (linear regression, YoY changes)
    2. Country summaries (snapshot at a point in time)
    3. Multi-country comparisons
    4. Carbon intensity calculations
    5. Regional averages
    """
```

### Key Methods Explained

#### `calculate_trend_stats(country_code, metric="co2")` - Trend Analysis

This method calculates comprehensive trend statistics for any numeric metric:

```python
def calculate_trend_stats(self, country_code, metric="co2"):
    """
    Returns dictionary with:
    - start_value, end_value (boundary values)
    - min_value, max_value, mean_value
    - overall_change_pct (percentage change over period)
    - trend_direction ("increasing", "decreasing", "stable")
    - trend_slope (linear regression coefficient)
    - yoy_changes (year-over-year percentage changes)
    """
```

**Linear Regression for Trend Direction:**
```python
# Simple linear regression: y = mx + b
values = [158, 162, 170, 180, ...]  # CO2 over years
x = np.arange(len(values))          # [0, 1, 2, ...]
coeffs = np.polyfit(x, values, 1)   # Fit degree-1 polynomial
slope = coeffs[0]                   # e.g., 4.5 = +4.5 Mt per year

trend_direction = "increasing" if slope > 0 else "decreasing"
```

**Year-over-Year (YoY) Calculation:**
```python
# Percentage change between consecutive years
values = np.array([158, 162, 170, 180])
yoy_changes = np.diff(values) / values[:-1] * 100
# Result: [0, 2.53, 5.88] (% change between years)
```

#### `get_country_summary(country_code, year=None)` - Country Snapshot

```python
def get_country_summary(self, country_code, year=None):
    """
    Returns snapshot of country at a point in time:
    - Basic metrics (CO2, per capita, share)
    - Economic data (GDP, population)
    - Global comparison (vs world average)
    - Derived metric: vs_global_per_capita
    """
```

**Derived Metric Example:**
```python
# How many times global average?
summary["vs_global_per_capita"] = (
    summary["co2_per_capita"] / global_stats["co2_per_capita"]
)
# Egypt: 2.47 / 4.70 = 0.53 (53% of global average)
```

**Why this matters for climate justice:** Egypt emits only 53% of the global average per capita, despite being a developing nation with 1.3% of world population but only 0.64% of global CO₂.

#### `calculate_carbon_intensity(country_code)` - Efficiency Metric

```python
def calculate_carbon_intensity(self, country_code):
    """
    Measures CO2 efficiency of economy
    
    Formula: CO2 (Mt) / GDP (million USD)
    Unit: tonnes CO2 per million USD GDP
    
    Lower = more efficient (less carbon per dollar of GDP)
    """
    carbon_intensity = co2_total / (gdp / 1_000_000)
```

**Formula breakdown:**
```python
# Example for Egypt 2023:
CO2 = 249  # Million tonnes
GDP = 302_000_000_000  # $302 billion USD

# Convert GDP to millions
GDP_millions = GDP / 1_000_000  # = 302,000

# Calculate intensity
carbon_intensity = CO2 / GDP_millions  # = 249 / 302,000 = 0.82
# Interpretation: 0.82 tonnes CO2 per $1 million GDP
```

**Why useful?**
- Compares emissions efficiency across countries at different development stages
- Shows decoupling potential (economic growth with emissions control)
- Important for climate justice: developing nations often have higher intensity

#### `get_regional_averages(countries, year)` - Group Statistics

```python
def get_regional_averages(self, countries, year):
    """
    Calculates statistics for a group of countries
    
    Returns: mean, median, std deviation
    Used for: Africa average, Global North average
    """
    for code in countries:
        summary = self.get_country_summary(code, year)
        # Accumulate values
    
    return {
        "co2_avg": np.mean(values),
        "co2_median": np.median(values),
        "co2_std": np.std(values)
    }
```

**Usage for dashboard:**
- "Africa avg" comparison: `get_regional_averages(["NGA", "EGY", "ZAF", ...])`
- "Global North avg": `get_regional_averages(["USA", "CAN", "DEU", ...])`

---

## 5. Module 3: countries.ipynb

### Purpose
Provides country metadata, regional groupings, and configuration for the dashboard.

### Configuration Dictionaries

#### `COUNTRIES` - Country Metadata
```python
COUNTRIES = {
    "EGY": {
        "name": "Egypt",
        "region": "Middle East & North Africa",
        "capital": "Cairo",
        "description": "..."
    },
    # ... 30+ countries included
}
```

**Why hardcode?** Ensures:
- Consistent display names
- Correct regional groupings
- Meaningful descriptions for AI context

#### `REGIONS` - Regional Groupings
```python
REGIONS = {
    "Africa": ["ZAF", "NGA"],  # South Africa, Nigeria
    "Asia": ["CHN", "JPN", "IND", ...],
    "Europe": ["DEU", "GBR", "FRA", ...],
    "North America": ["USA", "CAN", "MEX"],
    "South America": ["BRA", "ARG"],
    "Middle East": ["SAU", "ARE", "EGY"],
    "Oceania": ["AUS"],
}
```

**Use cases:**
- Regional averages for comparison
- Color coding by region
- Dropdown organization

#### `DEFAULT_COMPARISONS` - Smart Defaults
```python
DEFAULT_COMPARISONS = {
    "EGY": ["IND", "SAU", "ARE", "WLD"],  # Egypt compares to:
    "IND": ["EGY", "CHN", "USA", "WLD"],  # Similar development stage
    "SAU": ["EGY", "ARE", "IRQ", "WLD"],  # Regional comparison
}
```

**Design rationale:** Each country compares to contextually relevant peers, not random selections.

#### `EMISSION_CATEGORIES` - Classification
```python
EMISSION_CATEGORIES = {
    "low":    {"max_per_capita": 2.0,  "color": "#81B29A"},
    "medium": {"max_per_capita": 5.0,  "color": "#F2CC8F"},
    "high":   {"max_per_capita": float("inf"), "color": "#E07A5F"},
}
```

**Thresholds explained:**
| Category | Threshold | Examples | Climate Justice Implication |
|----------|-----------|----------|----------------------------|
| Low | ≤ 2.0 t/capita | India (1.9), Egypt (2.5) | Below global average |
| Medium | 2.0 - 5.0 t/capita | China (8.0), Brazil (2.3) | Developing/emerging |
| High | > 5.0 t/capita | USA (14.7), Australia (15.0) | Developed nations |

---

## 6. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPLETE DATA PIPELINE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐                                                     │
│  │ OWID GitHub │                                                     │
│  │   CSV URL   │                                                     │
│  │ (External)  │                                                     │
│  └──────┬──────┘                                                     │
│         │                                                             │
│         ▼                                                             │
│  ┌─────────────────────────────────────────┐                        │
│  │         DataFetcher Class                │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ fetch_owid_data()               │    │                        │
│  │  │ 1. Check cache exists?          │    │                        │
│  │  │ 2. Load from CSV or GitHub     │    │                        │
│  │  │ 3. Save to cache               │    │                        │
│  │  │ 4. Return DataFrame             │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  │                                         │                        │
│  │  Output Methods:                         │                        │
│  │  ├─ get_country_data()      → Dict     │                        │
│  │  ├─ get_comparison_data()    → Dict     │                        │
│  │  ├─ get_global_stats()       → Dict     │                        │
│  │  └─ export_country_json()    → JSON     │                        │
│  └──────────────────┬──────────────────────┘                        │
│                     │                                                 │
│                     ▼                                                 │
│  ┌─────────────────────────────────────────┐                        │
│  │        EmissionAnalyzer Class            │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ calculate_trend_stats()         │    │                        │
│  │  │ 1. Get filtered country data   │    │                        │
│  │  │ 2. Calculate linear regression │    │                        │
│  │  │ 3. Compute YoY changes        │    │                        │
│  │  │ 4. Return statistics dict     │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  │                                         │                        │
│  │  Analysis Methods:                       │                        │
│  │  ├─ get_country_summary()     → Dict    │                        │
│  │  ├─ calculate_carbon_intensity() → Dict  │                        │
│  │  └─ get_regional_averages()   → Dict    │                        │
│  └──────────────────┬──────────────────────┘                        │
│                     │                                                 │
│         ┌───────────┴───────────┐                                    │
│         ▼                       ▼                                    │
│  ┌─────────────┐         ┌─────────────┐                             │
│  │  Countries  │         │  OWID Data  │                             │
│  │  Config     │         │  (Raw 80+   │                             │
│  │  - Names    │         │   cols)     │                             │
│  │  - Regions  │         │             │                             │
│  │  - Defaults │         │             │                             │
│  └─────────────┘         └─────────────┘                             │
│                     │                                                 │
│                     ▼                                                 │
│  ┌─────────────────────────────────────────┐                        │
│  │         Voila Dashboard                  │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ ipywidgets                       │    │                        │
│  │  │  ├─ Country dropdown            │    │                        │
│  │  │  ├─ Period pills (toggle)       │    │                        │
│  │  │  ├─ Comparison checkboxes       │    │                        │
│  │  │  └─ AI chat input              │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ Plotly Charts                   │    │                        │
│  │  │  ├─ Line (emissions trend)     │    │                        │
│  │  │  ├─ Multi-line (comparisons)   │    │                        │
│  │  │  └─ Scatter (GDP vs CO2)       │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ Gemini AI Integration            │    │                        │
│  │  │  └─ On-demand insights          │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Key Variables for Dashboard

### Primary Variables (Essential - For Core Charts)

| Variable | Dashboard Use | Chart Type | Egypt 2023 |
|----------|---------------|------------|------------|
| `co2` | Total emissions trend | Line | 249 Mt |
| `co2_per_capita` | Per capita comparison | Multi-line | 2.47 t |
| `share_global_co2` | Global context | Metric card | 0.64% |
| `gdp` | Economic context | Scatter X-axis | $302B |
| `population` | Scale | Metric card | 107M |
| `co2_growth_prct` | Change rate | YoY analysis | -6.4% |

### Secondary Variables (Enhancement)

| Variable | Dashboard Use | Value |
|----------|---------------|-------|
| `coal_co2` | Source breakdown | Stacked area |
| `gas_co2` | Source breakdown (Zohr!) | Stacked area |
| `oil_co2` | Source breakdown | Stacked area |
| `consumption_co2` | Trade-adjusted view | Alternative metric |
| `total_ghg` | Broader emissions | Additional metric |
| `trade_co2` | Import/export analysis | Climate justice |

### Variables for AI Context (Passed to Gemini)

```python
ai_context = {
    "country": "Egypt",
    "iso_code": "EGY",
    "year": 2023,
    
    # Core metrics
    "co2_total": 249,              # Million tonnes
    "co2_per_capita": 2.47,        # Tonnes per person
    "share_global_co2": 0.64,      # Percentage
    "gdp": 302_000_000_000,        # USD
    "population": 107_000_000,     # People
    
    # Derived
    "gdp_per_capita": 302_000_000_000 / 107_000_000,  # ~$2822 USD
    "trend": "increasing",         # From linear regression
    "period_change": "+57.5%",     # 2005-2023 change
    "emission_category": "low",    # From EMISSION_CATEGORIES
    
    # Context
    "global_co2_per_capita": 4.70,  # World average
    "vs_global_average": 2.47 / 4.70,  # = 0.53 (53%)
    
    # Historical
    "peak_year": 2022,
    "peak_value": 267,             # Mt (Zohr effect)
    
    # Economic events
    "arab_spring_year": 2011,
    "zohr_gas_online": 2017,
    "imf_reform_year": 2016,
}
```

---

## 8. Robustness Features

### A. Error Handling

```python
# 1. Missing data handling
if pd.notna(row.get("co2")):
    entry[col] = float(row[col])
else:
    entry[col] = None  # Explicit None instead of NaN

# 2. Empty dataframe check
if data.empty:
    return {}
    
# 3. Division by zero protection
if values[0] != 0:
    overall_change = (values[-1] - values[0]) / values[0] * 100
else:
    overall_change = 0

# 4. API failure recovery
except Exception as e:
    print(f"Error: {e}")
    if os.path.exists(cache_file):
        self.owid_df = pd.read_csv(cache_file)  # Graceful fallback
```

### B. Data Validation

```python
# 1. ISO code validation (3 characters)
(self.owid_df["iso_code"].str.len() == 3)

# 2. Year range validation
(data["year"] >= START_YEAR) & (data["year"] <= END_YEAR)

# 3. Required columns check
if "co2" not in data.columns:
    return []

# 4. Type checking
try:
    entry[col] = float(row[col])
except (ValueError, TypeError):
    entry[col] = row[col]  # Keep as-is if conversion fails
```

### C. Caching Strategy

```
┌────────────────────────────────────────────────────┐
│              CACHING FLOW                           │
├────────────────────────────────────────────────────┤
│                                                     │
│   Request ──▶ Cache exists? ──▶ Return cache      │
│                   │                                │
│                   │ No                             │
│                   ▼                                │
│              Fetch from GitHub                     │
│                   │                                │
│                   ├────▶ Success ──▶ Save & Return │
│                   │                                │
│                   └────▶ Failure ──▶ Use cache   │
│                                    (if exists)     │
│                                                     │
│   Benefit: Works offline after first fetch         │
│                                                     │
└────────────────────────────────────────────────────┘
```

### D. Type Safety

```python
# 1. Explicit type conversion
entry = {"year": int(row["year"])}  # Always int for year

# 2. Safe None checking
if summary["co2_per_capita"] and global_stats:
    # Only calculate if both exist

# 3. Default values
.fillna(0)  # For calculations
.fillna(None)  # For display
```

---

## 9. Recommendations for Enhancement

### For Academic Presentation (Recommended)

#### 1. Add Period-Based Statistics

```python
def get_period_stats(self, country_code, period):
    """Calculate stats for specific historical periods"""
    
    periods = {
        "pre_arab_spring": (2005, 2010),
        "post_arab_spring": (2011, 2015),
        "imf_reform": (2016, 2019),
        "post_zohr": (2018, 2023),
        "covid": (2019, 2023),
        "full": (2005, 2023)
    }
    
    start, end = periods[period]
    data = self.get_country_data_owid(country_code, (start, end))
    
    # Calculate: start_val, end_val, change_pct, CAGR, avg_growth
```

#### 2. Add GDP per Capita Calculation

```python
def get_gdp_per_capita(self, country_code, year):
    """Calculate GDP per capita = GDP / Population"""
    summary = self.get_country_summary(country_code, year)
    
    if summary["gdp"] and summary["population"]:
        return summary["gdp"] / summary["population"]
    return None
```

#### 3. Add Peak/Valley Detection

```python
def find_significant_years(self, country_code):
    """Identify years with local max/min (peaks/valleys)"""
    from scipy.signal import find_peaks
    
    data = self.get_country_data_owid(country_code)
    values = data["co2"].values
    
    # Find peaks (local maxima)
    peaks, _ = find_peaks(values, prominence=10)
    
    # Get years and values
    peak_years = data["year"].iloc[peaks].tolist()
    peak_values = values[peaks].tolist()
    
    return {"peaks": list(zip(peak_years, peak_values))}
```

#### 4. Add CAGR (Compound Annual Growth Rate)

```python
def calculate_cagr(self, start_value, end_value, years):
    """
    Compound Annual Growth Rate
    
    CAGR = (End Value / Start Value)^(1/years) - 1
    
    Example: CO2 grew from 158 to 249 Mt over 18 years
    CAGR = (249/158)^(1/18) - 1 = 2.5% annual growth
    """
    if start_value <= 0 or years <= 0:
        return None
    return (end_value / start_value) ** (1/years) - 1
```

### For Robustness (Before Deployment)

#### 1. Data Freshness Check

```python
import time
from datetime import datetime

def check_data_freshness(self, max_age_hours=24):
    """Verify cache isn't too old"""
    cache_file = os.path.join(CACHE_DIR, "owid_emissions.csv")
    
    if not os.path.exists(cache_file):
        return {"fresh": False, "message": "No cache found"}
    
    cache_time = os.path.getmtime(cache_file)
    age_hours = (time.time() - cache_time) / 3600
    
    cache_date = datetime.fromtimestamp(cache_time).strftime("%Y-%m-%d")
    
    return {
        "fresh": age_hours < max_age_hours,
        "age_hours": round(age_hours, 1),
        "cache_date": cache_date,
        "message": f"Data from {cache_date} ({age_hours:.1f}h old)"
    }
```

#### 2. Input Validation for Widgets

```python
def validate_country_code(code):
    """Ensure valid ISO code before processing"""
    from data.countries import COUNTRIES
    
    if code not in COUNTRIES:
        raise ValueError(
            f"Invalid country code: {code}\n"
            f"Valid codes: {list(COUNTRIES.keys())}"
        )
    return True

def validate_year_range(start_year, end_year):
    """Ensure valid year range"""
    if start_year > end_year:
        raise ValueError(f"start_year ({start_year}) > end_year ({end_year})")
    if start_year < 1950 or end_year > 2024:
        raise ValueError(f"Year range must be between 1950-2024")
    return True
```

#### 3. Rate Limiting for API Calls

```python
import time

class RateLimitedFetcher:
    """Add delays between API calls"""
    
    def __init__(self, delay_seconds=1):
        self.last_call = 0
        self.delay = delay_seconds
    
    def fetch_with_delay(self, url):
        # Wait if called too recently
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        
        self.last_call = time.time()
        return requests.get(url)
```

### For Climate Justice Narrative

#### 1. Historical Responsibility Calculator

```python
def calculate_historical_emissions(self, country_code):
    """Sum cumulative emissions vs share of global population"""
    data = self.get_country_data_owid(country_code, (1990, 2023))
    
    cumulative_co2 = data["co2"].sum()  # Mt
    
    # Compare to fair share (population × global avg)
    # If a country emitted more than their population share justifies
    
    return {
        "cumulative_co2": cumulative_co2,
        "fair_share_co2": calculate_fair_share(country_code),
        "emissions_deficit": cumulative_co2 - fair_share
    }
```

#### 2. Consumption vs Production Gap

```python
def calculate_consumption_production_gap(self, country_code, year):
    """Difference between production and consumption based CO2"""
    data = self.get_country_data_owid(country_code)
    row = data[data["year"] == year].iloc[0]
    
    production = row.get("co2", 0)
    consumption = row.get("consumption_co2", 0)
    
    return {
        "production": production,
        "consumption": consumption,
        "gap": consumption - production,  # Positive = net importer
        "is_importer": consumption > production
    }
```

---

## Summary

### Backend Architecture

| Module | Class | Responsibility | Key Output |
|--------|-------|----------------|------------|
| `fetch_data` | `DataFetcher` | Data acquisition & caching | Clean DataFrame |
| `analysis` | `EmissionAnalyzer` | Statistical calculations | Metrics & trends |
| `countries` | (Dictionary) | Configuration & metadata | Settings |

### Data Pipeline Flow

```
OWID GitHub CSV → DataFetcher → DataFrame → EmissionAnalyzer → Statistics
                                              ↓
                                    Countries Config
                                              ↓
                                    Voila Dashboard
                                              ↓
                                    Plotly Charts + AI
```

### Robustness Checklist

| Feature | Status | Implementation |
|---------|--------|----------------|
| Caching | ✅ | CSV file in `data/cache/` |
| Error Handling | ✅ | Try-except with fallback |
| Missing Data | ✅ | `.fillna(0)` and `pd.notna()` |
| Empty Data | ✅ | `if data.empty: return {}` |
| Type Safety | ✅ | Explicit conversion |
| Input Validation | ⚠️ | Can be enhanced |

### Key Variables for Egypt Climate Justice

| Metric | Value | Implication |
|--------|-------|-------------|
| CO₂ per capita | 2.47 t | 53% of global average (4.70 t) |
| Global share | 0.64% | 1/3 of population share (1.3%) |
| Emissions category | Low | Below threshold |
| GDP per capita | ~$2,800 | Developing nation |
| Historical growth | +57.5% | Development-driven, not luxury |

### OWID Dataset Advantages

| Advantage | Explanation |
|-----------|-------------|
| **Authoritative** | Source: Global Carbon Project, UNFCCC |
| **Comprehensive** | 80+ variables, 200+ countries |
| **Historical** | Data from 1750 onwards |
| **Well-documented** | Clear methodology, citations |
| **Free** | Open source, no API key needed |
| **Updated** | Annual updates from official sources |

---

## 10. Flask API Architecture

### Overview

The Flask application (`app.py`) serves as the backend API layer, providing endpoints for data retrieval and AI-powered insights. All endpoints return JSON responses.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLASK APPLICATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   /api/    │  │   /api/    │  │   /api/ai/  │             │
│  │  summary   │  │ comparison  │  │   sources   │             │
│  │   {code}   │  │  {code}?   │  │   {code}?   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                 │                 │                     │
│         └────────────────┼─────────────────┘                     │
│                          ▼                                       │
│              ┌───────────────────────┐                           │
│              │    data_utils.py       │                           │
│              │  ┌─────────────────┐  │                           │
│              │  │ load_data()     │  │                           │
│              │  │ get_country_*   │  │                           │
│              │  │ calculate_*     │  │                           │
│              │  └─────────────────┘  │                           │
│              └───────────┬───────────┘                           │
│                          ▼                                       │
│              ┌───────────────────────┐                           │
│              │  data/cache/          │                           │
│              │  owid_emissions.csv   │                           │
│              └───────────────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### API Endpoints

#### Core Data Endpoints

| Endpoint | Method | Parameters | Returns |
|----------|--------|------------|---------|
| `/` | GET | None | Renders main dashboard HTML |
| `/api/countries` | GET | None | List of all available countries |
| `/api/summary/<code>` | GET | `code`: ISO country code | Country summary with KPIs |
| `/api/trend/<code>` | GET | `code`, `metric`: co2/ghg | Trend statistics |
| `/api/comparison/<code>` | GET | `code`, `tier`, `year` | Comparison data |
| `/api/emission-sources/<code>` | GET | `code`, `mode`, `year` | Source breakdown |

#### AI-Powered Endpoints

| Endpoint | Method | Parameters | Returns |
|----------|--------|------------|---------|
| `/api/ai/trend/<code>` | GET | `code`, `metric` | AI-generated trend insight |
| `/api/ai/comparison/<code>` | GET | `code`, `tier` | AI-generated comparison |
| `/api/ai/sources/<code>` | GET | `code`, `mode` | AI-generated sources analysis |
| `/api/ai/reflection/<code>` | GET | `code` | Climate justice reflection |

### Key Route Implementations

#### Comparison Endpoint with Year Filter

```python
@app.route("/api/comparison/<country_code>")
def api_comparison(country_code):
    tier = request.args.get("tier", None)
    year = request.args.get("year", 2023, type=int)
    comp_data = get_comparison_data(
        country_code.upper(), 
        df=_data, 
        tier=tier,
        year=year  # Year filter added
    )
    return jsonify(comp_data)
```

**Parameters:**
- `tier`: Comparison tier - `peers`, `regional`, or `responsibility`
- `year`: Data year filter (2001-2023, default: 2023)

#### Emission Sources Endpoint with CO2/GHG Toggle

```python
@app.route("/api/emission-sources/<country_code>")
def api_emission_sources(country_code):
    mode = request.args.get("mode", "co2")  # "co2" or "ghg"
    year = request.args.get("year", None)
    sources = get_emission_sources(
        country_code.upper(), 
        year=year,
        mode=mode,  # Mode toggle added
        df=_data
    )
    return jsonify(sources)
```

**Mode Logic:**
- `co2`: Returns CO2 only (coal, oil, gas, cement, flaring)
- `ghg`: Calculates non-CO2 GHGs and returns full breakdown

### Global Data Loading

```python
# Load data once at startup (not per request)
_data = load_data()

@app.route("/api/summary/<country_code>")
def api_summary(country_code):
    summary = get_country_summary(country_code.upper(), df=_data)
    return jsonify(summary)
```

**Performance optimization:** Data is loaded once when the app starts, then reused across all requests to avoid repeated CSV parsing.

---

## 11. AI Service Integration

### Overview

The AI service uses OpenRouter API to provide natural language insights. It supports free-tier models for cost-effective operation.

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI SERVICE FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frontend Request ──▶ Flask API ──▶ ai_service.py               │
│                                       │                          │
│                                       ▼                          │
│                          ┌─────────────────────┐                │
│                          │  Rate Limiter      │                │
│                          │  (2s between calls) │               │
│                          └──────────┬──────────┘                │
│                                     │                           │
│                                     ▼                           │
│                          ┌─────────────────────┐                │
│                          │ OpenRouter API      │                │
│                          │ Free Tier Model     │                │
│                          │ liquid/lfm-2.5-...  │                │
│                          └──────────┬──────────┘                │
│                                     │                           │
│                                     ▼                           │
│                          ┌─────────────────────┐                │
│                          │ Response Formatter │                │
│                          │ (Markdown support) │                │
│                          └──────────┬──────────┘                │
│                                     │                           │
│                                     ▼                           │
│                          Frontend AI Box Display                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### AI Service Functions

| Function | Purpose | Prompt Focus |
|----------|---------|--------------|
| `generate_emissions_insight()` | Trend analysis | Period comparison, key drivers |
| `generate_comparison_insight()` | Country comparison | Relative position, fairness |
| `generate_climate_reflection()` | Climate justice | Vulnerability vs responsibility |
| `generate_sources_insight()` | Source breakdown | Energy mix implications |

### Rate Limiting

```python
_last_call = 0
MIN_INTERVAL = 2  # seconds

def ai_service_call():
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _last_call = time.time()
    # ... make API call
```

### Prompt Engineering

Each AI function constructs a specialized prompt with:
1. **Country context**: Name, population, development status
2. **Data metrics**: Current values, trends, comparisons
3. **Climate narrative**: Framing around justice/fairness
4. **Output format**: Concise, actionable insights

Example trend prompt:
```
Generate a brief analysis of Egypt's CO2 emissions trend...
Include: Recent trajectory, key drivers, comparison to peers...
```

---

## 12. Frontend Logic & Visualizations

### Overview

The frontend uses vanilla JavaScript with Plotly.js for interactive visualizations. All chart rendering is handled client-side with data fetched from Flask API.

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    index.html                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │   Header    │  │   Hero      │  │   KPI       │    │   │
│  │  │  Navigation │  │   Section   │  │   Cards     │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │  Emissions  │  │  Sources    │  │   Global    │    │   │
│  │  │  Charts     │  │  Donut+Line │  │  Context    │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              JavaScript Modules                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │ Plotly.js   │  │  API Calls  │  │  UI State   │    │   │
│  │  │  Charts     │  │  (fetch)    │  │  (current*) │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### State Variables

```javascript
let currentCountry = 'EGY';      // Current selected country
let currentTier = 'peers';       // Comparison tier
let currentMode = 'co2';          // 'co2' or 'ghg'
let selectedPhase = null;         // Historical phase
let selectedYear = 2023;           // Year for sources
```

### Chart Rendering

#### Shared Plotly Configuration (PB)

```javascript
const PB = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor:  'rgba(0,0,0,0)',
    font: { family: 'Plus Jakarta Sans, sans-serif', color: '#7A6F5A', size: 11 },
    margin: { t: 16, r: 16, b: 48, l: 56 },
    xaxis: { gridcolor: 'rgba(44,36,22,0.06)', ... },
    yaxis: { gridcolor: 'rgba(44,36,22,0.06)', ... },
    hoverlabel: { bgcolor: '#FFFFFF', bordercolor: 'rgba(92,42,26,0.12)', ... }
};
```

#### Helper Function

```javascript
function plotInto(id, traces, layout, cfg) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';  // Clear spinner
    Plotly.newPlot(el, traces, { ...PB, ...layout }, { responsive: true, displayModeBar: false });
}
```

### Comparison Charts

Four charts in the Global Comparison section:

| Chart | Type | Data Source | Features |
|-------|------|-------------|----------|
| Per Capita Bar | Bar | co2_per_capita | Sorted descending, world avg line |
| GDP vs CO2 | Scatter | gdp, co2_per_capita | Bubble size = population |
| HDI-Adjusted | Bar | co2_per_capita / HDI | Shows efficiency ratio |
| Carbon Intensity | Bar | co2 / GDP | Economic efficiency |

---

## 13. CO2/GHG Toggle Logic

### Overview

The dashboard supports toggling between CO2-only and full GHG (Greenhouse Gas) views in the Sources section only. KPIs always display CO2 values.

```
┌─────────────────────────────────────────────────────────────────┐
│                     CO2/GHG TOGGLE LOGIC                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User toggles switch ──▶ currentMode = 'co2' or 'ghg'           │
│                                │                                │
│                                ▼                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   API Call                                 │  │
│  │  /api/emission-sources/EGY?mode=co2&year=2023           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                │                                │
│              ┌─────────────────┴─────────────────┐              │
│              ▼                                   ▼              │
│  ┌─────────────────────┐         ┌─────────────────────────┐  │
│  │      CO2 Mode       │         │        GHG Mode          │  │
│  │  - Coal, Oil, Gas   │         │  - Coal, Oil, Gas       │  │
│  │  - Cement, Flaring  │         │  - Cement, Flaring     │  │
│  │  - Total = Sum      │         │  - Non-CO2 GHGs        │  │
│  │                     │         │  - Total = Sum          │  │
│  └─────────────────────┘         └─────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Calculation (Non-CO2 GHGs)

```python
# Non-CO2 = Total GHG excluding LUCF - Sum of CO2 sources
other_ghgs = total_ghg_excluding_lucf - (coal + oil + gas + cement + flaring)

# Displayed in donut as separate slice
ghg_sources = {
    'coal': coal_co2,
    'oil': oil_co2,
    'gas': gas_co2,
    'cement': cement_co2,
    'flaring': flaring_co2,
    'other_ghg': max(0, other_ghgs)  # Ensure non-negative
}
```

### Frontend Label Updates

```javascript
// Toggle UI elements based on mode
if (currentMode === 'co2') {
    chartTitle = 'CO₂ by Source';
    yAxisLabel = 'Mt CO₂';
    footnote = '';  // No footnote for CO2 mode
} else {
    chartTitle = 'GHG by Source';
    yAxisLabel = 'Mt CO₂e';
    footnote = 'Non-CO₂ values calculated using GWP100 metric via OWID/IPCC';
}
```

### LULUCF Overlay

LULUCF (Land Use, Land-Use Change, and Forestry) data is shown as a line overlay in GHG mode when available:

```javascript
// Only show LULUCF line if data exists and is non-zero
if (lulucfData && lulucfData.some(v => v !== 0)) {
    // Add line trace for LULUCF
}
```

---

## 14. Year Filter Implementation

### Overview

The Global Comparison section includes a year filter dropdown that allows users to view historical comparison data (2001-2023).

```
┌─────────────────────────────────────────────────────────────────┐
│                      YEAR FILTER FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User selects year ──▶ onchange event                          │
│         │                                                        │
│         ▼                                                        │
│  loadComparisonCharts(currentTier)                               │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Fetch: /api/comparison/EGY?tier=peers&year=2015       │    │
│  └─────────────────────────────────────────────────────────┘    │
│         │                                                        │
│         ▼                                                        │
│  Backend filters data for year=2015                             │
│         │                                                        │
│         ▼                                                        │
│  All 4 comparison charts update with 2015 data                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend Implementation

```javascript
// Year dropdown HTML
<div class="year-selector">
    <select id="compYear" onchange="loadComparisonCharts(currentTier)">
        <!-- Options populated by JS -->
    </select>
</div>

// Initialize dropdown with years 2001-2023
function initComparisonYearDropdown() {
    const select = document.getElementById('compYear');
    const years = [];
    for (let y = 2023; y >= 2001; y--) years.push(y);
    select.innerHTML = years.map(y => 
        `<option value="${y}" ${y === 2023 ? 'selected' : ''}>${y}</option>`
    ).join('');
}

// Use selected year in API call
async function loadComparisonCharts(tier) {
    const year = document.getElementById('compYear')?.value || 2023;
    const url = `/api/comparison/${currentCountry}?tier=${tier}&year=${year}`;
    // ... fetch and render
}
```

### Backend Implementation

```python
def get_comparison_data(country_code, comparison_codes=None, df=None, tier=None, year=None):
    if year is None:
        year = END_YEAR  # Default to 2023
    
    # Filter for specific year
    year_data = data[data["year"] == year]
    
    # Fallback if year data not available
    if year_data.empty:
        year_data = data.iloc[[-1]]  # Use latest available
    
    # Extract values for that year
    co2_val = float(year_data["co2"].iloc[0])
    gdp_val = float(year_data["gdp"].iloc[0])
    # ... other metrics
```

---

## 15. Tier Comparison System

### Overview

The Global Comparison section uses a tier system to show different comparison contexts:

| Tier | Purpose | Countries Compared |
|------|---------|-------------------|
| Peers | Similar development | Egypt → India, Morocco, Pakistan, Indonesia |
| Regional | Geographic neighbors | Egypt → Saudi Arabia, Iran, Iraq, Africa |
| Responsibility | Major emitters | Egypt → USA, China, Germany, World |

### Tier Mappings

```python
TIER_COMPARISONS = {
    "EGY": {
        "peers": ["IND", "IDN", "MAR", "PAK"],      # Similar GDP/capita
        "regional": ["SAU", "IRN", "IRQ", "ZAF"],   # Geographic region
        "responsibility": ["USA", "CHN", "DEU", "WLD"]  # Historical emitters
    },
    # ... other countries
}
```

### Frontend Tier Switching

```javascript
// Tier cells rendered as clickable cards
function renderTierCells() {
    const tiers = ['peers', 'regional', 'responsibility'];
    el.innerHTML = tiers.map(t => {
        const cfg = TIER_CONFIG[t];
        const active = t === currentTier ? 'active' : '';
        return `<div class="tier-cell ${active}" onclick="switchTier('${t}')">
            <div class="tier-name">${cfg.label}</div>
            <div class="tier-desc">${cfg.desc}</div>
        </div>`;
    }).join('');
}

function switchTier(tier) {
    currentTier = tier;
    renderTierCells();
    loadComparisonCharts(tier);
}
```

### Tier Configuration

```javascript
const TIER_CONFIG = {
    peers: {
        label: "Peers",
        desc: "Similar development level",
        color: "#5E8C61"  // Green - harmony
    },
    regional: {
        label: "Regional",
        desc: "Geographic neighbors",
        color: "#C8943A"  // Amber - warm
    },
    responsibility: {
        label: "Responsibility",
        desc: "Historical emitters",
        color: "#C65D3B"  // Terracotta - urgent
    }
};
```

---

## 16. Color System & Theming

### CSS Variables

```css
:root {
    /* Primary - Terracotta (used for Egypt highlights) */
    --primary:    #C65D3B;
    --primary2:   #A84D2F;
    --primary-bg: rgba(198, 93, 59, 0.08);
    
    /* Secondary - Sage Green */
    --secondary:  #5E8C61;
    --secondary2: #4A7050;
    --secondary-bg: rgba(94, 140, 97, 0.08);
    
    /* Neutrals - Warm grays */
    --text:       #3D3226;
    --text2:      #5A5045;
    --text3:      #8B8070;
    --surface:    #FAFAF8;
    --surface2:   #F5F2ED;
    --border:     rgba(44, 36, 22, 0.10);
}
```

### Comparison Chart Colors

```javascript
// Egypt always highlighted in green (secondary)
const egyptColor = '#5E8C61';

// Other countries in maroon gradient (warm, earthy)
const maroonGradient = ['#8B5A4A', '#9E6B5B', '#B07B6B', '#C28B7B', '#D49B8B'];

// Color assignment function
const getBarColor = (name, index) => 
    name === 'Egypt' ? egyptColor : maroonGradient[index % maroonGradient.length];
```

### Phase Colors

Historical phases use distinct colors:

```javascript
const PHASES = {
    preArabSpring: { color: '#8B6914', name: 'Pre-Arab Spring' },
    arabSpring:    { color: '#C65D3B', name: 'Arab Spring' },
    postCrisis:   { color: '#C8943A', name: 'Post-Crisis Recovery' },
    reformZohr:    { color: '#5E8C61', name: 'Reform & Zohr' },
    covid:         { color: '#7A6F5A', name: 'COVID-19' }
};
```

### Source Colors

Emission sources use a warm palette:

```javascript
const srcColors = {
    'Gas':    '#C65D3B',  // Terracotta
    'Oil':    '#8B6B4F',  // Brown
    'Coal':   '#A89E8C',  // Gray-brown
    'Cement': '#C9A84C',  // Gold
    'Flaring':'#5E8C61'   // Green
};
```

---

## 17. Global Context Panel

### Overview

The Global Context panel provides comparative context using data from OWID and World Bank:

```
┌─────────────────────────────────────────────────────────────────┐
│                     GLOBAL CONTEXT PANEL                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ GDP per Capita  │  │  vs Global Avg  │  │    Emissions    │  │
│  │  $3,457 (nominal)│ │    -54%         │  │   0.64% share   │  │
│  │   ───────────    │ │   ┌──────┐      │  │                 │  │
│  │   [gauge ring]  │ │   │ EGY │      │  │                 │  │
│  │                 │ │   └──────┘      │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### GDP per Capita Calculation

```python
# World Bank nominal USD (not OWID PPP)
GDP_PER_CAPITA_FALLBACK = {
    "EGY": 3457,  # 2023 World Bank nominal USD
    # ... other countries
}

# If OWID data unavailable, use fallback
if gdp_pc is None and code in GDP_PER_CAPITA_FALLBACK:
    gdp_pc = GDP_PER_CAPITA_FALLBACK[code]
```

### vs Global Average Calculation

```python
# Calculate how much below/above global average
egypt_per_capita = 2.19  # t CO2/person
world_per_capita = 4.71  # t CO2/person

vs_avg = ((egypt_per_capita - world_per_capita) / world_per_capita) * 100
# Result: -54% (Egypt emits 54% less than world average)
```

### Gauge Ring Visualization

```javascript
// Small circular gauge showing relative position
<div class="gauge-wrap-sm">
    <svg viewBox="0 0 120 120">
        <circle class="gauge-bg" ... />
        <circle class="gauge-fill" 
            stroke-dasharray="${percentage * 3.77} 377" ... />
    </svg>
    <div class="gauge-center">
        <div class="gauge-val">${value}</div>
        <div class="gauge-unit">${unit}</div>
    </div>
</div>
```

### Comparison Bars

```javascript
// Horizontal bars comparing Egypt to other countries
const comparisonData = [
    { name: 'Egypt', value: 2.19 },
    { name: 'India', value: 2.13 },
    { name: 'World avg', value: 4.71 }
];

// Calculate percentage of world average
const pct = (egyptValue / worldValue) * 100;
// Egypt bar width = 46% of world bar width
```

---

## Contact & References

**Data Source:** Our World in Data - CO₂ and GHG Emissions Dataset
- GitHub: https://github.com/owid/co2-data
- Citation: "Our World in Data" - Global Carbon Project

**Code Structure:** Three-module architecture for modularity and maintainability

**Prepared for:** TISS Mumbai - Climate Change, Sustainability & Development Assignment
