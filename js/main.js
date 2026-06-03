import {
  loadData,
  filterByYearRange,
  filterBySeason,
  markExtremeDays,
} from "./dataProcessing.js";

let renderAnnualTrend;
let renderSeasonalPattern;
let renderScatterDriver;
let renderExtremeDays;
let updateStoryStep;

const state = {
  currentStep: 1,
  startYear: null,
  endYear: null,
  selectedSeason: "all",
  showExtremeOnly: false,
  selectedExtremeDate: null,
};

let rawData = [];
let minYear = null;
let maxYear = null;

const chartArea = document.getElementById("chart-area");
const insightPanel = document.getElementById("insight-panel");
const startYearInput = document.getElementById("start-year-input");
const endYearInput = document.getElementById("end-year-input");
const yearWarning = document.getElementById("year-warning");
const seasonSelect = document.getElementById("season-filter");
const extremeToggle = document.getElementById("extreme-toggle");
const resetButton = document.getElementById("reset-filters");
const stepButtons = Array.from(document.querySelectorAll(".story-steps button"));

function renderPlaceholder(title, detail) {
  chartArea.innerHTML = "";
  const placeholder = document.createElement("div");
  placeholder.className = "chart-placeholder";
  placeholder.textContent = detail ? `${title} — ${detail}` : title;
  chartArea.appendChild(placeholder);
}

function updateInsightCopy(message) {
  insightPanel.innerHTML = "";
  const heading = document.createElement("h2");
  heading.textContent = "Insight Panel";
  const paragraph = document.createElement("p");
  paragraph.textContent = message;
  insightPanel.appendChild(heading);
  insightPanel.appendChild(paragraph);
}

function showError(message) {
  renderPlaceholder("Data load error", message);
  updateInsightCopy("Check the CSV path or file format, then reload the page.");
}

function updateYearLabel() {
  if (!startYearInput || !endYearInput) {
    return;
  }
  startYearInput.value = state.startYear;
  endYearInput.value = state.endYear;
  yearWarning.style.display = "none";
  yearWarning.textContent = "";
}

function updateStepButtons() {
  stepButtons.forEach((button) => {
    const step = Number(button.dataset.step);
    const isActive = step === state.currentStep;
    button.classList.toggle("is-active", isActive);
    if (isActive) {
      button.setAttribute("aria-current", "step");
    } else {
      button.removeAttribute("aria-current");
    }
  });
}

function getFilteredData() {
  let filtered = filterByYearRange(rawData, state.startYear, state.endYear);
  filtered = filterBySeason(filtered, state.selectedSeason);
  return markExtremeDays(filtered);
}

function handleExtremeDaySelect(dateKey) {
  if (!dateKey) {
    return;
  }

  updateState({
    currentStep: 3,
    selectedExtremeDate: dateKey,
    showExtremeOnly: true,
  });

  if (extremeToggle) {
    extremeToggle.checked = true;
  }
}

function renderCurrentStep() {
  updateStepButtons();
  updateYearLabel();

  const data = getFilteredData();
  chartArea.innerHTML = "";

  switch (state.currentStep) {
    case 1:
      renderAnnualTrend(chartArea, data, state, insightPanel);
      break;
    case 2:
      renderSeasonalPattern(chartArea, data, state, insightPanel);
      break;
    case 3:
      renderScatterDriver(chartArea, data, state, insightPanel);
      break;
    case 4:
      renderExtremeDays(chartArea, data, {
        ...state,
        onSelectExtremeDay: handleExtremeDaySelect,
      });
      break;
    case 5:
      renderPlaceholder("Planning takeaway", "Narrative cards coming soon.");
      updateInsightCopy("Planning recommendations will be summarized here.");
      break;
    default:
      renderPlaceholder("Story step not found", "Select a step to continue.");
      updateInsightCopy("Choose a story step from the sidebar.");
  }

  if (typeof updateStoryStep === "function") {
    updateStoryStep({ state, data, chartArea, insightPanel });
  }
}

function updateState(partial) {
  Object.assign(state, partial);
  renderCurrentStep();
}

function handleReset() {
  state.currentStep = 1;
  state.startYear = minYear;
  state.endYear = maxYear;
  state.selectedSeason = "all";
  state.showExtremeOnly = false;
  state.selectedExtremeDate = null;

  if (startYearInput) {
    startYearInput.value = minYear;
  }
  if (endYearInput) {
    endYearInput.value = maxYear;
  }
  if (seasonSelect) {
    seasonSelect.value = "all";
  }
  if (extremeToggle) {
    extremeToggle.checked = false;
  }

  renderCurrentStep();
}

function validateYearRange(start, end) {
  const startYear = Number(start);
  const endYear = Number(end);

  if (!Number.isFinite(startYear) || !Number.isFinite(endYear)) {
    return { valid: false, message: "Invalid year values." };
  }

  if (startYear > endYear) {
    return { valid: false, message: "Start year cannot be greater than end year." };
  }

  return { valid: true };
}

function attachEventListeners() {
  stepButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const step = Number(button.dataset.step);
      if (Number.isFinite(step)) {
        updateState({ currentStep: step });
      }
    });
  });

  if (startYearInput) {
    startYearInput.addEventListener("change", (event) => {
      const validation = validateYearRange(event.target.value, endYearInput.value);
      if (!validation.valid) {
        yearWarning.textContent = validation.message;
        yearWarning.style.display = "block";
        startYearInput.value = state.startYear;
        return;
      }
      yearWarning.style.display = "none";
      updateState({ startYear: Number(event.target.value) });
    });
  }

  if (endYearInput) {
    endYearInput.addEventListener("change", (event) => {
      const validation = validateYearRange(startYearInput.value, event.target.value);
      if (!validation.valid) {
        yearWarning.textContent = validation.message;
        yearWarning.style.display = "block";
        endYearInput.value = state.endYear;
        return;
      }
      yearWarning.style.display = "none";
      updateState({ endYear: Number(event.target.value) });
    });
  }

  if (seasonSelect) {
    seasonSelect.addEventListener("change", (event) => {
      updateState({ selectedSeason: event.target.value });
    });
  }

  if (extremeToggle) {
    extremeToggle.addEventListener("change", (event) => {
      updateState({
        showExtremeOnly: event.target.checked,
        selectedExtremeDate: event.target.checked ? state.selectedExtremeDate : null,
      });
    });
  }

  if (resetButton) {
    resetButton.addEventListener("click", handleReset);
  }
}

async function loadChartModules() {
  const fallback =
    (title) =>
    (container) => {
      container.innerHTML = "";
      const placeholder = document.createElement("div");
      placeholder.className = "chart-placeholder";
      placeholder.textContent = `${title} chart placeholder`;
      container.appendChild(placeholder);
      updateInsightCopy("Chart modules will be wired in the next step.");
    };

  try {
    const module = await import("./annualTrend.js?v=20260603-report-v2");
    renderAnnualTrend = module.renderAnnualTrend || fallback("Annual trend");
  } catch (error) {
    console.warn("annualTrend.js not available yet.", error);
    renderAnnualTrend = fallback("Annual trend");
  }

  try {
    const module = await import("./seasonalPattern.js?v=20260603-report-v2");
    renderSeasonalPattern =
      module.renderSeasonalPattern || fallback("Seasonal pattern");
  } catch (error) {
    console.warn("seasonalPattern.js not available yet.", error);
    renderSeasonalPattern = fallback("Seasonal pattern");
  }

  try {
    const module = await import("./scatterDriver.js?v=20260603-report-v2");
    renderScatterDriver =
      module.renderScatterDriver || fallback("Sunshine relationship");
  } catch (error) {
    console.warn("scatterDriver.js not available yet.", error);
    renderScatterDriver = fallback("Sunshine relationship");
  }

  try {
    const module = await import("./extremeDays.js?v=20260603-report-v2");
    renderExtremeDays = module.renderExtremeDays || fallback("Extreme days");
  } catch (error) {
    console.warn("extremeDays.js not available yet.", error);
    renderExtremeDays = fallback("Extreme days");
  }

  try {
    const module = await import("./storyController.js?v=20260603-report-v2");
    updateStoryStep = module.updateStoryStep || module.renderStoryStep || null;
  } catch (error) {
    console.warn("storyController.js not available yet.", error);
    updateStoryStep = null;
  }
}

async function initialize() {
  attachEventListeners();

  await loadChartModules();

  try {
    rawData = await loadData();
  } catch (error) {
    showError("Unable to load daily_KP_all_merged.csv.");
    return;
  }

  const years = rawData
    .map((row) => row.year)
    .filter((year) => Number.isFinite(year))
    .sort((a, b) => a - b);

  if (!years.length) {
    showError("No valid year values found in the dataset.");
    return;
  }

  minYear = years[0];
  maxYear = years[years.length - 1];
  state.startYear = minYear;
  state.endYear = maxYear;

  if (startYearInput) {
    startYearInput.min = String(minYear);
    startYearInput.max = String(maxYear);
    startYearInput.value = String(minYear);
  }
  if (endYearInput) {
    endYearInput.min = String(minYear);
    endYearInput.max = String(maxYear);
    endYearInput.value = String(maxYear);
  }

  renderCurrentStep();
}

window.addEventListener("DOMContentLoaded", initialize);
