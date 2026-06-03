// Story-level helpers for navigation and narrative content.

function resolveContainer(containerSelector) {
  if (typeof containerSelector === "string") {
    return document.querySelector(containerSelector);
  }
  if (containerSelector instanceof Element) {
    return containerSelector;
  }
  return null;
}

export function getInsightText(step) {
  switch (Number(step)) {
    case 1:
      return (
        "Annual global solar radiation and rainfall show an inverse but variable relationship " +
        "across the record. Urban planners should account for this inter-annual variability " +
        "when forecasting long-term solar generation capacity and designing climate-resilient " +
        "infrastructure."
      );
    case 2:
      return (
        "Solar radiation, sunshine duration, rainfall, and humidity display a coherent " +
        "seasonal cycle with marked peaks and troughs. This seasonal rhythm is essential for " +
        "planning solar installations and mitigating weather-dependent generation shortfalls " +
        "during high-humidity or rainy months."
      );
    case 3:
      return (
        "Sunshine duration has the strongest observed association with solar radiation in daily data. " +
        "The extreme-day highlight keeps rare high-radiation events visible inside the full daily " +
        "context, helping policy advisors compare peak opportunities with normal operating conditions."
      );
    case 4:
      return (
        "The top 5% solar radiation days are concentrated in summer and are characterised most clearly " +
        "by high sunshine duration and very low rainfall. Relative humidity is only slightly lower on " +
        "average. Click any top-10 date to trace that event back to the multivariate scatterplot."
      );
    case 5:
      return (
        "This analysis synthesises five evidence-based insights for solar planning in Hong Kong. " +
        "The takeaways below translate the observed climate patterns into actionable design and " +
        "policy recommendations."
      );
    default:
      return "Select a story step to see its key insight.";
  }
}

export function updateActiveStep(step) {
  const buttons = document.querySelectorAll(".story-steps button");
  buttons.forEach((button) => {
    const isActive = Number(button.dataset.step) === Number(step);
    button.classList.toggle("is-active", isActive);
    if (isActive) {
      button.setAttribute("aria-current", "step");
    } else {
      button.removeAttribute("aria-current");
    }
  });
}

export function updateInsightPanel(step) {
  const panel = document.getElementById("insight-panel");
  if (!panel) {
    return;
  }

  panel.innerHTML = "";
  const heading = document.createElement("h2");
  heading.textContent = "Insight Panel";
  const paragraph = document.createElement("p");
  paragraph.textContent = getInsightText(step);
  panel.appendChild(heading);
  panel.appendChild(paragraph);
}

export function renderPlanningTakeaway(containerSelector, data, state) {
  const container = resolveContainer(containerSelector);
  if (!container) {
    console.error("Planning takeaway container not found.");
    return;
  }

  container.innerHTML = "";

  const heading = document.createElement("h3");
  heading.textContent = "Planning takeaways for Hong Kong";
  container.appendChild(heading);

  const cardWrapper = document.createElement("div");
  cardWrapper.className = "takeaway-cards";

  const cards = [
    {
      title: "Solar potential is seasonally structured",
      body:
        "Design solar strategies that align with the strongest seasonal radiation windows.",
    },
    {
      title: "Sunshine duration is the clearest association",
      body:
        "Use sunshine availability as the primary indicator when screening solar sites.",
    },
    {
      title: "Wet conditions reduce solar opportunity",
      body:
        "Plan for reduced output during rainy periods and treat humidity as supporting context.",
    },
    {
      title: "Extreme opportunities cluster in summer",
      body:
        "Use the high-sunshine, low-rainfall extreme-day pattern to plan seasonal capacity.",
    },
  ];

  cards.forEach((card) => {
    const cardEl = document.createElement("div");
    cardEl.className = "takeaway-card";
    const title = document.createElement("h4");
    title.textContent = card.title;
    const body = document.createElement("p");
    body.textContent = card.body;
    cardEl.appendChild(title);
    cardEl.appendChild(body);
    cardWrapper.appendChild(cardEl);
  });

  container.appendChild(cardWrapper);

  const notes = document.createElement("div");
  notes.className = "takeaway-notes";

  const dataSource = document.createElement("p");
  dataSource.innerHTML =
    "<strong>Data source:</strong> King's Park daily climate observations (data/daily_KP_all_merged.csv).";

  const limitation = document.createElement("p");
  limitation.innerHTML =
    "<strong>Limitation:</strong> Station-level measurements do not capture neighborhood shading or rooftop microclimates.";

  const futureWork = document.createElement("p");
  futureWork.innerHTML =
    "<strong>Future work:</strong> Combine solar radiation with urban form and demand forecasts to refine siting guidance.";

  notes.appendChild(dataSource);
  notes.appendChild(limitation);
  notes.appendChild(futureWork);

  container.appendChild(notes);
}

// Optional hook for main.js when available.
export function updateStoryStep({ state, chartArea }) {
  updateActiveStep(state?.currentStep);
  updateInsightPanel(state?.currentStep);

  if (state?.currentStep === 5 && chartArea) {
    renderPlanningTakeaway(chartArea, null, state);
  }
}
