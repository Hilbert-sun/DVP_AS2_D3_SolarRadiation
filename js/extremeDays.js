import { computeExtremeThreshold } from "./dataProcessing.js";

function requireD3() {
  if (!globalThis.d3) {
    throw new Error("D3 library not found. Ensure d3.v7 is loaded first.");
  }
  return globalThis.d3;
}

function resolveContainer(containerSelector) {
  if (typeof containerSelector === "string") {
    return document.querySelector(containerSelector);
  }
  if (containerSelector instanceof Element) {
    return containerSelector;
  }
  return null;
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(2) : "N/A";
}

function renderSummaryCards(container, summary) {
  const cards = document.createElement("div");
  cards.className = "extreme-cards";

  const entries = [
    { label: "Extreme days", value: summary.count, unit: "" },
    { label: "Average GSR", value: formatNumber(summary.gsrAvg), unit: "MJ/m²" },
    { label: "Average SUN", value: formatNumber(summary.sunAvg), unit: "hours" },
    { label: "Average RF", value: formatNumber(summary.rfAvg), unit: "mm" },
    { label: "Average RH", value: formatNumber(summary.rhAvg), unit: "%" },
  ];

  entries.forEach((entry) => {
    const card = document.createElement("div");
    card.className = "extreme-card";
    
    const title = document.createElement("div");
    title.className = "extreme-card-title";
    title.textContent = entry.label;
    
    const valueContainer = document.createElement("div");
    valueContainer.className = "extreme-card-value-container";
    
    const value = document.createElement("div");
    value.className = "extreme-card-value";
    value.textContent = entry.value;
    
    const unit = document.createElement("div");
    unit.className = "extreme-card-unit";
    unit.textContent = entry.unit;
    
    valueContainer.appendChild(value);
    valueContainer.appendChild(unit);
    
    card.appendChild(title);
    card.appendChild(valueContainer);
    cards.appendChild(card);
  });

  container.appendChild(cards);
}

function getDateKey(row, d3) {
  if (row?.date instanceof Date) {
    return d3.timeFormat("%Y-%m-%d")(row.date);
  }
  return row?.date ? String(row.date).slice(0, 10) : "";
}

function renderTopTable(container, rows, d3, onSelectExtremeDay) {
  const table = document.createElement("table");
  table.className = "extreme-table";

  const headerLabels = ["Date", "Season", "GSR (MJ/m²)", "SUN (hours)", "RF (mm)", "RH (%)"];
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  headerLabels.forEach((label) => {
    const th = document.createElement("th");
    th.textContent = label;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  const timeFormat = d3.timeFormat("%Y-%m-%d");

  rows.forEach((row, index) => {
    const tr = document.createElement("tr");
    if (index % 2 === 0) {
      tr.classList.add("zebra-row");
    }
    const dateLabel = getDateKey(row, d3) || "Unknown";

    const cells = [
      dateLabel,
      row.season || "Unknown",
      formatNumber(row.GSR),
      formatNumber(row.SUN),
      formatNumber(row.RF),
      formatNumber(row.RH),
    ];

    cells.forEach((value, colIndex) => {
      const td = document.createElement("td");
      if (colIndex === 0 && typeof onSelectExtremeDay === "function") {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "date-link";
        button.textContent = value;
        button.setAttribute(
          "aria-label",
          `Highlight ${value} in the sunshine-GSR scatterplot`
        );
        button.addEventListener("click", () => onSelectExtremeDay(dateLabel));
        td.appendChild(button);
      } else {
        td.textContent = value;
      }
      if (colIndex > 1) {
        td.className = "numeric";
      }
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  container.appendChild(table);
}

export function renderExtremeDays(containerSelector, data, state) {
  const d3 = requireD3();
  const container = resolveContainer(containerSelector);

  if (!container) {
    console.error("Extreme days container not found.");
    return;
  }

  container.innerHTML = "";
  container.style.position = "relative";

  try {
    const threshold = computeExtremeThreshold(data);
    if (!Number.isFinite(threshold)) {
      container.textContent = "No extreme days available for this selection.";
      return;
    }

    const extremeDays = data.filter(
      (row) => Number.isFinite(row.GSR) && row.GSR >= threshold
    );

    if (!extremeDays.length) {
      container.textContent = "No extreme days available for this selection.";
      return;
    }

    const summary = {
      count: extremeDays.length,
      gsrAvg: d3.mean(extremeDays, (d) => d.GSR),
      sunAvg: d3.mean(extremeDays, (d) => d.SUN),
      rfAvg: d3.mean(extremeDays, (d) => d.RF),
      rhAvg: d3.mean(extremeDays, (d) => d.RH),
    };

    const title = document.createElement("h3");
    title.textContent = "Extreme solar radiation days";
    container.appendChild(title);

    renderSummaryCards(container, summary);

    const chartWrapper = document.createElement("div");
    chartWrapper.className = "extreme-chart";
    container.appendChild(chartWrapper);

    const seasons = ["winter", "spring", "summer", "autumn"];
    const seasonalCounts = seasons.map((season) => ({
      season,
      count: extremeDays.filter((row) => row.season === season).length,
    }));

    const margin = { top: 20, right: 20, bottom: 40, left: 50 };
    const width = Math.max(640, container.clientWidth || 900);
    const height = 260;
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(chartWrapper)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", "100%")
      .attr("height", height);

    const chart = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3
      .scaleBand()
      .domain(seasons)
      .range([0, innerWidth])
      .padding(0.25);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(seasonalCounts, (d) => d.count) || 0])
      .nice()
      .range([innerHeight, 0]);

    chart
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(
        d3
          .axisBottom(xScale)
          .tickFormat((d) => d[0].toUpperCase() + d.slice(1))
      );

    chart.append("g").call(d3.axisLeft(yScale).ticks(5));

    chart
      .selectAll("rect")
      .data(seasonalCounts)
      .join("rect")
      .attr("x", (d) => xScale(d.season))
      .attr("y", (d) => yScale(d.count))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => innerHeight - yScale(d.count))
      .attr("fill", "#1f5fa2")
      .attr("opacity", 0.85);

    chart
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 32)
      .attr("text-anchor", "middle")
      .attr("font-size", 12)
      .attr("fill", "#5b6670")
      .text("Season");

    chart
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -38)
      .attr("text-anchor", "middle")
      .attr("font-size", 12)
      .attr("fill", "#5b6670")
      .text("Extreme day count");

    const tableTitle = document.createElement("h4");
    tableTitle.textContent = "Top 10 extreme days";
    container.appendChild(tableTitle);

    const tableHint = document.createElement("p");
    tableHint.className = "interaction-hint";
    tableHint.textContent =
      "Click a date to trace that extreme event in the sunshine-GSR scatterplot.";
    container.appendChild(tableHint);

    const topDays = [...extremeDays]
      .sort((a, b) => b.GSR - a.GSR)
      .slice(0, 10);

    renderTopTable(container, topDays, d3, state?.onSelectExtremeDay);
  } catch (error) {
    console.error("Failed to render extreme days view:", error);
    container.textContent = "Unable to render extreme day details.";
  }
}
