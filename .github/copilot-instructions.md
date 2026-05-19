# GitHub Copilot Instructions

This is a FIT5147 Data Visualisation Project.

Build a standalone interactive narrative visualisation using:
- D3.js v7
- HTML5
- CSS3
- Vanilla JavaScript
- Local CSV data

Do not use:
- R Shiny
- R Markdown
- Python dashboard
- Tableau
- Observable-only notebook
- C3.js, dimple.js, or other high-level D3 wrapper libraries

Project topic:
Solar radiation patterns at King's Park, Hong Kong.

Main variables:
- GSR: Global Solar Radiation
- RF: Rainfall
- SUN: Sunshine Duration
- RH: Relative Humidity

Target audience:
Hong Kong urban planners and environmental policy advisors.

Narrative steps:
1. Long-term climate context
2. Seasonal rhythm
3. Sunshine as the main driver of solar radiation
4. Extreme solar radiation days
5. Planning takeaway

Interface layout:
- Header
- Story step sidebar
- Main visualisation area
- Insight panel
- Control bar

Controls:
- Year range selector
- Season filter
- Extreme-day toggle
- Reset button
- Hover tooltip

Use the main data file:
data/daily_KP_all_merged.csv

Code requirements:
- Keep files modular.
- Use clear function names.
- Add comments.
- Clear SVG before re-rendering.
- Make charts readable and suitable for academic assessment.
- Prioritise narrative clarity over decorative complexity.