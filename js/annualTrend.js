import { computeAnnualSummary } from "./dataProcessing.js";

const COLOR_GSR = "#1f5fa2";
const COLOR_RF = "#d26a2e";

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

function standardize(values, d3) {
  const mean = d3.mean(values);
  const deviation = d3.deviation(values);
  return values.map((value) =>
    deviation ? (value - mean) / deviation : 0
  );
}

export function renderAnnualTrend(containerSelector, data, state) {
  const d3 = requireD3();
  const container = resolveContainer(containerSelector);

  if (!container) {
    console.error("Annual trend chart container not found.");
    return;
  }

  container.innerHTML = "";
  container.style.position = "relative";

  try {
    const summary = computeAnnualSummary(data).filter((row) =>
      Number.isFinite(row.year)
    );

    if (!summary.length) {
      container.textContent = "No annual data available for this selection.";
      return;
    }

    const gsrValues = summary.map((row) => row.gsrAvg ?? 0);
    const rfValues = summary.map((row) => row.rfAvg ?? 0);
    const gsrStd = standardize(gsrValues, d3);
    const rfStd = standardize(rfValues, d3);

    const series = summary.map((row, index) => ({
      ...row,
      gsrStd: gsrStd[index],
      rfStd: rfStd[index],
    }));

    const margin = { top: 105, right: 150, bottom: 80, left: 95 };
    const containerWidth = container.clientWidth || 960;
    const width = Math.max(900, Math.min(containerWidth, 1300));
    const height = 660;
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
      .attr("y", 34)
      .attr("font-size", 24)
      .attr("font-weight", 600)
      .text("Annual trends of solar radiation and rainfall");

    svg
      .append("text")
      .attr("x", margin.left)
      .attr("y", 60)
      .attr("font-size", 15)
      .attr("fill", "#5b6670")
      .text(
        "Standardised annual values show long-term co-movement while preserving different original units."
      );

    const chart = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3
      .scaleLinear()
      .domain(d3.extent(series, (d) => d.year))
      .range([0, innerWidth]);

    const allValues = series.flatMap((d) => [d.gsrStd, d.rfStd]);
    const yExtent = d3.extent(allValues);
    const yPadding = 0.3;
    const yScale = d3
      .scaleLinear()
      .domain([yExtent[0] - yPadding, yExtent[1] + yPadding])
      .range([innerHeight, 0]);

    const grid = chart
      .append("g")
      .attr("class", "grid")
      .call(
        d3
          .axisLeft(yScale)
          .ticks(7)
          .tickSize(-innerWidth)
          .tickFormat("")
      );

    grid.selectAll("line").attr("stroke", "#e6ebf1").attr("stroke-dasharray", "2,2");
    grid.select(".domain").remove();

    const xAxis = chart
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).ticks(8).tickFormat(d3.format("d")));

    xAxis.selectAll("text").attr("font-size", 13).attr("fill", "#5b6670");
    xAxis.selectAll("line").attr("stroke", "#cfd8e3");
    xAxis.select(".domain").attr("stroke", "#cfd8e3");

    const yAxis = chart.append("g").call(d3.axisLeft(yScale).ticks(7));
    yAxis.selectAll("text").attr("font-size", 13).attr("fill", "#5b6670");
    yAxis.selectAll("line").attr("stroke", "#cfd8e3");
    yAxis.select(".domain").attr("stroke", "#cfd8e3");

    chart
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 58)
      .attr("text-anchor", "middle")
      .attr("font-size", 14)
      .attr("font-weight", 500)
      .attr("fill", "#5b6670")
      .text("Year");

    chart
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -78)
      .attr("text-anchor", "middle")
      .attr("font-size", 14)
      .attr("font-weight", 500)
      .attr("fill", "#5b6670")
      .text("Standardised value (z-score)");

    const line = d3
      .line()
      .x((d) => xScale(d.year))
      .y((d) => yScale(d.value));

    chart
      .append("path")
      .datum(series.map((d) => ({ year: d.year, value: d.gsrStd })))
      .attr("fill", "none")
      .attr("stroke", COLOR_GSR)
      .attr("stroke-width", 3.5)
      .attr("d", line);

    chart
      .append("path")
      .datum(series.map((d) => ({ year: d.year, value: d.rfStd })))
      .attr("fill", "none")
      .attr("stroke", COLOR_RF)
      .attr("stroke-width", 3.5)
      .attr("d", line);

    chart
      .selectAll("circle.gsr-point")
      .data(series)
      .join("circle")
      .attr("class", "gsr-point")
      .attr("cx", (d) => xScale(d.year))
      .attr("cy", (d) => yScale(d.gsrStd))
      .attr("r", 3.5)
      .attr("fill", COLOR_GSR)
      .attr("opacity", 0.9);

    chart
      .selectAll("circle.rf-point")
      .data(series)
      .join("circle")
      .attr("class", "rf-point")
      .attr("cx", (d) => xScale(d.year))
      .attr("cy", (d) => yScale(d.rfStd))
      .attr("r", 3.5)
      .attr("fill", COLOR_RF)
      .attr("opacity", 0.9);

    const lastPoint = series[series.length - 1];
    if (lastPoint) {
      let gsrLabelY = yScale(lastPoint.gsrStd);
      let rfLabelY = yScale(lastPoint.rfStd);
      if (Math.abs(gsrLabelY - rfLabelY) < 14) {
        gsrLabelY -= 10;
        rfLabelY += 10;
      }

      chart
        .append("text")
        .attr("x", xScale(lastPoint.year) + 10)
        .attr("y", gsrLabelY)
        .attr("font-size", 13)
        .attr("font-weight", 600)
        .attr("fill", COLOR_GSR)
        .attr("alignment-baseline", "middle")
        .text("GSR");

      chart
        .append("text")
        .attr("x", xScale(lastPoint.year) + 10)
        .attr("y", rfLabelY)
        .attr("font-size", 13)
        .attr("font-weight", 600)
        .attr("fill", COLOR_RF)
        .attr("alignment-baseline", "middle")
        .text("Rainfall");
    }

    const annotationValue = Number.isFinite(yExtent[1])
      ? Math.min(yExtent[1], 0.9)
      : 0.6;
    const annotationY = yScale(annotationValue);

    chart
      .append("text")
      .attr("x", innerWidth * 0.55)
      .attr("y", annotationY - 8)
      .attr("font-size", 12)
      .attr("fill", "#5b6670")
      .text("Rainfall shows stronger year-to-year variability,");

    chart
      .append("text")
      .attr("x", innerWidth * 0.55)
      .attr("y", annotationY + 10)
      .attr("font-size", 12)
      .attr("fill", "#5b6670")
      .text("while solar radiation changes more gradually.");

    const legend = chart
      .append("g")
      .attr("transform", `translate(${innerWidth - 10}, 0)`);

    [
      { label: "GSR (standardised)", color: COLOR_GSR },
      { label: "Rainfall (standardised)", color: COLOR_RF },
    ].forEach((item, index) => {
      const row = legend
        .append("g")
        .attr("transform", `translate(0, ${index * 26})`);
      row
        .append("line")
        .attr("x1", -40)
        .attr("x2", -8)
        .attr("y1", 8)
        .attr("y2", 8)
        .attr("stroke", item.color)
        .attr("stroke-width", 4);
      row
        .append("text")
        .attr("x", 0)
        .attr("y", 12)
        .attr("font-size", 13)
        .attr("font-weight", 500)
        .attr("fill", "#1f2933")
        .text(item.label);
    });

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
      .style("font-size", "13px")
      .style("color", "#1f2933")
      .style("box-shadow", "0 6px 16px rgba(31, 41, 51, 0.12)");

    const focusGsr = chart
      .append("circle")
      .attr("r", 4.5)
      .attr("fill", COLOR_GSR)
      .style("opacity", 0);

    const focusRf = chart
      .append("circle")
      .attr("r", 4.5)
      .attr("fill", COLOR_RF)
      .style("opacity", 0);

    const bisectYear = d3.bisector((d) => d.year).left;

    chart
      .append("rect")
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", "transparent")
      .on("mousemove", (event) => {
        const [hoverX] = d3.pointer(event);
        const yearValue = xScale.invert(hoverX);
        const index = bisectYear(series, yearValue);
        const prev = series[index - 1];
        const next = series[index];
        const selected =
          !prev || !next
            ? prev || next
            : yearValue - prev.year > next.year - yearValue
              ? next
              : prev;

        if (!selected) {
          return;
        }

        focusGsr
          .attr("cx", xScale(selected.year))
          .attr("cy", yScale(selected.gsrStd))
          .style("opacity", 1);
        focusRf
          .attr("cx", xScale(selected.year))
          .attr("cy", yScale(selected.rfStd))
          .style("opacity", 1);

        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${selected.year}</strong><br/>` +
              `Annual GSR: ${d3.format(".2f")(selected.gsrAvg)} MJ/m²<br/>` +
              `Annual RF: ${d3.format(".2f")(selected.rfAvg)} mm<br/>` +
              `<span style="color:#5b6670;">GSR std: ${d3.format(".2f")(
                selected.gsrStd
              )}, RF std: ${d3.format(".2f")(selected.rfStd)}</span>`
          );

        const tooltipNode = tooltip.node();
        const [containerX, containerY] = d3.pointer(event, container);
        const tooltipWidth = tooltipNode.offsetWidth;
        const tooltipHeight = tooltipNode.offsetHeight;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const padding = 12;

        let left = containerX + padding;
        let top = containerY - tooltipHeight - padding;

        if (containerX + tooltipWidth + padding > containerWidth) {
          left = containerX - tooltipWidth - padding;
        }
        if (containerY - tooltipHeight - padding < 0) {
          top = containerY + padding;
        }

        left = Math.max(padding, Math.min(left, containerWidth - tooltipWidth - padding));
        top = Math.max(padding, Math.min(top, containerHeight - tooltipHeight - padding));

        tooltip.style("left", `${left}px`).style("top", `${top}px`);
      })
      .on("mouseleave", () => {
        focusGsr.style("opacity", 0);
        focusRf.style("opacity", 0);
        tooltip.style("opacity", 0);
      });
  } catch (error) {
    console.error("Failed to render annual trend chart:", error);
    container.textContent = "Unable to render annual trend chart.";
  }
}
