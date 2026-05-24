# When Sunshine Meets Rain: Understanding Solar Radiation Patterns at King's Park, Hong Kong

## Description
An interactive D3.js narrative visualisation explaining how solar radiation at King's Park relates to sunshine duration, rainfall, relative humidity, seasonality, and extreme solar radiation days. The story is organised into five guided steps with coordinated filters, tooltips, and linked highlighting between the extreme-day table and the sunshine-GSR scatterplot.

## Target Audience
Hong Kong urban planners and environmental policy advisors.

## Data Files Used
- `data/daily_KP_all_merged.csv` is the main dataset used by the application.
- The separate cleaned source files are retained in `data/` for transparency.

## Variables
- **GSR**: Global Solar Radiation
- **RF**: Rainfall
- **SUN**: Sunshine Duration
- **RH**: Relative Humidity
- **Date / Year / Month**: Time fields used for trend and seasonal analysis
- **Season**: Derived in JavaScript when not present: Winter is Dec-Feb, Spring is Mar-May, Summer is Jun-Aug, Autumn is Sep-Nov.

## How to Run Locally
1. Ensure Python is installed.
2. From the project root, run:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in a browser.

The application reads data from local CSV files. It does not require a database, server-side code, or remote data API.

## Interaction Guide
- **Story steps**: Use the left sidebar buttons to move through the narrative.
- **Year range**: Enter a start and end year to focus the analysis period.
- **Season filter**: Focus on all seasons or one seasonal subset.
- **Extreme days toggle**: Highlight top 5% GSR days while preserving the broader daily context.
- **Linked extreme-day tracing**: In Step 4, click a top-10 extreme date to jump to Step 3 and highlight that same day in the SUN-GSR scatterplot.
- **Tooltips**: Hover chart elements to inspect detailed values.
- **Reset**: Restore default filters and clear linked selections.

## File Structure
```text
.
|-- css/
|   `-- style.css
|-- data/
|   |-- daily_KP_all_merged.csv
|   |-- daily_KP_GSR_clean.csv
|   |-- daily_KP_RF_clean.csv
|   |-- daily_KP_RH_clean.csv
|   `-- daily_KP_SUN_clean.csv
|-- docs/
|   |-- copilot_notes.md
|   `-- technical_requirements.md
|-- js/
|   |-- annualTrend.js
|   |-- dataProcessing.js
|   |-- extremeDays.js
|   |-- lib/
|   |   `-- d3.v7.min.js
|   |-- main.js
|   |-- scatterDriver.js
|   |-- seasonalPattern.js
|   `-- storyController.js
|-- index.html
`-- README.md
```

## Technical Implementation
- **D3.js v7** is included locally in `js/lib/` and renders SVG charts, legends, axes, tooltips, and interaction states.
- **Modular JavaScript** separates data parsing, state management, story control, and chart rendering.
- **Local CSV loading** keeps the submission reproducible for markers.
- **Standardisation** is used where variables have different units, such as annual GSR versus rainfall trends.
- **Linked interaction** connects the extreme-day evidence table with the multivariate scatterplot, supporting traceability from summary evidence to individual records.
- **Responsive layout** uses a structured header, story navigation, main chart area, insight panel, and control bar.

## Limitations
- Station-level data does not capture neighbourhood microclimates, rooftop geometry, or shading.
- Extreme day threshold uses the top 5% of GSR within the current filtered selection.
- The narrative prioritises planning clarity over full meteorological attribution.

## AI Declaration
Generative AI tools were used to support planning, wording, and code development. ChatGPT helped structure implementation ideas and draft explanatory text. GitHub Copilot assisted with D3.js, HTML, CSS, and JavaScript code completion. All generated material was reviewed, edited, tested, and integrated by the student before submission.
