# Technical Requirements

## Project Title
When Sunshine Meets Rain: Understanding Solar Radiation Patterns at King's Park, Hong Kong

## Goal
Create an interactive narrative visualisation using D3.js to communicate how solar radiation at King's Park is related to sunshine duration, rainfall, relative humidity, seasonality, and extreme solar radiation days.

## Audience
Hong Kong urban planners and environmental policy advisors.

## Data
Use data/daily_KP_all_merged.csv as the main dataset.

Expected fields:
- date or Date
- year or Year
- month or Month
- GSR
- RF
- SUN
- RH

If season is missing, generate it in JavaScript:
- Winter: Dec-Feb
- Spring: Mar-May
- Summer: Jun-Aug
- Autumn: Sep-Nov

Extreme solar days are defined as the top 5% of GSR values.

## Story Steps

### Step 1: Long-term climate context
Show annual trend of GSR and rainfall.

### Step 2: Seasonal rhythm
Show monthly average patterns of GSR, RF, SUN, and RH.

### Step 3: Sunshine driver
Show scatterplot:
- x-axis: SUN
- y-axis: GSR
- point size: RF
- point colour: RH

### Step 4: Extreme solar days
Show top 5% GSR days, seasonal distribution, and summary cards.

### Step 5: Planning takeaway
Show three takeaway cards for planners.

## Interactions
- Click story step buttons.
- Select year range.
- Select season.
- Toggle extreme solar days.
- Hover for tooltip.
- Reset all filters.

## Technical stack
- D3.js v7
- HTML
- CSS
- Vanilla JavaScript