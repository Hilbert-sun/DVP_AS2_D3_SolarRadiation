import { computeMonthlySummary } from "./dataProcessing.js";

const SERIES = [
  { key: "gsrAvg", label: "GSR", color: "#1f5fa2" },
  { key: "rfAvg", label: "Rainfall", color: "#d26a2e" },
  { key: "sunAvg", label: "Sunshine", color: "#2f8f5b" },
  { key: "rhAvg", label: "Humidity", color: "#6a4c93" },
];

const MONTH_LABELS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

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

export function renderSeasonalPattern(containerSelector, data, state) {
  const d3 = requireD3();
  const container = resolveContainer(containerSelector);

  if (!container) {
    console.error("Seasonal pattern chart container not found.");
    return;
  }

  container.innerHTML = "";
  container.style.position = "relative";

  try {
    const summary = computeMonthlySummary(data).filter((row) =>
      Number.isFinite(row.month)
    );

    if (!summary.length) {
      container.textContent = "No monthly data available for this selection.";
      return;
    }

    const months = d3.range(1, 13);
    const summaryByMonth = new Map(summary.map((row) => [row.month, row]));

    const margin = { top: 85, right: 130, bottom: 65, left: 80 };
    const containerWidth = container.clientWidth || 960;
    const width = Math.max(800, Math.min(containerWidth, 1200));
    const height = 560;
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
      .text("Monthly climate rhythm at King's Park");

    svg
      .append("text")
      .attr("x", margin.left)
      .attr("y", 56)
      .attr("font-size", 13)
      .attr("fill", "#5b6670")
      .text(
        "Standardised values allow different units to be compared on the same rhythm."
      );

    const chart = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3
      .scalePoint()
      .domain(months)
      .range([0, innerWidth])
      .padding(0.5);

    const seriesStats = new Map(
      SERIES.map((series) => {
        const values = months
          .map((month) => summaryByMonth.get(month)?.[series.key])
          .filter(Number.isFinite);
        return [
          series.key,
          {
            mean: d3.mean(values),
            deviation: d3.deviation(values),
          },
        ];
      })
    );

    const standardize = (value, stats) => {
      if (!Number.isFinite(value) || !stats?.deviation) {
        return null;
      }
      return (value - stats.mean) / stats.deviation;
    };

    const allValues = summary.flatMap((row) =>
      SERIES.map((series) =>
        standardize(row[series.key], seriesStats.get(series.key))
      ).filter(Number.isFinite)
    );
    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(allValues))
      .nice()
      .range([innerHeight, 0]);

    chart
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(
        d3
          .axisBottom(xScale)
          .tickFormat((month) => MONTH_LABELS[month - 1])
      );

    chart.append("g").call(d3.axisLeft(yScale).ticks(6));

    chart
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 48)
      .attr("text-anchor", "middle")
      .attr("font-size", 13)
      .attr("fill", "#5b6670")
      .text("Month");

    chart
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -62)
      .attr("text-anchor", "middle")
      .attr("font-size", 13)
      .attr("fill", "#5b6670")
      .text("Standardised monthly value");

    const line = d3
      .line()
      .x((d) => xScale(d.month))
      .y((d) => yScale(d.value));

    SERIES.forEach((series) => {
      chart
        .append("path")
        .datum(
          months.map((month) => ({
            month,
            value: standardize(
              summaryByMonth.get(month)?.[series.key],
              seriesStats.get(series.key)
            ),
          }))
        )
        .attr("fill", "none")
        .attr("stroke", series.color)
        .attr("stroke-width", 2.2)
        .attr(
          "d",
          line.defined((d) => Number.isFinite(d.value))
        );
    });

    const legend = chart
      .append("g")
      .attr("transform", `translate(${innerWidth + 10}, 0)`);

    SERIES.forEach((series, index) => {
      const row = legend
        .append("g")
        .attr("transform", `translate(0, ${index * 20})`);
      row
        .append("line")
        .attr("x1", 0)
        .attr("x2", 26)
        .attr("y1", 8)
        .attr("y2", 8)
        .attr("stroke", series.color)
        .attr("stroke-width", 3);
      row
        .append("text")
        .attr("x", 34)
        .attr("y", 12)
        .attr("font-size", 12)
        .attr("fill", "#1f2933")
        .text(series.label);
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
      .style("font-size", "12px")
      .style("color", "#1f2933")
      .style("box-shadow", "0 6px 16px rgba(31, 41, 51, 0.12)");

    const focusGroup = chart.append("g").style("opacity", 0);
    SERIES.forEach((series) => {
      focusGroup
        .append("circle")
        .attr("r", 4.5)
        .attr("fill", series.color)
        .attr("data-key", series.key);
    });

    const monthPositions = months.map((month) => xScale(month));

    chart
      .append("rect")
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", "transparent")
      .on("mousemove", (event) => {
        const [mouseX] = d3.pointer(event);
        let nearestMonth = months[0];
        let smallestDistance = Infinity;

        monthPositions.forEach((pos, index) => {
          const distance = Math.abs(mouseX - pos);
          if (distance < smallestDistance) {
            smallestDistance = distance;
            nearestMonth = months[index];
          }
        });

        const row = summaryByMonth.get(nearestMonth);
        if (!row) {
          return;
        }

        focusGroup.style("opacity", 1);
        focusGroup.selectAll("circle").each(function (seriesItem) {
          const series = SERIES.find(
            (item) => item.key === d3.select(this).attr("data-key")
          );
          if (!series) {
            return;
          }
          const zValue = standardize(row[series.key], seriesStats.get(series.key));
          d3.select(this)
            .attr("cx", xScale(nearestMonth))
            .attr("cy", yScale(zValue));
        });

        const details = SERIES.map(
          (series) =>
            `${series.label}: ${d3.format(".2f")(row[series.key])}`
        ).join("<br/>");

        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${MONTH_LABELS[nearestMonth - 1]}</strong><br/>${details}`
          );

        const [containerX, containerY] = d3.pointer(event, container);
        const tooltipNode = tooltip.node();
        const tooltipWidth = tooltipNode.offsetWidth;
        const tooltipHeight = tooltipNode.offsetHeight;
        const availableWidth = container.clientWidth;
        const availableHeight = container.clientHeight;
        const padding = 12;

        let left = containerX + padding;
        let top = containerY - tooltipHeight / 2;

        if (left + tooltipWidth + padding > availableWidth) {
          left = containerX - tooltipWidth - padding;
        }
        if (top < padding) {
          top = padding;
        }
        if (top + tooltipHeight + padding > availableHeight) {
          top = availableHeight - tooltipHeight - padding;
        }

        left = Math.max(
          padding,
          Math.min(left, availableWidth - tooltipWidth - padding)
        );

        tooltip.style("left", `${left}px`).style("top", `${top}px`);
      })
      .on("mouseleave", () => {
        focusGroup.style("opacity", 0);
        tooltip.style("opacity", 0);
      });
  } catch (error) {
    console.error("Failed to render seasonal pattern chart:", error);
    container.textContent = "Unable to render seasonal pattern chart.";
  }
}
