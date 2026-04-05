# Egypt Emissions Trend & Climate Inequality Dashboard

<p align="center">
  <img src="static/egypt_hero.jpg" alt="Egypt Dashboard" width="100%" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</p>

<p align="center">
  <strong>An interactive dashboard exploring Egypt's emissions trajectory through a climate justice lens</strong>
</p>

<p align="center">
  <a href="https://github.com/owid/co2-data">Data Source: Our World in Data</a> •
  <a href="https://github.com/openrouter/openrouter-api">AI: OpenRouter</a> •
  <a href="https://plotly.com/javascript/">Visualizations: Plotly.js</a>
</p>

---

## The Climate Justice Story

Egypt presents a compelling case of **climate injustice** — where vulnerability vastly exceeds responsibility.

### Key Statistics (2023)

| Metric | Egypt | Global Average | Implication |
|--------|-------|----------------|-------------|
| CO₂ per capita | **2.19 t** | 4.71 t | 54% below average |
| Global CO₂ share | **0.64%** | — | 1/3 of population share |
| Population | **114 million** | — | Growing at ~2M/year |
| GDP per capita | **$3,457** (nominal) | — | Developing nation |

### Why This Matters

- Egypt contributes **less than 0.7%** of global CO₂ emissions
- Hosts **COP27** (2022)** and committed to **42% renewable electricity by 2035**
- One of the world's most **climate-vulnerable coastal zones** faces sea-level rise
- Despite Zohr gas discovery (2015) making Egypt a net exporter, fossil fuels still account for **90%+ of electricity**

---

## Dashboard Features

### 1. Emissions Trend Analysis

Interactive line charts showing Egypt's CO₂ emissions from 2001-2023 with:

- **Total emissions** (Mt CO₂) with historical phases
- **Per capita emissions** (t CO₂/person) normalized by population
- **CAGR calculations** for each historical period

**Historical Phases:**
| Period | Phase | CAGR | Key Events |
|--------|-------|------|------------|
| 2001-2010 | Pre-Arab Spring | +5.4%/yr | Rapid industrialization |
| 2011-2015 | Post-Crisis | +0.6%/yr | Arab Spring, political transition |
| 2016-2019 | Reform & Zohr | **-1.5%/yr** | Zohr gas online, IMF reform |
| 2020-2023 | COVID & Recovery | +0.5%/yr | Pandemic, global recovery |

### 2. Fuel Mix Breakdown (CO₂/GHG Toggle)

Explore emissions by source with a toggle between:

- **CO₂ Mode**: Coal, Oil, Gas, Cement, Flaring
- **GHG Mode**: Full greenhouse gas breakdown including methane (CH₄), nitrous oxide (N₂O)

**Key Insight:** The Zohr gas field (discovered 2015, online 2017) led to Egypt becoming a net gas exporter by 2019 — explaining the emissions decline during 2016-2019.

### 3. Global Comparison with Year Filter

Compare Egypt's performance against different country groups across **2001-2023**:

| Tier | Countries | Purpose |
|------|----------|---------|
| **Peers** | India, Morocco, Pakistan, Indonesia | Similar development stage |
| **Regional** | Saudi Arabia, Iran, Iraq, South Africa | Geographic neighbors |
| **Responsibility** | USA, China, Germany, World | Historical emitters |

**Four Comparison Charts:**
1. **Per Capita Bar** — Sorted descending with world average reference line
2. **GDP vs CO₂ Scatter** — Bubble size shows population
3. **HDI-Adjusted Emissions** — CO₂ per capita / HDI score (lower = more efficient)
4. **Carbon Intensity** — CO₂ per million USD GDP

### 4. AI-Powered Insights

Generated using free-tier LLMs via OpenRouter, providing:

- Trend analysis with key drivers
- Country comparison insights
- Emission source breakdown analysis
- Climate justice reflection

### 5. Global Context Panel

Quick reference metrics showing:
- **GDP per capita** (nominal USD, not PPP)
- **vs Global Average** (-54% less)
- **Share of Global Emissions** (0.64%)

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      FLASK BACKEND                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │   │
│  │  │  app.py     │  │data_utils.py│  │ai_service.py│        │   │
│  │  │  (Routes)   │  │  (Data)     │  │  (AI API)   │        │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      OWID DATA                                │   │
│  │              data/cache/owid_emissions.csv                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    JINJA2 TEMPLATES                            │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐   │   │
│  │  │    base.html    │  │         index.html               │   │   │
│  │  │  (CSS, Layout)  │  │  (Charts, JS, Components)       │   │   │
│  │  └─────────────────┘  └─────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    PLOTLY.JS FRONTEND                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │
│  │  │  Line   │  │  Donut  │  │   Bar   │  │ Scatter │       │   │
│  │  │  Chart  │  │  Chart  │  │  Chart  │  │  Chart  │       │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python Flask | API endpoints, data processing |
| **Data** | Pandas, OWID CSV | Emissions data |
| **Frontend** | HTML/CSS/JavaScript | Dashboard UI |
| **Charts** | Plotly.js | Interactive visualizations |
| **AI** | OpenRouter API | Natural language insights |
| **Dev Assistant** | Opencode Big Pickle | HTML/CSS/JS implementation |
| **Fonts** | Plus Jakarta Sans, Outfit, DM Mono | Typography |

---

## API Reference

### Core Endpoints

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/` | GET | — | Main dashboard |
| `/api/countries` | GET | — | List available countries |
| `/api/summary/<code>` | GET | `code`: ISO code | Country summary |
| `/api/trend/<code>` | GET | `code`, `metric`: co2/ghg | Trend statistics |
| `/api/comparison/<code>` | GET | `code`, `tier`, `year` | Comparison data |
| `/api/emission-sources/<code>` | GET | `code`, `mode`, `year` | Source breakdown |

### AI Endpoints

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/ai/trend/<code>` | GET | `code`, `metric` | Trend insight |
| `/api/ai/comparison/<code>` | GET | `code`, `tier` | Comparison insight |
| `/api/ai/sources/<code>` | GET | `code`, `mode` | Sources insight |
| `/api/ai/reflection/<code>` | GET | `code` | Climate reflection |

### Example API Calls

```bash
# Get Egypt summary
curl http://localhost:5000/api/summary/EGY

# Get comparison data for 2015
curl "http://localhost:5000/api/comparison/EGY?tier=peers&year=2015"

# Get emission sources in GHG mode
curl "http://localhost:5000/api/emission-sources/EGY?mode=ghg&year=2023"
```

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd emission_trend_analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key (optional, for AI features)
   ```

5. **Run the dashboard**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

### Environment Variables

Create a `.env` file:

```env
# OpenRouter API Key (optional - AI features won't work without it)
# Get free key at: https://openrouter.ai/
OPENROUTER_API_KEY=your_api_key_here

# Optional: Flask configuration
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## Data Sources & Citations

### Primary Data

| Source | Description | URL |
|--------|-------------|-----|
| **Our World in Data** | CO₂ & GHG emissions dataset | [github.com/owid/co2-data](https://github.com/owid/co2-data) |
| **Global Carbon Project** | Emissions data provider | [globalcarbonproject.org](https://www.globalcarbonproject.org) |
| **UNFCCC** | GHG inventories | [unfccc.int](https://unfccc.int) |

### Economic Data

| Source | Description | Used For |
|--------|-------------|----------|
| **World Bank** | GDP per capita (nominal USD) | Global Context panel |
| **UNDP** | Human Development Index (HDI) | HDI-adjusted emissions |

### Policy References

| Source | Description |
|--------|-------------|
| **IEA** | World Energy Outlook 2023 |
| **IPCC** | AR6 Climate Change 2023 Synthesis Report |
| **ICAP** | Emissions Trading Worldwide Status Report 2023 |
| **UNEP** | Emissions Gap Report 2024 |
| **CCPI** | Climate Change Performance Index 2024 |

---

## Climate Policy Context

### Egypt's Climate Commitments

- **COP27 Host (2022)**: Egypt hosted the UN Climate Change Conference in Sharm El-Sheikh
- **NDC Target**: 42% renewable electricity by 2035
- **Zohr Gas Field**: Discovery (2015) made Egypt a net gas exporter by 2019
- **Vulnerability**: One of world's most climate-vulnerable coastal zones

### Historical Context

| Event | Year | Impact on Emissions |
|-------|------|---------------------|
| Arab Spring | 2011 | Political instability, growth slowdown |
| IMF Currency Reform | 2016 | Economic adjustment, energy reforms |
| Zohr Gas Online | 2017 | Natural gas surplus, exports begin |
| COVID-19 | 2020 | Global emissions dip |
| COP27 | 2022 | International climate spotlight |

---

## Project Structure

```
emission_trend_analysis/
├── app.py                 # Flask application & routes
├── data_utils.py          # Data processing functions
├── ai_service.py          # OpenRouter AI integration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
│
├── data/
│   ├── cache/
│   │   └── owid_emissions.csv  # OWID data (cached)
│   ├── fetch_data.ipynb   # Data fetching notebook
│   ├── analysis.ipynb     # Analysis notebook
│   └── countries.ipynb    # Country config notebook
│
├── templates/
│   ├── base.html          # Base template (CSS, layout)
│   └── index.html         # Main dashboard page
│
├── static/
│   └── egypt_hero.jpg     # Hero background image
│
├── CODE_EXPLANATION.md    # Technical documentation
└── README.md             # This file
```

---

## Key Features Explained

### CO₂ vs GHG Toggle

The dashboard supports two emission views:

- **CO₂ Mode**: Only carbon dioxide emissions
- **GHG Mode**: Full greenhouse gas inventory including methane (CH₄) and nitrous oxide (N₂O)

**Non-CO₂ Calculation:**
```
Other GHGs = Total GHG (excl. LUCF) - (Coal + Oil + Gas + Cement + Flaring)
```

Calculated using GWP100 metric via OWID/IPCC methodology.

### HDI-Adjusted Emissions

This metric combines CO₂ per capita with Human Development Index to assess climate justice:

```
HDI-Adjusted = CO₂ per capita / HDI Score
```

**Lower values = more efficient human development per unit of CO₂**

Example values (2023):
| Country | CO₂/capita | HDI | Adjusted |
|---------|------------|-----|----------|
| Egypt | 2.19 | 0.731 | 3.0 |
| India | 2.13 | 0.645 | 3.3 |

### CAGR Calculation

Compound Annual Growth Rate calculated from actual data:

```
CAGR = (End Value / Start Value)^(1/years) - 1
```

Not hardcoded estimates — computed from OWID time series data.

---

## Development Notes

### Adding New Countries

1. Update `data_utils.py` with country code and HDI score
2. Add to `TIER_COMPARISONS` for comparison groups
3. Create country description in `index.html` `countryDescriptions` object

### Modifying Charts

All Plotly charts use a shared configuration (`PB` object) in `index.html`:

```javascript
const PB = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Plus Jakarta Sans', ... },
    margin: { t: 16, r: 16, b: 48, l: 56 },
    // ...
};
```

### AI Service

The AI service uses free-tier models via OpenRouter. Rate limiting (2-second intervals) prevents API overuse. Prompts are optimized for concise, actionable insights.

---

## License

This project is for educational and research purposes. Data sourced from [Our World in Data](https://ourworldindata.org/) under their license terms, and Human Development Index data from the [United Nations Development Programme (UNDP)](https://hdr.undp.org/data-center/human-development-index).

---

## Acknowledgments

- **Main Data**: [Our World in Data](https://ourworldindata.org/) - Global Carbon Project
- **HDI Data**: [United Nations Development Programme (UNDP)](https://hdr.undp.org/data-center/human-development-index) - Human Development Index & PHDI
- **AI**: [OpenRouter](https://openrouter.ai/) - Free tier LLM access for dashboard insights
- **AI Development Assistant**: [Opencode Big Pickle](https://opencode.ai) - Used for HTML, CSS, and JavaScript implementation assistance
- **Visualizations**: [Plotly](https://plotly.com/javascript/)
- **Fonts**: [Google Fonts](https://fonts.google.com/) - Plus Jakarta Sans, Outfit, DM Mono

---

<p align="center">
  <strong>Built for TISS Mumbai - Climate Change, Sustainability & Development Assignment</strong>
</p>
