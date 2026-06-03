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

function normalizeSeason(value) {
  if (!value) {
    return null;
  }
  return String(value).trim().toLowerCase();
}

function getDateKey(row, d3) {
  if (row?.date instanceof Date) {
    return d3.timeFormat("%Y-%m-%d")(row.date);
  }
  return row?.date ? String(row.date).slice(0, 10) : "";
}

export function renderScatterDriver(containerSelector, data, state) {
  const d3 = requireD3();
  const container = resolveContainer(containerSelector);

  if (!container) {
    console.error("Scatter driver chart container not found.");
    return;
  }

  container.innerHTML = "";
  container.style.position = "relative";

  try {
    const selectedSeason = normalizeSeason(state?.selectedSeason || "all");
    const filtered = Array.isArray(data)
      ? data.filter((row) => {
          if (!selectedSeason || selectedSeason === "all") {
            return true;
          }
          return normalizeSeason(row.season) === selectedSeason;
        })
      : [];

    if (!filtered.length) {
      container.textContent = "No data available for this selection.";
      return;
    }

    const margin = { top: 75, right: 160, bottom: 65, left: 80 };
    const containerWidth = container.clientWidth || 960;
    const width = Math.max(800, Math.min(containerWidth, 1200));
    const height = 550;
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(container)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", "100%")
      .attr("height", height);

    svg
      .append("text")
      .attr("x", margin.left)
      .attr("y", 32)
      .attr("font-size", 20)
      .attr("font-weight", 600)
      .text("Sunshine as the main driver of solar radiation");

    const selectedRow = state?.selectedExtremeDate
      ? filtered.find((row) => getDateKey(row, d3) === state.selectedExtremeDate)
      : null;

    if (state?.showExtremeOnly) {
      svg
        .append("text")
        .attr("x", margin.left)
        .attr("y", 56)
        .attr("font-size", 13)
        .attr("fill", "#5b6670")
        .text(
          selectedRow
            ? `Linked from Step 4: ${state.selectedExtremeDate} is highlighted against the full daily context.`
            : "Extreme solar radiation days are highlighted while the full daily context remains visible."
        );
    }

    const chart = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3
      .scaleLinear()
      .domain(d3.extent(filtered, (d) => d.SUN))
      .nice()
      .range([0, innerWidth]);

    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(filtered, (d) => d.GSR))
      .nice()
      .range([innerHeight, 0]);

    const sizeScale = d3
      .scaleSqrt()
      .domain(d3.extent(filtered, (d) => d.RF))
      .range([3, 14]);

    const colorScale = d3
      .scaleLinear()
      .domain(d3.extent(filtered, (d) => d.RH))
      .range(["#dfe9f3", "#1f5fa2"]);

    chart
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).ticks(6).tickSize(5));

    chart.append("g").call(d3.axisLeft(yScale).ticks(6).tickSize(5));

    chart
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 48)
      .attr("text-anchor", "middle")
      .attr("font-size", 13)
      .attr("fill", "#5b6670")
      .text("Sunshine duration (SUN)");

    chart
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -62)
      .attr("text-anchor", "middle")
      .attr("font-size", 13)
      .attr("fill", "#5b6670")
      .text("Global solar radiation (GSR)");

    const tooltip = d3
      .select(container)
      .append("div")
      .attr("class", "chart-tooltip")
      .style("position", "absolute")
      .style("opacity", 0)
      .style("pointer-events", "none")
      .style("background", "#ffffff")
      .style("border", "1px solid #d9e1ea")
      .style("border-radius", "8px")
      .style("padding", "8px 10px")
      .style("font-size", "12px")
      .style("color", "#1f2933")
      .style("box-shadow", "0 6px 16px rgba(31, 41, 51, 0.12)");

    const timeFormat = d3.timeFormat("%Y-%m-%d");

    chart
      .append("g")
      .selectAll("circle")
      .data(filtered)
      .join("circle")
      .attr("cx", (d) => xScale(d.SUN))
      .attr("cy", (d) => yScale(d.GSR))
      .attr("r", (d) => sizeScale(d.RF))
      .attr("fill", (d) => colorScale(d.RH))
      .attr("fill-opacity", (d) => {
        if (!state?.showExtremeOnly) {
          return 0.72;
        }
        return d.isExtreme ? 0.88 : 0.18;
      })
      .attr("stroke", (d) =>
        getDateKey(d, d3) === state?.selectedExtremeDate
          ? "#d26a2e"
          : state?.showExtremeOnly && d.isExtreme
            ? "#1f2933"
            : "none"
      )
      .attr("stroke-width", (d) =>
        getDateKey(d, d3) === state?.selectedExtremeDate
          ? 3
          : state?.showExtremeOnly && d.isExtreme
            ? 1.1
            : 0
      )
      .on("mousemove", (event, d) => {
        const dateLabel = d.date instanceof Date ? timeFormat(d.date) : d.date || "Unknown date";
        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${dateLabel}</strong><br/>Season: ${
              d.season || "Unknown"
            }<br/>GSR: ${d3.format(".2f")(d.GSR)}<br/>SUN: ${d3.format(".2f")(
              d.SUN
            )}<br/>RF: ${d3.format(".2f")(d.RF)}<br/>RH: ${d3.format(".2f")(d.RH)}`
          );

        const tooltipNode = tooltip.node();
        const tooltipWidth = tooltipNode.offsetWidth;
        const tooltipHeight = tooltipNode.offsetHeight;
        const containerRect = container.getBoundingClientRect();
        const padding = 12;
        const pointerX = event.clientX - containerRect.left;
        const pointerY = event.clientY - containerRect.top;

        let left = pointerX + padding;
        let top = pointerY - tooltipHeight / 2;

        if (left + tooltipWidth + padding > container.clientWidth) {
          left = pointerX - tooltipWidth - padding;
        }
        if (top < padding) {
          top = padding;
        }
        if (top + tooltipHeight + padding > container.clientHeight) {
          top = container.clientHeight - tooltipHeight - padding;
        }

        left = Math.max(
          padding,
          Math.min(left, container.clientWidth - tooltipWidth - padding)
        );

        tooltip.style("left", `${left}px`).style("top", `${top}px`);
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", 0);
      });

    if (selectedRow) {
      const selectedX = xScale(selectedRow.SUN);
      const selectedY = yScale(selectedRow.GSR);

      chart
        .append("circle")
        .attr("cx", selectedX)
        .attr("cy", selectedY)
        .attr("r", Math.max(18, sizeScale(selectedRow.RF) + 8))
        .attr("fill", "none")
        .attr("stroke", "#d26a2e")
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", "5,4")
        .attr("pointer-events", "none");

      chart
        .append("line")
        .attr("x1", selectedX)
        .attr("x2", selectedX)
        .attr("y1", selectedY)
        .attr("y2", innerHeight)
        .attr("stroke", "#d26a2e")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,4")
        .attr("pointer-events", "none");

      chart
        .append("line")
        .attr("x1", 0)
        .attr("x2", selectedX)
        .attr("y1", selectedY)
        .attr("y2", selectedY)
        .attr("stroke", "#d26a2e")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,4")
        .attr("pointer-events", "none");

      const labelX = Math.min(selectedX + 16, innerWidth - 170);
      const labelY = Math.max(selectedY - 26, 24);
      chart
        .append("text")
        .attr("x", labelX)
        .attr("y", labelY)
        .attr("font-size", 12)
        .attr("font-weight", 600)
        .attr("fill", "#d26a2e")
        .text(`Selected extreme day: ${state.selectedExtremeDate}`);
    }

    const legendGroup = chart
      .append("g")
      .attr("transform", `translate(${innerWidth + 20}, 0)`);

    legendGroup
      .append("text")
      .attr("x", 0)
      .attr("y", 0)
      .attr("font-size", 12)
      .attr("font-weight", 600)
      .text("Rainfall (size)");

    const rfExtent = d3.extent(filtered, (d) => d.RF).filter(Number.isFinite);
    const rfLegendValues = rfExtent.length
      ? [rfExtent[0], (rfExtent[0] + rfExtent[1]) / 2, rfExtent[1]]
      : [0, 1, 2];

    const sizeLegend = legendGroup.append("g").attr("transform", "translate(0, 16)");

    rfLegendValues.forEach((value, index) => {
      const y = index * 26 + 12;
      sizeLegend
        .append("circle")
        .attr("cx", 10)
        .attr("cy", y)
        .attr("r", sizeScale(value))
        .attr("fill", "#cfd8e3")
        .attr("stroke", "#9aa5b1");
      sizeLegend
        .append("text")
        .attr("x", 28)
        .attr("y", y + 4)
        .attr("font-size", 11)
        .attr("fill", "#1f2933")
        .text(d3.format(".1f")(value));
    });

    const colorLegendY = 110;
    legendGroup
      .append("text")
      .attr("x", 0)
      .attr("y", colorLegendY)
      .attr("font-size", 12)
      .attr("font-weight", 600)
      .text("Humidity (colour)");

    const gradientId = "humidity-gradient";
    const defs = svg.append("defs");
    const gradient = defs
      .append("linearGradient")
      .attr("id", gradientId)
      .attr("x1", "0%")
      .attr("x2", "100%");

    gradient
      .append("stop")
      .attr("offset", "0%")
      .attr("stop-color", colorScale.range()[0]);
    gradient
      .append("stop")
      .attr("offset", "100%")
      .attr("stop-color", colorScale.range()[1]);

    legendGroup
      .append("rect")
      .attr("x", 0)
      .attr("y", colorLegendY + 10)
      .attr("width", 90)
      .attr("height", 10)
      .attr("fill", `url(#${gradientId})`)
      .attr("stroke", "#c7d0d9");

    const rhExtent = d3.extent(filtered, (d) => d.RH);
    legendGroup
      .append("text")
      .attr("x", 0)
      .attr("y", colorLegendY + 34)
      .attr("font-size", 11)
      .attr("fill", "#1f2933")
      .text(d3.format(".1f")(rhExtent[0]));
    legendGroup
      .append("text")
      .attr("x", 90)
      .attr("y", colorLegendY + 34)
      .attr("text-anchor", "end")
      .attr("font-size", 11)
      .attr("fill", "#1f2933")
      .text(d3.format(".1f")(rhExtent[1]));
  } catch (error) {
    console.error("Failed to render scatter driver chart:", error);
    container.textContent = "Unable to render scatterplot.";
  }
}
