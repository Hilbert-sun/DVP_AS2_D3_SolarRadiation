from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
BODY_PDF = ROOT / "SUNZHEN_36446874_DVP_Report_HD_body.pdf"
FINAL_PDF = ROOT / "SUNZHEN_36446874_DVP_Report_HD.pdf"
PRESENTATION_PDF = ROOT / "SUNZHEN_36446874_Presentation.pdf"
SCREENSHOTS = ROOT / "report_screenshots"


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=18,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=17,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=15,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.8,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "body_indent": ParagraphStyle(
            "BodyIndent",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.2,
            leftIndent=14,
            firstLineIndent=-14,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=11,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#444444"),
            spaceBefore=3,
            spaceAfter=8,
        ),
        "toc": ParagraphStyle(
            "TOC",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=17,
            leftIndent=0,
            spaceAfter=5,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            textColor=colors.black,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.HexColor("#777777"),
            borderWidth=0.4,
            borderPadding=7,
            spaceBefore=5,
            spaceAfter=8,
        ),
    }


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    page = canvas.getPageNumber()
    canvas.drawRightString(A4[0] - 1.55 * cm, 1.0 * cm, f"Page {page}")
    canvas.drawString(
        1.55 * cm,
        1.0 * cm,
        "When Sunshine Meets Rain - FIT5147 Data Visualisation Project",
    )
    canvas.restoreState()


def p(text, style):
    return Paragraph(text, style)


def bullets(items, styles):
    return ListFlowable(
        [ListItem(p(item, styles["body"]), leftIndent=10) for item in items],
        bulletType="bullet",
        leftIndent=14,
        bulletFontSize=7,
    )


def fig(path, caption, styles, max_w=16.0 * cm, max_h=8.2 * cm):
    image_path = SCREENSHOTS / path
    with Image.open(image_path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return KeepTogether(
        [
            RLImage(str(image_path), width=w * scale, height=h * scale),
            p(caption, styles["caption"]),
        ]
    )


def data_table(rows, col_widths):
    table = Table(rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.7),
                ("LEADING", (0, 0), (-1, -1), 9.7),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def rule():
    table = Table([[""]], colWidths=[16.4 * cm], rowHeights=[0.04 * cm])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#444444"))]))
    return table


def kv_lines(items, styles):
    flow = []
    for key, value in items:
        flow.append(p(f"<b>{key}:</b> {value}", styles["body_indent"]))
    return flow


def toc_line(title, page, styles):
    return p(f"{title}<font color='#777777'> {' . ' * 20}</font>{page}", styles["toc"])


def toc_table(items, styles):
    rows = [[p(title, styles["toc"]), p(page, styles["toc"])] for title, page in items]
    table = Table(rows, colWidths=[14.7 * cm, 1.1 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LINEBELOW", (0, 0), (-1, -1), 0.15, colors.HexColor("#dddddd")),
            ]
        )
    )
    return table


def build_body():
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(BODY_PDF),
        pagesize=A4,
        rightMargin=1.55 * cm,
        leftMargin=1.55 * cm,
        topMargin=1.35 * cm,
        bottomMargin=1.35 * cm,
    )

    story = []

    story += [
        Spacer(1, 3.0 * cm),
        p("When Sunshine Meets Rain", styles["title"]),
        rule(),
        Spacer(1, 0.45 * cm),
        p("Understanding Solar Radiation Patterns at King's Park, Hong Kong", styles["subtitle"]),
        Spacer(1, 0.6 * cm),
        p("FIT5147 Data Exploration and Visualisation", styles["subtitle"]),
        p("Data Visualisation Project - Part 2 Report", styles["subtitle"]),
        Spacer(1, 1.0 * cm),
        data_table(
            [
                ["Student name", "Sun Zhen"],
                ["Student ID", "36446874"],
                ["Applied session", "Workshop01"],
                ["Teaching Associate", "Dr Ting Chai Wen"],
                ["Implementation technology", "D3.js, HTML, CSS, JavaScript"],
            ],
            [5.0 * cm, 10.0 * cm],
        ),
        Spacer(1, 0.8 * cm),
        p(
            "This report documents the design process, implementation, interaction design, and reflection for an interactive narrative visualisation built with D3.js.",
            styles["subtitle"],
        ),
        PageBreak(),
    ]

    story += [
        p("Table of Contents", styles["h1"]),
        Spacer(1, 0.2 * cm),
        rule(),
        Spacer(1, 0.45 * cm),
        toc_table(
            [
                ("1. Introduction", "3"),
                ("2. Design Process", "4"),
                ("2.1 Audience and Narrative Framing", "4"),
                ("2.2 Five Design Sheet Development", "4"),
                ("2.3 Theory-Grounded Design Rationale", "5"),
                ("3. Implementation", "6"),
                ("3.1 Technical Implementation", "6"),
                ("3.2 Interactive Narrative Visualisation Implementation", "7"),
                ("3.3 Using the Implementation", "12"),
                ("4. Conclusion and Reflection", "12"),
                ("AI Declaration", "13"),
                ("References", "13"),
                ("Appendix A: Five Design Sheets", "15"),
            ],
            styles,
        ),
        PageBreak(),
    ]

    story += [
        p("1. Introduction", styles["h1"]),
        p(
            "This project presents an interactive narrative visualisation about solar radiation patterns at King's Park, Hong Kong. It transforms findings from the data exploration stage into a guided D3.js interface for Hong Kong urban planners and environmental policy advisors. The central message is that global solar radiation is strongly associated with sunshine duration, while rainfall and relative humidity help explain lower-radiation conditions, seasonal variation, and the context surrounding extreme solar radiation days.",
            styles["body"],
        ),
        p(
            "The audience may not need detailed statistical modelling, but it does need clear visual evidence that can support infrastructure planning, solar feasibility discussion, and climate-adaptation decisions. The design therefore avoids a purely exploratory dashboard. Instead, it uses a five-step narrative that moves from long-term context to seasonal rhythm, daily driver, extreme events, and planning implications.",
            styles["body"],
        ),
        p("Research questions and implementation response", styles["h2"]),
        *kv_lines(
            [
                (
                    "Long-term relationship",
                    "Step 1 shows standardised annual GSR and rainfall trends, preserving raw values in tooltips.",
                ),
                (
                    "Seasonal climate rhythm",
                    "Step 2 compares standardised monthly rhythms across GSR, rainfall, sunshine duration, and relative humidity.",
                ),
                (
                    "Extreme solar conditions",
                    "Step 4 identifies the top 5% GSR days and links top events back to the SUN-GSR scatterplot.",
                ),
            ],
            styles,
        ),
        p(
            "The final implementation is designed to be readable without the report: story navigation, chart titles, legends, tooltips, an insight panel, and planning takeaways work together to communicate the narrative inside the interface itself.",
            styles["callout"],
        ),
        PageBreak(),
    ]

    story += [
        p("2. Design Process", styles["h1"]),
        p("2.1 Audience and Narrative Framing", styles["h2"]),
        p(
            "The design process follows the Five Design Sheet methodology, moving from divergent brainstorming to alternative complete interface concepts and then to a final realisation. The intended audience shaped the process throughout. Urban planners and environmental policy advisors require interpretable evidence, clear sequencing, and planning implications rather than dense statistical output. This led to a guided narrative structure with limited but purposeful interactions.",
            styles["body"],
        ),
        p(
            "The narrative structure moves from context to explanation and then to action: (1) long-term annual variability, (2) monthly seasonal rhythm, (3) the daily relationship between sunshine duration and solar radiation, (4) extreme solar radiation days, and (5) planning takeaways. This sequence reduces cognitive load by introducing simpler temporal patterns before the denser multivariate scatterplot.",
            styles["body"],
        ),
        p("2.2 Five Design Sheet Development", styles["h2"]),
        p(
            "Sheet 1 generated possible encodings and interactions, including annual trend lines, monthly climate rhythm charts, GSR boxplots, SUN-GSR scatterplots, seasonal facets, LOESS curves, season cards, extreme solar days, story steps, and interaction controls. Dense pairplots and raw daily line charts were removed because they were too noisy for the audience. A map was removed because the dataset represents one station rather than spatial variation.",
            styles["body"],
        ),
        p(
            "Sheets 2, 3, and 4 explored three alternative complete designs. Sheet 2 used a scrollytelling climate story, which offered strong guidance but reduced comparison flexibility. Sheet 3 used a guided story dashboard with a main chart, insight panel, story navigation, and controls. Sheet 4 focused on seasonal and extreme-event exploration. The final realisation combines the guided dashboard from Sheet 3 with the seasonal and extreme-event emphasis from Sheet 4.",
            styles["body"],
        ),
        p(
            "A change was made after the Part 1 design presentation: Sheet 5 originally listed R Shiny as the intended implementation environment, but the final implementation uses D3.js. This change was made because the final design needed direct SVG control, custom story-step state, and linked highlighting between views. These interaction requirements are more naturally implemented in D3 than in a Shiny layout based mainly on packaged chart outputs.",
            styles["callout"],
        ),
        PageBreak(),
    ]

    story += [
        p("2.3 Theory-Grounded Design Rationale", styles["h2"]),
        p(
            "Munzner's what-why-how framework guided the mapping from data and tasks to visual encodings. The data abstractions are daily observations and derived annual, monthly, seasonal, and extreme-event summaries. The main tasks are to identify trends, compare seasonal rhythms, relate sunshine duration to solar radiation, and inspect high-radiation events. These tasks led to line charts for ordered temporal comparison, a multivariate scatterplot for relationship analysis, and summary cards plus a bar chart for extreme-day characterisation.",
            styles["body"],
        ),
        p(
            "Tufte's principle of maximising meaningful data ink influenced the restrained visual style, limited decoration, and emphasis on readable labels. Gestalt principles of proximity and similarity shaped the grouping of story controls, filters, and explanatory text. Related controls are grouped together, repeated story buttons share a consistent treatment, and the active step is highlighted to maintain orientation. The visual hierarchy places the chart at the centre and the interpretation in a separate insight panel so that text does not compete with the data.",
            styles["body"],
        ),
        p(
            "The scatterplot uses position for SUN and GSR because position on common scales supports more accurate quantitative comparison than colour or area. Rainfall is encoded by point size and humidity by colour because they are contextual variables. This ordering reflects the narrative hierarchy: the SUN-GSR relationship is primary, while rainfall and humidity explain conditions around lower or extreme radiation days.",
            styles["body"],
        ),
        p(
            "The linked extreme-day interaction supports Shneiderman's overview-then-details principle. Readers first see aggregate extreme-day counts and summary cards, then click an individual date to trace that record back to the full daily scatterplot context. This creates a clear connection between summary evidence and individual observations.",
            styles["callout"],
        ),
        p(
            "The design also reflects human visual perception constraints. Temporal patterns are encoded with connected lines because continuity supports the perception of change over ordered time. Seasonal comparison uses a shared standardised scale to make peaks and troughs comparable across variables with different units. The scatterplot uses partially transparent marks to reduce overplotting, while the extreme-day highlight increases salience only when the user asks to inspect rare high-radiation records.",
            styles["body"],
        ),
        p(
            "The final design deliberately avoids a map, despite the planning context, because the available data is station-level and contains no spatial variation. Including a map would imply a spatial analytic claim that the data cannot support. This decision reflects the principle that visual form should match the evidence available, not only the topic domain.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3. Implementation", styles["h1"]),
        p("3.1 Technical Implementation", styles["h2"]),
        p(
            "The final visualisation was implemented as a standalone web application using D3.js v7, HTML, CSS, and vanilla JavaScript. D3 was selected because the final design required custom story-step navigation, direct SVG control, coordinated state, tooltips, and flexible narrative layout. The implementation does not use R Markdown, Tableau, Python dashboards, server-side code, or high-level D3 wrapper libraries.",
            styles["body"],
        ),
        p(
            "The project reads all data from local submitted CSV files. The main file, data/daily_KP_all_merged.csv, contains 11,887 daily observations from 1992 to 2025 with Date, Year, Month, Day, GSR, RF, SUN, and RH fields. D3.js is included locally in js/lib/d3.v7.min.js so the marker does not depend on a remote CDN.",
            styles["body"],
        ),
        p("Implementation structure", styles["h2"]),
        *kv_lines(
            [
                ("index.html", "Defines layout, story buttons, chart container, insight panel, controls, and local D3 loading."),
                ("js/main.js", "Loads data, stores application state, validates filters, and re-renders the selected story step."),
                ("js/dataProcessing.js", "Parses CSV rows, derives season, filters records, computes summaries, and marks extreme days."),
                ("js/annualTrend.js", "Renders standardised annual GSR and rainfall trends."),
                ("js/seasonalPattern.js", "Renders standardised monthly climate rhythm across GSR, RF, SUN, and RH."),
                ("js/scatterDriver.js", "Renders the SUN-GSR scatterplot with rainfall size, humidity colour, extreme highlighting, and selected-date annotation."),
                ("js/extremeDays.js", "Renders extreme-day summary cards, seasonal distribution, top-10 table, and clickable date tracing."),
                ("js/storyController.js", "Maintains active navigation and narrative insight text."),
            ],
            styles,
        ),
        p(
            "The main technical challenge was maintaining consistent narrative state across multiple views. The year range, season filter, extreme-day highlight, and selected extreme date all interact with the same filtered dataset. The implementation marks extreme days after filtering and passes a shared state object to each renderer. This allows a selected extreme day to persist when the reader moves from Step 4 back to Step 3.",
            styles["body"],
        ),
        p(
            "Data handling is intentionally performed before rendering each view. Annual and monthly summaries are computed from the filtered dataset, which means the year and season controls change both the visual output and the narrative context. Extreme days are recomputed within the current selection, so a planner can inspect peak radiation events in the full dataset or within a narrower period or season.",
            styles["body"],
        ),
        p(
            "The implementation was kept as a static client-side application so that the marker can run it with a simple local server. This avoids installation complexity and aligns with the assignment requirement that data be read from submitted files rather than remote services.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation", styles["h2"]),
        fig(
            "fig1_overall_interface.png",
            "Figure 1. Overall interface showing story navigation, main chart area, insight panel, and controls.",
            styles,
            max_h=7.0 * cm,
        ),
        p(
            "The final interface follows the Sheet 5 guided story dashboard. It combines a fixed story navigation panel, a main visualisation panel, an insight panel, and a control bar. This layout makes the project read as a narrative rather than as a general-purpose dashboard.",
            styles["body"],
        ),
        fig(
            "fig2_long_term_context.png",
            "Figure 2. Step 1 shows standardised annual trends of solar radiation and rainfall.",
            styles,
            max_h=6.6 * cm,
        ),
        p(
            "Step 1 introduces long-term climate context. Because GSR and rainfall have different units, values are standardised for visual comparison while tooltips retain raw values. This avoids implying that the two physical variables are directly equivalent.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig3_seasonal_rhythm.png",
            "Figure 3. Step 2 compares monthly climate rhythm across GSR, rainfall, sunshine, and humidity.",
            styles,
            max_h=6.6 * cm,
        ),
        p(
            "Step 2 shifts from annual context to monthly seasonality. It highlights that Hong Kong's warmer months can combine high solar radiation with wet and humid conditions, which is useful for planners considering both solar potential and weather-related generation risk.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig4_sunshine_driver.png",
            "Figure 4. Step 3 shows sunshine duration as the clearest visual driver of solar radiation.",
            styles,
            max_h=7.4 * cm,
        ),
        p(
            "Step 3 presents the strongest daily relationship identified during exploration: sunshine duration and global solar radiation. SUN is placed on the x-axis and GSR on the y-axis. Rainfall is encoded by point size and relative humidity by colour. When extreme-day highlighting is enabled, non-extreme points remain visible in the background so that peak events can be interpreted against the full daily context.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig5_extreme_days.png",
            "Figure 5. Step 4 summarises top 5% GSR days and provides concrete high-radiation records.",
            styles,
            max_h=8.4 * cm,
        ),
        p(
            "Step 4 focuses on the top 5% of GSR observations. Summary cards communicate the number of extreme days and their average GSR, SUN, RF, and RH values. A seasonal bar chart shows the distribution of these events, and the top-10 table provides concrete examples. The table dates are linked: clicking a date jumps to Step 3 and highlights the same record in the scatterplot.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig6_planning_takeaway.png",
            "Figure 6. Step 5 translates the visual findings into planning takeaways.",
            styles,
            max_h=6.9 * cm,
        ),
        p(
            "Step 5 closes the narrative by translating the evidence into planning implications. It avoids adding a further complex chart because the goal of the final step is synthesis: solar potential is seasonally structured, sunshine duration is the clearest driver, and rainfall and humidity shape low-radiation conditions.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.3 Using the Implementation", styles["h2"]),
        p("The visualisation runs locally from the submitted code folder:", styles["body"]),
        p("python -m http.server 8000", styles["callout"]),
        p("Then open http://localhost:8000 in a browser.", styles["body"]),
        bullets(
            [
                "Click the five story-step buttons to move through the narrative.",
                "Enter start and end years to restrict the analysis period.",
                "Use the season filter to focus on all seasons or one seasonal subset.",
                "Use the extreme-day toggle to highlight top 5% GSR days while preserving context.",
                "In Step 4, click a top-10 date to trace that record in the Step 3 scatterplot.",
                "Hover chart elements to inspect detailed values through tooltips.",
                "Click Reset to return filters and linked selections to their default values.",
            ],
            styles,
        ),
        p("4. Conclusion and Reflection", styles["h1"]),
        p(
            "This project transformed exploratory climate analysis into an interactive narrative visualisation. The final implementation communicates that solar radiation at King's Park is closely related to sunshine duration, while rainfall and relative humidity help explain seasonal and lower-radiation conditions. The guided structure leads users from long-term context to monthly patterns, daily relationships, extreme solar days, and planning implications.",
            styles["body"],
        ),
        p(
            "A key design trade-off was between analytical completeness and narrative clarity. A more technical interface could have included regression models, seasonal correlation matrices, or additional meteorological variables. However, this would have increased cognitive load and moved the project away from the needs of planning and policy audiences. The final design therefore prioritises a coherent explanation of the strongest exploratory findings rather than presenting every possible analysis.",
            styles["body"],
        ),
        p(
            "If extended further, the most valuable improvement would be stronger linked brushing across all views. Selecting a seasonal bar or an extreme-day record could highlight the same subset across the annual trend, monthly rhythm, scatterplot, and extreme-day table. A second improvement would be to incorporate urban-form variables such as roof geometry, shading, and electricity demand so that the visualisation could move from climate-context evidence toward site-specific planning support.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("AI Declaration", styles["h1"]),
        p(
            "Generative AI tools were used to assist with planning, wording, and code development support for this assessment. ChatGPT was used to help structure the technical design, prepare draft report wording, and refine explanations of the implemented visualisations. GitHub Copilot was used in Visual Studio Code to assist with D3.js, HTML, CSS, and JavaScript implementation. All generated material was reviewed, edited, tested, and validated by the student before inclusion. The final design decisions, data interpretation, code integration, and submitted work remain the student's responsibility.",
            styles["body"],
        ),
        p("References", styles["h1"]),
        p("Bostock, M., Ogievetsky, V., & Heer, J. (2011). D3: Data-driven documents. IEEE Transactions on Visualization and Computer Graphics, 17(12), 2301-2309. https://doi.org/10.1109/TVCG.2011.185", styles["small"]),
        p("Hong Kong Observatory. (2025). Historical meteorological data download. Hong Kong Government Open Data Portal. https://data.weather.gov.hk/", styles["small"]),
        p("Lu, N., Qin, J., Yang, K., & Sun, J. (2011). A simple and efficient algorithm to estimate daily global solar radiation from geostationary satellite data. Energy, 36(5), 3179-3188. https://doi.org/10.1016/j.energy.2011.03.007", styles["small"]),
        p("Munzner, T. (2014). Visualization analysis and design. CRC Press.", styles["small"]),
        p("Roberts, J. C., Headleand, C. J., & Ritsos, P. D. (2017). Five Design-Sheets: Creative design and sketching for computing and visualisation. Springer.", styles["small"]),
        p("Shneiderman, B. (1996). The eyes have it: A task by data type taxonomy for information visualizations. Proceedings of the IEEE Symposium on Visual Languages, 336-343.", styles["small"]),
        p("Tufte, E. R. (2001). The visual display of quantitative information (2nd ed.). Graphics Press.", styles["small"]),
        p("World Meteorological Organization. (2023). Climate indicators and sustainable development: Demonstrating the interconnections (WMO-No. 1290). https://library.wmo.int/idurl/4/68695", styles["small"]),
        PageBreak(),
        p("Appendix A: Five Design Sheets", styles["h1"]),
        p(
            "The following five pages reproduce the Five Design Sheets from the Part 1 design presentation: brainstorming, three alternative complete designs, and the final realisation used as the basis for the implemented D3 narrative visualisation.",
            styles["body"],
        ),
    ]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def append_design_sheets():
    writer = PdfWriter()
    body = PdfReader(str(BODY_PDF))
    for page in body.pages:
        writer.add_page(page)

    appendix = PdfReader(str(PRESENTATION_PDF))
    # Pages 2-6 of the presentation are the five design sheets.
    for index in range(1, 6):
        writer.add_page(appendix.pages[index])

    with FINAL_PDF.open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    build_body()
    append_design_sheets()
    print(FINAL_PDF)
