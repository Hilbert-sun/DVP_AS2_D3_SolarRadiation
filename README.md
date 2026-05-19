# When Sunshine Meets Rain: Understanding Solar Radiation Patterns at King's Park, Hong Kong

## Description
An interactive narrative visualisation built with D3.js to explain how solar radiation at King's Park relates to sunshine duration, rainfall, relative humidity, seasonality, and extreme solar radiation days. The story is organised into five steps with coordinated filters and tooltips to support evidence-based planning.

## Target Audience
Hong Kong urban planners and environmental policy advisors.

## Data Files Used
- `data/daily_KP_all_merged.csv` (main dataset)

## Variables
- **GSR**: Global Solar Radiation
- **RF**: Rainfall
- **SUN**: Sunshine Duration
- **RH**: Relative Humidity
- **Date / Year / Month**: Date components for temporal analysis
- **Season**: Derived if not present (Winter: Dec–Feb, Spring: Mar–May, Summer: Jun–Aug, Autumn: Sep–Nov)

## How to Run Locally
1. Ensure Python is installed.
2. From the project root, run:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in a browser.

## Interaction Guide
- **Story steps**: Use the left sidebar buttons to move through the narrative.
- **Year range**: Adjust the slider to focus on recent or full-range trends.
- **Season filter**: Toggle seasonal subsets (Winter, Spring, Summer, Autumn).
- **Extreme days**: Highlight top 5% GSR events.
- **Reset**: Restore default filters.
- **Tooltips**: Hover charts to inspect details.

## File Structure
```
.
├── css/
│   └── style.css
├── data/
│   └── daily_KP_all_merged.csv
├── docs/
│   └── technical_requirements.md
├── js/
│   ├── annualTrend.js
│   ├── dataProcessing.js
│   ├── extremeDays.js
│   ├── main.js
│   ├── scatterDriver.js
│   ├── seasonalPattern.js
│   └── storyController.js
└── index.html
```

## Technical Implementation
- **D3.js v7** for rendering charts and interactive tooltips.
- **Modular JavaScript** to separate data processing, story control, and visual modules.
- **Standardisation** used where variables have different units (e.g., annual GSR vs rainfall trends).
- **Responsive layout** with a structured header, story sidebar, main chart area, insight panel, and control bar.

## Limitations
- Station-level data does not capture neighbourhood microclimates or rooftop shading.
- Extreme day threshold uses a global top 5% of GSR, which may mask intra-season variability.
- Narrative focus prioritises clarity over full meteorological attribution.

## AI Declaration (Placeholder)
_To be completed by the author._
