from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
BODY_PDF = ROOT / "SUNZHEN_36446874_Report_body.pdf"
FINAL_PDF = ROOT / "SUNZHEN_36446874_Report.pdf"
FDS_PDF = ROOT / "SUNZHEN_36446874_Presentation.pdf"
FDS_DIR = ROOT / "fds_revised"
SCREENSHOTS = ROOT / "report_screenshots"

FONT_BODY = "TimesNewRoman"
FONT_BODY_BOLD = "TimesNewRoman-Bold"
FONT_BODY_ITALIC = "TimesNewRoman-Italic"


def register_fonts():
    fonts_dir = Path(r"C:\Windows\Fonts")
    pdfmetrics.registerFont(TTFont(FONT_BODY, str(fonts_dir / "times.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BODY_BOLD, str(fonts_dir / "timesbd.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BODY_ITALIC, str(fonts_dir / "timesi.ttf")))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", str(fonts_dir / "timesbi.ttf")))
    pdfmetrics.registerFontFamily(
        FONT_BODY,
        normal=FONT_BODY,
        bold=FONT_BODY_BOLD,
        italic=FONT_BODY_ITALIC,
        boldItalic="TimesNewRoman-BoldItalic",
    )


register_fonts()


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName=FONT_BODY_BOLD,
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=18,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base["Normal"],
            fontName=FONT_BODY,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName=FONT_BODY_BOLD,
            fontSize=15.5,
            leading=20,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName=FONT_BODY_BOLD,
            fontSize=12.2,
            leading=16,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=FONT_BODY,
            fontSize=10.1,
            leading=14.9,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "body_indent": ParagraphStyle(
            "BodyIndent",
            parent=base["BodyText"],
            fontName=FONT_BODY,
            fontSize=9.9,
            leading=14.2,
            leftIndent=14,
            firstLineIndent=-14,
            spaceAfter=4.5,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=FONT_BODY,
            fontSize=8.8,
            leading=11.7,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName=FONT_BODY_ITALIC,
            fontSize=8.6,
            leading=11,
            textColor=colors.HexColor("#444444"),
            spaceBefore=3,
            spaceAfter=8,
        ),
        "toc": ParagraphStyle(
            "TOC",
            parent=base["BodyText"],
            fontName=FONT_BODY,
            fontSize=11,
            leading=17.5,
            leftIndent=0,
            spaceAfter=5,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName=FONT_BODY,
            fontSize=9.8,
            leading=14,
            textColor=colors.black,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.HexColor("#aaaaaa"),
            borderWidth=0.25,
            borderPadding=7,
            spaceBefore=5,
            spaceAfter=8,
        ),
    }


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_BODY, 8)
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
        bulletFontName=FONT_BODY,
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


def fds_fig(path, caption, styles, max_w=16.0 * cm, max_h=8.2 * cm):
    image_path = FDS_DIR / path
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
                ("FONTNAME", (0, 0), (-1, 0), FONT_BODY_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_BODY),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
                ("INNERGRID", (0, 0), (-1, -1), 0.18, colors.HexColor("#c8c8c8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def text_table(rows, col_widths, styles):
    paragraph_rows = []
    for row_index, row in enumerate(rows):
        style = styles["small"] if row_index else styles["small"]
        paragraph_rows.append([p(str(cell), style) for cell in row])
    table = Table(paragraph_rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BODY_BOLD),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
                ("INNERGRID", (0, 0), (-1, -1), 0.18, colors.HexColor("#cccccc")),
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
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#999999"))]))
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
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.55 * cm,
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
                ("3.3 Using the Implementation", "13"),
                ("4. Conclusion and Reflection", "13"),
                ("AI Declaration", "14"),
                ("References", "14"),
                ("Appendix A: Five Design Sheets", "15"),
            ],
            styles,
        ),
        PageBreak(),
    ]

    story += [
        p("1. Introduction", styles["h1"]),
        p(
            "This project presents an interactive narrative visualisation of solar radiation patterns at King's Park, Hong Kong. It transforms the data exploration findings into a guided D3.js interface for Hong Kong urban planners and environmental policy advisors. The submitted dataset contains 11,887 daily observations from 1992 to 2025, including global solar radiation (GSR), rainfall (RF), sunshine duration (SUN), and relative humidity (RH).",
            styles["body"],
        ),
        p(
            "The audience does not require a dense statistical dashboard, but it does require clear evidence that can support solar feasibility discussion, infrastructure planning, and climate-adaptation decisions. The design therefore uses a five-step narrative that moves from long-term context to seasonal rhythm, daily association, extreme events, and planning implications.",
            styles["body"],
        ),
        p("Hypotheses and validated findings", styles["h2"]),
        text_table(
            [
                ["<b>Hypothesis</b>", "<b>Result from the final dataset</b>", "<b>Interpretation used in the visualisation</b>"],
                [
                    "<b>H1:</b> GSR and rainfall are inversely related.",
                    "Supported, but not strongly deterministic. Daily GSR-RF correlation is r = -0.309 and annual GSR-RF correlation is r = -0.265.",
                    "Step 1 shows the inverse long-term tendency while retaining year-to-year variability.",
                ],
                [
                    "<b>H2:</b> Sunshine duration has the strongest positive relationship with GSR, while humidity is negative.",
                    "Supported. Daily SUN-GSR correlation is r = 0.909; RH-GSR correlation is r = -0.345.",
                    "Step 3 describes SUN as the strongest observed association, not as a causal predictor.",
                ],
                [
                    "<b>H3:</b> Extreme GSR days occur in high-sunshine, low-rainfall, low-humidity seasonal windows.",
                    "Partially supported and refined. The 595 top 5% GSR days average SUN 10.85 hours and RF 0.47 mm; 422 occur in summer. RH is only slightly lower than non-extreme days.",
                    "Step 4 emphasises high sunshine, very low rainfall, and summer concentration. Humidity is treated as supporting context rather than a defining signature.",
                ],
            ],
            [3.6 * cm, 6.2 * cm, 6.2 * cm],
            styles,
        ),
        Spacer(1, 0.2 * cm),
        p(
            "The final implementation is designed to be readable without the report: story navigation, chart titles, legends, tooltips, an insight panel, and planning takeaways communicate the narrative inside the interface itself. The wording is deliberately evidence-aware: association is not described as causation, and the humidity hypothesis is explicitly refined rather than overstated.",
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
            "The narrative structure moves from context to explanation and then to action: (1) long-term annual variability, (2) monthly seasonal rhythm, (3) the daily SUN-GSR relationship, (4) extreme solar radiation days, and (5) planning takeaways. This sequence reduces cognitive load by introducing simpler temporal patterns before the denser multivariate scatterplot and rare-event evidence.",
            styles["body"],
        ),
        p("2.2 Five Design Sheet Development", styles["h2"]),
        p(
            "The Part 1 demonstration feedback identified that the original design sheets needed clearer draft sketches. The revised Five Design Sheets in Appendix A preserve the original design intent, but they now communicate the proposed visual evidence more honestly and concretely through chart sketches, interaction arrows, layout annotations, and explicit design trade-offs. This revision is documented as a response to feedback rather than presented as if it existed before the Part 1 demonstration.",
            styles["body"],
        ),
        p(
            "Sheet 1 records divergent ideas: annual trend lines, monthly climate rhythm, a SUN-GSR scatterplot, extreme-day summaries, story steps, filters, tooltips, and linked date tracing. It also shows ideas that were removed. A map was rejected because the dataset represents one station rather than spatial variation; a raw daily line chart and dense pairplot were rejected because they would be too noisy for the target audience.",
            styles["body"],
        ),
        text_table(
            [
                ["<b>Sheet</b>", "<b>Complete design concept</b>", "<b>Decision</b>"],
                ["2", "Scrollytelling climate story: a linear article-style sequence with one claim and one chart per section.", "Retain the strong guidance, but reject the limited ability to revisit and compare evidence."],
                ["3", "Guided story dashboard: stable story navigation, main chart, insight panel, and focused controls.", "Selected as the structural basis of the implementation."],
                ["4", "Seasonal and extreme-event explorer: prioritises monthly rhythm, extreme-day counts, summary cards, and record details.", "Carry its strongest seasonal and rare-event evidence into the guided dashboard."],
                ["5", "Final realisation: a five-step narrative combining the structure of Sheet 3 with the evidence emphasis of Sheet 4.", "Used as the implementation specification for the D3.js application."],
            ],
            [1.1 * cm, 8.2 * cm, 6.7 * cm],
            styles,
        ),
        Spacer(1, 0.2 * cm),
        p(
            "A second change was made after the Part 1 design presentation: the original final sheet listed R Shiny as the intended implementation environment, but the final implementation uses D3.js. Direct SVG control, custom story-step state, and linked highlighting between views are more naturally implemented in D3 than in a Shiny layout based mainly on packaged chart outputs.",
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
            "The scatterplot uses position for SUN and GSR because position on common scales supports more accurate quantitative comparison than colour or area. Rainfall is encoded by point size and humidity by colour because they are contextual variables. This ordering reflects the narrative hierarchy: the SUN-GSR association is primary, rainfall helps explain wet low-radiation conditions, and humidity provides secondary context without being overclaimed as a defining extreme-day feature.",
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
        fds_fig(
            "sheet5_revised.png",
            "Revised Sheet 5 documents the final implementable design, chart sketches, interaction link, and evidence-aware wording.",
            styles,
            max_h=6.8 * cm,
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
            "For the default full-record view, the top 5% threshold is GSR 24.237 MJ/m2 and identifies 595 extreme days. The application does not treat this threshold as a universal physical definition; it is a relative threshold that updates when the current selection changes.",
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
            "Step 1 introduces long-term climate context. Because GSR and rainfall have different units, values are standardised for visual comparison while tooltips retain raw values. The annual GSR-RF correlation is r = -0.265, supporting an inverse tendency while also showing that rainfall does not fully determine annual solar radiation.",
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
            max_h=11.0 * cm,
        ),
        p(
            "Step 2 shifts from annual context to monthly seasonality. GSR and SUN both reach their highest monthly mean in July, while rainfall peaks in August and relative humidity peaks in June. This overlap shows that Hong Kong's summer solar opportunity exists within a wet and humid seasonal context, which is useful for planners considering both potential output and weather-related generation risk.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig4_sunshine_driver.png",
            "Figure 4. Step 3 shows sunshine duration as the clearest observed association with solar radiation.",
            styles,
            max_h=11.0 * cm,
        ),
        p(
            "Step 3 presents the strongest daily association identified during exploration: sunshine duration and global solar radiation, with r = 0.909. SUN is placed on the x-axis and GSR on the y-axis. Rainfall is encoded by point size and relative humidity by colour. When extreme-day highlighting is enabled, non-extreme points remain visible in the background so that peak events can be interpreted against the full daily context.",
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
            max_h=12.5 * cm,
        ),
        p(
            "Step 4 focuses on the top 5% of GSR observations in the current selection. In the default full-record view, the 595 extreme days average GSR 25.79 MJ/m2, SUN 10.85 hours, RF 0.47 mm, and RH 75.03%. Their seasonal distribution is strongly concentrated in summer: 422 occur in summer, 157 in spring, 16 in autumn, and none in winter. The very low rainfall and high sunshine are clear signatures; RH is only slightly lower than the non-extreme mean of 76.90%, so the final narrative does not overstate humidity.",
            styles["body"],
        ),
        p(
            "The top-10 table provides concrete examples, and its dates are linked: clicking a date jumps to Step 3 and highlights the same record in the scatterplot. This connection lets the reader move from a summary claim to an individual observation without losing the full daily context.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig7_linked_extreme_day.png",
            "Figure 6. A selected top-10 extreme date is traced from Step 4 into the Step 3 scatterplot.",
            styles,
            max_h=11.0 * cm,
        ),
        p(
            "The linked highlight is the most important coordinated interaction in the final implementation. It supports traceability between aggregate evidence and a specific record, while the dashed guide and annotation make the selected date visible without removing the surrounding observations.",
            styles["body"],
        ),
        PageBreak(),
    ]

    story += [
        p("3.2 Interactive Narrative Visualisation Implementation continued", styles["h2"]),
        fig(
            "fig6_planning_takeaway.png",
            "Figure 7. Step 5 translates the visual findings into planning takeaways.",
            styles,
            max_h=10.5 * cm,
        ),
        p(
            "Step 5 closes the narrative by translating the evidence into planning implications. It avoids adding a further complex chart because the goal is synthesis: solar potential is seasonally structured, sunshine duration has the clearest observed association, wet conditions reduce solar opportunity, and extreme high-radiation opportunities cluster in summer. Humidity is retained as supporting context rather than a headline conclusion.",
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
            "This project transformed exploratory climate analysis into an interactive narrative visualisation. The final evidence supports the main hypothesis that sunshine duration has the strongest observed daily association with GSR (r = 0.909) and supports an inverse relationship between GSR and rainfall (daily r = -0.309; annual r = -0.265). It also shows that the top 5% GSR days are primarily high-sunshine, very low-rainfall summer events.",
            styles["body"],
        ),
        p(
            "The humidity component of the original extreme-day hypothesis required refinement. Relative humidity is negatively associated with GSR overall, but extreme-day RH is only slightly lower than the non-extreme mean. The final visualisation therefore uses humidity as contextual encoding and avoids claiming that low humidity is a defining extreme-day signature. This is an important outcome of the design process: the narrative was changed to match the evidence rather than forcing the evidence to match the initial assumption.",
            styles["body"],
        ),
        p(
            "A key design trade-off was between analytical completeness and narrative clarity. A more technical interface could include regression models, seasonal correlation matrices, or additional meteorological variables, but this would increase cognitive load for the planning audience. The final design prioritises a coherent explanation of the strongest exploratory findings, supported by purposeful interaction and a documented response to Part 1 feedback.",
            styles["body"],
        ),
        p(
            "If extended further, the most valuable improvement would be stronger linked brushing across all views. Selecting a seasonal bar or an extreme-day record could highlight the same subset across the annual trend, monthly rhythm, scatterplot, and extreme-day table. A second improvement would be to incorporate urban-form variables such as roof geometry, shading, and electricity demand so that the visualisation could move from station-level climate evidence toward site-specific planning support.",
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
            "The following five pages contain the revised Five Design Sheets: brainstorming, three alternative complete designs, and the final realisation used as the basis for the implemented D3 narrative visualisation. These sheets were improved after the Part 1 demonstration feedback requested clearer draft chart sketches. The revision adds visual encodings, interaction arrows, evidence notes, and explicit design decisions while preserving the original design direction.",
            styles["body"],
        ),
    ]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def append_design_sheets():
    writer = PdfWriter()
    body = PdfReader(str(BODY_PDF))
    for page in body.pages:
        writer.add_page(page)

    appendix = PdfReader(str(FDS_PDF))
    for page in appendix.pages:
        writer.add_page(page)

    with FINAL_PDF.open("wb") as handle:
        writer.write(handle)
    BODY_PDF.unlink(missing_ok=True)


if __name__ == "__main__":
    build_body()
    append_design_sheets()
    print(FINAL_PDF)
