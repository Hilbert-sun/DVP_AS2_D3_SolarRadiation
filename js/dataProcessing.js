// Data processing helpers for the King's Park solar radiation narrative.
// Uses the global D3 v7 bundle loaded in index.html.

const DATA_PATH = "data/daily_KP_all_merged.csv";

function requireD3() {
  if (!globalThis.d3) {
    throw new Error("D3 library not found. Ensure d3.v7 is loaded first.");
  }
  return globalThis.d3;
}

function toNumber(value) {
  const num = Number.parseFloat(value);
  return Number.isFinite(num) ? num : null;
}

function normalizeSeason(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const season = String(value).trim().toLowerCase();
  if (season === "fall") {
    return "autumn";
  }
  return season;
}

function getLowerCaseMap(row) {
  const map = {};
  Object.entries(row).forEach(([key, value]) => {
    map[key.toLowerCase()] = value;
  });
  return map;
}

export function parseClimateRow(row) {
  const lower = getLowerCaseMap(row);

  let date = null;
  if (lower.date) {
    const parsed = new Date(lower.date);
    date = Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  const parsedYear = Number.parseInt(lower.year, 10);
  const parsedMonth = Number.parseInt(lower.month, 10);

  const year = Number.isFinite(parsedYear) ? parsedYear : date?.getFullYear() ?? null;
  const month = Number.isFinite(parsedMonth) ? parsedMonth : date ? date.getMonth() + 1 : null;

  const parsed = {
    ...row,
    date,
    year,
    month,
    season: normalizeSeason(lower.season),
    GSR: toNumber(lower.gsr),
    RF: toNumber(lower.rf),
    SUN: toNumber(lower.sun),
    RH: toNumber(lower.rh),
  };

  return addSeason(parsed);
}

export function addSeason(row) {
  if (!row) {
    return row;
  }

  if (row.season) {
    row.season = normalizeSeason(row.season);
    return row;
  }

  const month = Number.parseInt(row.month, 10);
  if (!Number.isFinite(month)) {
    return row;
  }

  if (month === 12 || month === 1 || month === 2) {
    row.season = "winter";
  } else if (month >= 3 && month <= 5) {
    row.season = "spring";
  } else if (month >= 6 && month <= 8) {
    row.season = "summer";
  } else if (month >= 9 && month <= 11) {
    row.season = "autumn";
  }

  return row;
}

export async function loadData() {
  const d3 = requireD3();
  try {
    return await d3.csv(DATA_PATH, parseClimateRow);
  } catch (error) {
    console.error("Failed to load climate data:", error);
    throw error;
  }
}

export function filterByYearRange(data, startYear, endYear) {
  if (!Array.isArray(data)) {
    throw new Error("filterByYearRange expects an array of data rows.");
  }

  const start = Number(startYear);
  const end = Number(endYear);

  if (!Number.isFinite(start) || !Number.isFinite(end)) {
    console.warn("Year range filter skipped due to invalid bounds.");
    return data;
  }

  return data.filter((row) => Number.isFinite(row.year) && row.year >= start && row.year <= end);
}

export function filterBySeason(data, selectedSeason) {
  if (!Array.isArray(data)) {
    throw new Error("filterBySeason expects an array of data rows.");
  }

  if (!selectedSeason || selectedSeason === "all") {
    return data;
  }

  const season = normalizeSeason(selectedSeason);
  if (!season) {
    console.warn("Season filter skipped due to invalid selection.");
    return data;
  }

  return data.filter((row) => row.season === season);
}

function meanOrNull(values) {
  const d3 = requireD3();
  const filtered = values.filter((value) => Number.isFinite(value));
  return filtered.length ? d3.mean(filtered) : null;
}

export function computeAnnualSummary(data) {
  const d3 = requireD3();
  if (!Array.isArray(data)) {
    throw new Error("computeAnnualSummary expects an array of data rows.");
  }

  return d3
    .rollups(
      data.filter((row) => Number.isFinite(row.year)),
      (rows) => ({
        gsrAvg: meanOrNull(rows.map((row) => row.GSR)),
        rfAvg: meanOrNull(rows.map((row) => row.RF)),
        sunAvg: meanOrNull(rows.map((row) => row.SUN)),
        rhAvg: meanOrNull(rows.map((row) => row.RH)),
        count: rows.length,
      }),
      (row) => row.year
    )
    .map(([year, summary]) => ({ year, ...summary }))
    .sort((a, b) => d3.ascending(a.year, b.year));
}

export function computeMonthlySummary(data) {
  const d3 = requireD3();
  if (!Array.isArray(data)) {
    throw new Error("computeMonthlySummary expects an array of data rows.");
  }

  return d3
    .rollups(
      data.filter((row) => Number.isFinite(row.month)),
      (rows) => ({
        gsrAvg: meanOrNull(rows.map((row) => row.GSR)),
        rfAvg: meanOrNull(rows.map((row) => row.RF)),
        sunAvg: meanOrNull(rows.map((row) => row.SUN)),
        rhAvg: meanOrNull(rows.map((row) => row.RH)),
        count: rows.length,
      }),
      (row) => row.month
    )
    .map(([month, summary]) => ({ month, ...summary }))
    .sort((a, b) => d3.ascending(a.month, b.month));
}

export function computeExtremeThreshold(data) {
  const d3 = requireD3();
  if (!Array.isArray(data)) {
    throw new Error("computeExtremeThreshold expects an array of data rows.");
  }

  const values = data
    .map((row) => row.GSR)
    .filter((value) => Number.isFinite(value))
    .sort(d3.ascending);

  if (!values.length) {
    return null;
  }

  return d3.quantile(values, 0.95);
}

export function markExtremeDays(data) {
  const threshold = computeExtremeThreshold(data);
  return data.map((row) => ({
    ...row,
    isExtreme: Number.isFinite(row.GSR) && threshold !== null ? row.GSR >= threshold : false,
  }));
}
