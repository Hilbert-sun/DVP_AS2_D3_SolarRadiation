from pathlib import Path
import math
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "fds_revised"
PDF_PATH = ROOT / "SUNZHEN_36446874_FDS_Revised.pdf"

WIDTH = 1600
HEIGHT = 900
MARGIN = 42

PAPER = "#fbfaf7"
INK = "#202124"
MUTED = "#666a70"
LIGHT = "#e2e0da"
PANEL = "#ffffff"
PANEL_ALT = "#f4f3ef"
BLUE = "#486a88"
ORANGE = "#ad6845"
GREEN = "#657d68"
RED = "#9a5d58"

FONT_REGULAR = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")
FONT_HAND = Path(r"C:\Windows\Fonts\segoepr.ttf")
FONT_HAND_BOLD = Path(r"C:\Windows\Fonts\segoeprb.ttf")


def font(size, bold=False, hand=False):
    if hand and bold:
        path = FONT_HAND_BOLD
    elif hand:
        path = FONT_HAND
    elif bold:
        path = FONT_BOLD
    else:
        path = FONT_REGULAR
    return ImageFont.truetype(str(path), size)


F_TITLE = font(34, bold=True)
F_SUBTITLE = font(17)
F_H1 = font(22, bold=True)
F_H2 = font(16, bold=True)
F_BODY = font(14)
F_SMALL = font(12)
F_NOTE = font(16, hand=True)
F_NOTE_BOLD = font(18, bold=True, hand=True)


def text_width(draw, text, fnt):
    return draw.textbbox((0, 0), text, font=fnt)[2]


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if text_width(draw, trial, fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill=INK, max_width=400, line_gap=4):
    x, y = xy
    lines = wrap(draw, text, fnt, max_width)
    line_height = fnt.getbbox("Ag")[3] - fnt.getbbox("Ag")[1] + line_gap
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def box(draw, bounds, fill=PANEL, outline=LIGHT, width=2, radius=8):
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def hand_line(draw, points, fill=INK, width=3, seed=0, jitter=1.2):
    rng = random.Random(seed)
    rough = []
    for x, y in points:
        rough.append((x + rng.uniform(-jitter, jitter), y + rng.uniform(-jitter, jitter)))
    draw.line(rough, fill=fill, width=width, joint="curve")


def arrow(draw, start, end, fill=INK, width=3, seed=0):
    hand_line(draw, [start, end], fill=fill, width=width, seed=seed)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 14
    spread = 0.55
    p1 = (
        end[0] - length * math.cos(angle - spread),
        end[1] - length * math.sin(angle - spread),
    )
    p2 = (
        end[0] - length * math.cos(angle + spread),
        end[1] - length * math.sin(angle + spread),
    )
    draw.polygon([end, p1, p2], fill=fill)


def header(draw, sheet_no, title, subtitle):
    draw.text((MARGIN, 28), f"FIVE DESIGN SHEETS / SHEET {sheet_no}", font=F_SMALL, fill=MUTED)
    draw.text((MARGIN, 52), title, font=F_TITLE, fill=INK)
    draw.text((MARGIN, 102), subtitle, font=F_SUBTITLE, fill=MUTED)
    draw.line((MARGIN, 137, WIDTH - MARGIN, 137), fill=INK, width=2)


def footer(draw, text):
    draw.line((MARGIN, HEIGHT - 42, WIDTH - MARGIN, HEIGHT - 42), fill=LIGHT, width=1)
    draw.text((MARGIN, HEIGHT - 32), text, font=F_SMALL, fill=MUTED)
    right = "Sun Zhen / 36446874"
    draw.text((WIDTH - MARGIN - text_width(draw, right, F_SMALL), HEIGHT - 32), right, font=F_SMALL, fill=MUTED)


def label(draw, xy, text, fill=INK, hand=False):
    draw.text(xy, text, font=F_NOTE_BOLD if hand else F_H2, fill=fill)


def note(draw, bounds, title, body, accent=BLUE, seed=0):
    x1, y1, x2, y2 = bounds
    box(draw, bounds, fill="#fffefb", outline=accent, width=2, radius=6)
    hand_line(draw, [(x1 + 12, y1 + 11), (x1 + 12, y2 - 11)], fill=accent, width=4, seed=seed)
    draw.text((x1 + 25, y1 + 12), title, font=F_NOTE_BOLD, fill=accent)
    draw_wrapped(draw, (x1 + 25, y1 + 42), body, F_NOTE, fill=INK, max_width=x2 - x1 - 42, line_gap=3)


def chart_axes(draw, bounds, x_label="", y_label="", seed=0):
    x1, y1, x2, y2 = bounds
    left = x1 + 36
    bottom = y2 - 30
    top = y1 + 18
    right = x2 - 16
    hand_line(draw, [(left, top), (left, bottom), (right, bottom)], fill=MUTED, width=2, seed=seed)
    if x_label:
        draw.text((right - text_width(draw, x_label, F_SMALL), bottom + 8), x_label, font=F_SMALL, fill=MUTED)
    if y_label:
        draw.text((x1 + 2, top - 4), y_label, font=F_SMALL, fill=MUTED)
    return left, top, right, bottom


def sketch_line_chart(draw, bounds, title, series=2, seed=0, labels=None):
    x1, y1, x2, y2 = bounds
    draw.text((x1 + 10, y1 + 4), title, font=F_H2, fill=INK)
    left, top, right, bottom = chart_axes(draw, (x1 + 4, y1 + 24, x2 - 4, y2 - 4), "time", "value", seed)
    colors = [BLUE, ORANGE, GREEN, "#77639a"]
    patterns = [
        [0.20, 0.26, 0.34, 0.49, 0.43, 0.58, 0.68, 0.62, 0.72, 0.67],
        [0.72, 0.63, 0.57, 0.52, 0.48, 0.42, 0.36, 0.40, 0.31, 0.35],
        [0.18, 0.23, 0.30, 0.41, 0.54, 0.70, 0.65, 0.58, 0.47, 0.35],
        [0.48, 0.55, 0.63, 0.70, 0.73, 0.67, 0.58, 0.42, 0.28, 0.20],
    ]
    for idx in range(series):
        pts = []
        for i, value in enumerate(patterns[idx]):
            x = left + (right - left) * i / (len(patterns[idx]) - 1)
            y = bottom - (bottom - top) * value
            pts.append((x, y))
        hand_line(draw, pts, fill=colors[idx], width=3, seed=seed + idx + 1)
    if labels:
        y = y1 + 30
        for idx, item in enumerate(labels):
            draw.line((x2 - 92, y + idx * 17, x2 - 75, y + idx * 17), fill=colors[idx], width=3)
            draw.text((x2 - 68, y - 7 + idx * 17), item, font=F_SMALL, fill=MUTED)


def sketch_scatter(draw, bounds, title, seed=0, selected=False):
    x1, y1, x2, y2 = bounds
    draw.text((x1 + 10, y1 + 4), title, font=F_H2, fill=INK)
    left, top, right, bottom = chart_axes(draw, (x1 + 4, y1 + 24, x2 - 4, y2 - 4), "SUN", "GSR", seed)
    rng = random.Random(seed)
    for _ in range(70):
        u = rng.random()
        x = left + u * (right - left)
        trend = 0.12 + 0.72 * u + rng.uniform(-0.18, 0.18)
        y = bottom - max(0.03, min(0.95, trend)) * (bottom - top)
        radius = rng.choice([2, 2, 3, 4])
        fill = rng.choice([BLUE, BLUE, GREEN, ORANGE])
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=None)
    if selected:
        sx = left + 0.82 * (right - left)
        sy = bottom - 0.82 * (bottom - top)
        draw.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), outline=RED, width=3)
        arrow(draw, (sx + 55, sy - 35), (sx + 9, sy - 8), fill=RED, width=2, seed=seed + 99)
        draw.text((sx + 57, sy - 47), "selected date", font=F_NOTE, fill=RED)


def sketch_bar(draw, bounds, title, seed=0):
    x1, y1, x2, y2 = bounds
    draw.text((x1 + 10, y1 + 4), title, font=F_H2, fill=INK)
    left, top, right, bottom = chart_axes(draw, (x1 + 4, y1 + 24, x2 - 4, y2 - 4), "", "count", seed)
    values = [0.0, 0.37, 0.92, 0.08]
    names = ["Win", "Spr", "Sum", "Aut"]
    gap = (right - left) / 4
    bar_pad = min(12, max(2, gap * 0.22))
    for idx, value in enumerate(values):
        bx1 = left + gap * idx + bar_pad
        bx2 = left + gap * (idx + 1) - bar_pad
        by = bottom - value * (bottom - top)
        draw.rectangle((bx1, by, bx2, bottom), fill=ORANGE, outline=INK, width=1)
        draw.text((bx1, bottom + 5), names[idx], font=F_SMALL, fill=MUTED)


def sketch_table(draw, bounds, title, rows=5):
    x1, y1, x2, y2 = bounds
    draw.text((x1 + 10, y1 + 4), title, font=F_H2, fill=INK)
    top = y1 + 30
    row_h = max(15, (y2 - top - 8) / (rows + 1))
    inner_left = x1 + 10
    inner_right = x2 - 10
    inner_width = inner_right - inner_left
    cols = [
        inner_left,
        inner_left + inner_width * 0.42,
        inner_left + inner_width * 0.64,
        inner_left + inner_width * 0.82,
        inner_right,
    ]
    for c in cols:
        draw.line((c, top, c, top + row_h * (rows + 1)), fill=LIGHT, width=1)
    for r in range(rows + 2):
        y = top + row_h * r
        draw.line((x1 + 10, y, x2 - 10, y), fill=LIGHT, width=1)
    headers = ["Date", "GSR", "SUN", "RF"]
    for idx, item in enumerate(headers):
        draw.text((cols[idx] + 5, top + 2), item, font=F_SMALL, fill=INK)
    for r in range(rows):
        draw.line((cols[0] + 7, top + row_h * (r + 1) + row_h / 2, cols[0] + 65, top + row_h * (r + 1) + row_h / 2), fill=BLUE, width=2)


def new_sheet(sheet_no, title, subtitle):
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    header(draw, sheet_no, title, subtitle)
    return image, draw


def sheet_1():
    image, draw = new_sheet(
        1,
        "Brainstorming the solar radiation story",
        "Divergent ideas, evidence questions, and early chart sketches before implementation.",
    )

    note(
        draw,
        (50, 165, 585, 275),
        "Central audience question",
        "How can Hong Kong planners understand when solar radiation is strongest, what weather conditions explain it, and when extreme opportunities occur?",
        accent=BLUE,
        seed=1,
    )

    draw.text((630, 165), "Working hypotheses", font=F_H1, fill=INK)
    hypotheses = [
        ("H1", "GSR and rainfall move in opposite directions."),
        ("H2", "Sunshine duration is the strongest positive association; humidity is negative."),
        ("H3", "Extreme GSR days cluster in high-sunshine, low-rainfall seasons."),
    ]
    y = 205
    for idx, (code, body) in enumerate(hypotheses):
        draw.ellipse((635, y - 2, 675, y + 38), fill=PANEL, outline=ORANGE, width=2)
        draw.text((644, y + 5), code, font=F_H2, fill=ORANGE)
        draw_wrapped(draw, (690, y), body, F_BODY, fill=INK, max_width=430)
        y += 62

    draw.text((1140, 165), "Ideas removed or simplified", font=F_H1, fill=INK)
    removed = [
        "Map: one station cannot support a spatial claim",
        "Raw daily line chart: too noisy across 11,887 days",
        "Dense pairplot: too analytical for the target audience",
    ]
    y = 205
    for idx, item in enumerate(removed):
        draw_wrapped(draw, (1150, y), item, F_BODY, fill=MUTED, max_width=365)
        hand_line(draw, [(1145, y + 10), (1510, y + 10)], fill=RED, width=2, seed=20 + idx, jitter=2)
        y += 58

    draw.text((50, 345), "Candidate visual encodings", font=F_H1, fill=INK)
    chart_boxes = [
        (50, 385, 400, 590, "Annual GSR vs rainfall", "long-term context"),
        (430, 385, 780, 590, "Monthly climate rhythm", "compare different units"),
        (810, 385, 1160, 590, "SUN-GSR scatter", "daily relationship"),
        (1190, 385, 1540, 590, "Extreme days by season", "rare-event evidence"),
    ]
    for idx, (x1, y1, x2, y2, title, _) in enumerate(chart_boxes):
        box(draw, (x1, y1, x2, y2), fill=PANEL, outline=LIGHT, width=2)
        if idx == 0:
            sketch_line_chart(draw, (x1 + 8, y1 + 8, x2 - 8, y2 - 34), title, series=2, seed=31)
        elif idx == 1:
            sketch_line_chart(draw, (x1 + 8, y1 + 8, x2 - 8, y2 - 34), title, series=4, seed=32)
        elif idx == 2:
            sketch_scatter(draw, (x1 + 8, y1 + 8, x2 - 8, y2 - 34), title, seed=33)
        else:
            sketch_bar(draw, (x1 + 8, y1 + 8, x2 - 8, y2 - 34), title, seed=34)
        draw.text((x1 + 12, y2 - 26), chart_boxes[idx][5], font=F_NOTE, fill=BLUE)

    arrow(draw, (215, 610), (215, 665), fill=BLUE, seed=41)
    arrow(draw, (595, 610), (595, 665), fill=BLUE, seed=42)
    arrow(draw, (975, 610), (975, 665), fill=BLUE, seed=43)
    arrow(draw, (1355, 610), (1355, 665), fill=BLUE, seed=44)

    draw.text((50, 680), "Possible interactions and narrative structure", font=F_H1, fill=INK)
    interactions = [
        ("Story steps", "Move from context to explanation to action."),
        ("Year + season filters", "Let planners focus without turning the story into a general dashboard."),
        ("Tooltips", "Preserve raw values when standardised views are used."),
        ("Linked extreme date", "Trace one summary record back to the daily scatterplot."),
    ]
    x = 50
    for idx, (title, body) in enumerate(interactions):
        box(draw, (x, 725, x + 350, 825), fill=PANEL_ALT, outline=LIGHT, width=1)
        draw.text((x + 14, 738), title, font=F_H2, fill=INK)
        draw_wrapped(draw, (x + 14, 766), body, F_BODY, fill=MUTED, max_width=320)
        x += 380

    footer(draw, "Sheet 1 records the initial divergence before choosing complete interface alternatives.")
    return image


def sheet_2():
    image, draw = new_sheet(
        2,
        "Alternative A: Scrollytelling climate story",
        "A linear article-style experience where each scroll section introduces one visual claim.",
    )

    draw.text((50, 165), "Complete interface sketch", font=F_H1, fill=INK)
    box(draw, (50, 205, 1040, 820), fill=PANEL, outline=INK, width=2)
    draw.rectangle((70, 225, 1020, 290), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((95, 242), "WHEN SUNSHINE MEETS RAIN", font=F_H1, fill=INK)
    draw.text((95, 272), "A guided climate story for Hong Kong planners", font=F_BODY, fill=MUTED)

    section_y = [320, 435, 550, 665]
    section_titles = [
        "01 Long-term climate context",
        "02 Seasonal rhythm",
        "03 Daily sunshine relationship",
        "04 Extreme solar days",
    ]
    for idx, y in enumerate(section_y):
        draw.text((95, y + 12), section_titles[idx], font=F_H2, fill=INK)
        draw_wrapped(
            draw,
            (95, y + 40),
            "Short narrative paragraph explains the claim before the reader encounters the chart.",
            F_SMALL,
            fill=MUTED,
            max_width=300,
        )
        chart_bounds = (450, y, 950, y + 96)
        if idx == 0:
            sketch_line_chart(draw, chart_bounds, "", series=2, seed=101)
        elif idx == 1:
            sketch_line_chart(draw, chart_bounds, "", series=4, seed=102)
        elif idx == 2:
            sketch_scatter(draw, chart_bounds, "", seed=103)
        else:
            sketch_bar(draw, chart_bounds, "", seed=104)
        if idx < 3:
            arrow(draw, (970, y + 78), (970, y + 110), fill=BLUE, width=2, seed=110 + idx)

    draw.text((1090, 165), "Interaction sketch", font=F_H1, fill=INK)
    note(
        draw,
        (1090, 205, 1540, 315),
        "Scroll activates each chart",
        "The active section changes opacity and reveals its annotation. Hover provides exact values.",
        accent=BLUE,
        seed=120,
    )
    note(
        draw,
        (1090, 340, 1540, 450),
        "Strength",
        "Very clear narrative sequence for a non-technical audience.",
        accent=GREEN,
        seed=121,
    )
    note(
        draw,
        (1090, 475, 1540, 585),
        "Risk",
        "Readers cannot easily compare steps or return to a previous view while keeping filters.",
        accent=RED,
        seed=122,
    )
    note(
        draw,
        (1090, 610, 1540, 750),
        "Decision",
        "Keep the guided sequencing, but move away from a purely linear scroll so users can revisit evidence and use focused controls.",
        accent=ORANGE,
        seed=123,
    )
    footer(draw, "Alternative A tests strong guidance, but comparison flexibility is limited.")
    return image


def sheet_3():
    image, draw = new_sheet(
        3,
        "Alternative B: Guided story dashboard",
        "A stable workspace with explicit story steps, a main chart, an insight panel, and focused controls.",
    )

    draw.text((50, 165), "Complete interface sketch", font=F_H1, fill=INK)
    box(draw, (50, 205, 1190, 765), fill=PANEL, outline=INK, width=2)
    draw.rectangle((70, 225, 1170, 285), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((95, 242), "WHEN SUNSHINE MEETS RAIN", font=F_H1, fill=INK)
    draw.text((95, 270), "Narrative dashboard", font=F_SMALL, fill=MUTED)

    box(draw, (80, 315, 300, 650), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((100, 333), "STORY STEPS", font=F_H2, fill=INK)
    steps = [
        "1. Long-term context",
        "2. Seasonal rhythm",
        "3. Sunshine relationship",
        "4. Extreme days",
        "5. Planning takeaway",
    ]
    y = 375
    for idx, step in enumerate(steps):
        fill = "#e8edf1" if idx == 2 else PANEL
        outline = BLUE if idx == 2 else LIGHT
        box(draw, (100, y, 280, y + 38), fill=fill, outline=outline, width=1, radius=5)
        draw.text((112, y + 9), step, font=F_SMALL, fill=BLUE if idx == 2 else INK)
        y += 50

    box(draw, (325, 315, 860, 650), fill=PANEL, outline=LIGHT, width=1)
    sketch_scatter(draw, (350, 345, 835, 610), "SUN-GSR daily relationship", seed=201)

    box(draw, (885, 315, 1150, 650), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((905, 335), "INSIGHT PANEL", font=F_H2, fill=INK)
    draw_wrapped(
        draw,
        (905, 375),
        "Explain the selected view in plain language. Keep interpretation beside the chart rather than over the marks.",
        F_BODY,
        fill=MUTED,
        max_width=220,
    )
    note(
        draw,
        (900, 500, 1135, 620),
        "Design principle",
        "Chart first, interpretation second.",
        accent=BLUE,
        seed=202,
    )

    draw.rectangle((80, 675, 1150, 735), fill=PANEL_ALT, outline=LIGHT, width=1)
    controls = ["Year range", "Season", "Extreme toggle", "Reset"]
    x = 105
    for idx, item in enumerate(controls):
        draw.text((x, 690), item, font=F_SMALL, fill=MUTED)
        box(draw, (x, 710, x + 190, 728), fill=PANEL, outline=LIGHT, width=1, radius=4)
        x += 255

    draw.text((1240, 165), "Step-specific chart sketches", font=F_H1, fill=INK)
    sketches = [
        ("Step 1", "annual line"),
        ("Step 2", "monthly rhythm"),
        ("Step 3", "scatter"),
        ("Step 4", "bar + table"),
    ]
    y = 215
    for idx, (step, desc) in enumerate(sketches):
        box(draw, (1240, y, 1545, y + 120), fill=PANEL, outline=LIGHT, width=1)
        draw.text((1255, y + 10), f"{step}: {desc}", font=F_SMALL, fill=INK)
        if idx == 0:
            sketch_line_chart(draw, (1250, y + 28, 1535, y + 110), "", series=2, seed=210 + idx)
        elif idx == 1:
            sketch_line_chart(draw, (1250, y + 28, 1535, y + 110), "", series=4, seed=210 + idx)
        elif idx == 2:
            sketch_scatter(draw, (1250, y + 28, 1535, y + 110), "", seed=210 + idx)
        else:
            draw.text((1258, y + 48), "season", font=F_SMALL, fill=MUTED)
            for bx, bh in [(1310, 5), (1330, 13), (1350, 30), (1370, 7)]:
                draw.rectangle((bx, y + 95 - bh, bx + 12, y + 95), fill=ORANGE, outline=INK, width=1)
            sketch_table(draw, (1395, y + 25, 1535, y + 110), "", rows=3)
        y += 135

    note(
        draw,
        (1240, 760, 1545, 825),
        "Selected direction",
        "Guided, but easy to revisit.",
        accent=GREEN,
        seed=220,
    )
    footer(draw, "Alternative B becomes the structural basis of the final implementation.")
    return image


def sheet_4():
    image, draw = new_sheet(
        4,
        "Alternative C: Seasonal and extreme-event explorer",
        "A task-focused concept that prioritises monthly climate rhythm and rare high-radiation days.",
    )

    draw.text((50, 165), "Complete interface sketch", font=F_H1, fill=INK)
    box(draw, (50, 205, 1180, 780), fill=PANEL, outline=INK, width=2)
    draw.rectangle((70, 225, 1160, 285), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((95, 242), "SOLAR OPPORTUNITY EXPLORER", font=F_H1, fill=INK)
    draw.text((95, 270), "Seasonal patterns and extreme high-GSR days", font=F_SMALL, fill=MUTED)

    tabs = ["Seasonal rhythm", "Extreme days", "Record details"]
    x = 90
    for idx, tab in enumerate(tabs):
        fill = "#e8edf1" if idx == 0 else PANEL
        outline = BLUE if idx == 0 else LIGHT
        box(draw, (x, 310, x + 190, 345), fill=fill, outline=outline, width=1, radius=5)
        draw.text((x + 20, 319), tab, font=F_SMALL, fill=BLUE if idx == 0 else INK)
        x += 205

    box(draw, (90, 370, 720, 610), fill=PANEL, outline=LIGHT, width=1)
    sketch_line_chart(
        draw,
        (110, 390, 700, 590),
        "Monthly climate rhythm",
        series=4,
        seed=301,
        labels=["GSR", "RF", "SUN", "RH"],
    )

    box(draw, (750, 370, 1135, 610), fill=PANEL, outline=LIGHT, width=1)
    sketch_bar(draw, (770, 390, 1115, 590), "Extreme days by season", seed=302)

    card_titles = ["Extreme count", "Average GSR", "Average SUN", "Average RF"]
    x = 90
    for idx, title in enumerate(card_titles):
        box(draw, (x, 635, x + 245, 710), fill=PANEL_ALT, outline=LIGHT, width=1)
        draw.text((x + 15, 648), title, font=F_SMALL, fill=MUTED)
        draw.text((x + 15, 675), ["595", "25.79", "10.85", "0.47"][idx], font=F_H1, fill=ORANGE)
        x += 260

    draw.text((1230, 165), "Interaction and evidence notes", font=F_H1, fill=INK)
    note(
        draw,
        (1230, 205, 1545, 330),
        "Season first",
        "The concept makes monthly peaks, troughs, and summer clustering immediately visible.",
        accent=GREEN,
        seed=310,
    )
    note(
        draw,
        (1230, 355, 1545, 480),
        "Extreme evidence",
        "Summary cards and a top-record table make rare events concrete rather than abstract.",
        accent=ORANGE,
        seed=311,
    )
    note(
        draw,
        (1230, 505, 1545, 630),
        "Risk",
        "It is weaker at explaining the full long-term story and the daily SUN-GSR relationship.",
        accent=RED,
        seed=312,
    )
    note(
        draw,
        (1230, 655, 1545, 800),
        "Decision",
        "Carry the seasonal and extreme-event components into the guided dashboard from Sheet 3.",
        accent=BLUE,
        seed=313,
    )
    footer(draw, "Alternative C contributes the strongest seasonal and extreme-event evidence.")
    return image


def sheet_5():
    image, draw = new_sheet(
        5,
        "Final realisation: Guided five-step narrative",
        "The implementable design combines Sheet 3's stable narrative workspace with Sheet 4's seasonal and extreme-event evidence.",
    )

    note(
        draw,
        (50, 160, 690, 265),
        "Refinement after Part 1 feedback",
        "Draft chart sketches, interaction arrows, and implementation annotations were added so the design communicates what each story step will actually show.",
        accent=ORANGE,
        seed=401,
    )
    note(
        draw,
        (720, 160, 1545, 265),
        "Evidence-aware refinement",
        "The final wording does not overclaim humidity: extreme days are most clearly high-sunshine, low-rainfall summer events, while humidity is supporting context.",
        accent=BLUE,
        seed=402,
    )

    box(draw, (50, 285, 1210, 800), fill=PANEL, outline=INK, width=2)
    draw.rectangle((70, 305, 1190, 365), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((95, 321), "WHEN SUNSHINE MEETS RAIN", font=F_H1, fill=INK)
    draw.text((95, 350), "Understanding solar radiation patterns at King's Park, Hong Kong", font=F_SMALL, fill=MUTED)

    box(draw, (80, 390, 295, 690), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((100, 407), "STORY STEPS", font=F_H2, fill=INK)
    steps = [
        "1. Long-term context",
        "2. Seasonal rhythm",
        "3. Sunshine relationship",
        "4. Extreme days",
        "5. Planning takeaway",
    ]
    y = 448
    for idx, step in enumerate(steps):
        fill = "#e8edf1" if idx == 3 else PANEL
        outline = BLUE if idx == 3 else LIGHT
        box(draw, (100, y, 275, y + 35), fill=fill, outline=outline, width=1, radius=5)
        draw.text((110, y + 8), step, font=F_SMALL, fill=BLUE if idx == 3 else INK)
        y += 46

    box(draw, (320, 390, 850, 690), fill=PANEL, outline=LIGHT, width=1)
    draw.text((340, 407), "MAIN VISUALISATION", font=F_H2, fill=INK)
    sketch_bar(draw, (345, 440, 570, 635), "Extreme days by season", seed=410)
    sketch_table(draw, (585, 440, 830, 635), "Top records", rows=5)
    arrow(draw, (710, 650), (485, 650), fill=ORANGE, width=2, seed=411)
    draw.text((520, 655), "click date -> trace in Step 3 scatter", font=F_NOTE, fill=ORANGE)

    box(draw, (875, 390, 1170, 690), fill=PANEL_ALT, outline=LIGHT, width=1)
    draw.text((895, 407), "INSIGHT PANEL", font=F_H2, fill=INK)
    draw_wrapped(
        draw,
        (895, 448),
        "The top 5% GSR days are concentrated in summer and are characterised most clearly by high sunshine duration and very low rainfall.",
        F_BODY,
        fill=MUTED,
        max_width=245,
    )
    draw_wrapped(
        draw,
        (895, 570),
        "Relative humidity is only slightly lower on average.",
        F_BODY,
        fill=BLUE,
        max_width=245,
    )

    draw.rectangle((80, 715, 1170, 770), fill=PANEL_ALT, outline=LIGHT, width=1)
    controls = ["Year range", "Season filter", "Extreme-day toggle", "Reset"]
    x = 105
    for item in controls:
        draw.text((x, 728), item, font=F_SMALL, fill=MUTED)
        box(draw, (x, 748, x + 205, 764), fill=PANEL, outline=LIGHT, width=1, radius=4)
        x += 260

    draw.text((1250, 285), "Five-step evidence plan", font=F_H1, fill=INK)
    evidence = [
        ("1", "Annual line", "Test H1 across years"),
        ("2", "Monthly rhythm", "Show seasonal overlap"),
        ("3", "SUN-GSR scatter", "Test H2 in daily data"),
        ("4", "Bar + table", "Test H3 and trace records"),
        ("5", "Takeaway cards", "Translate evidence for planners"),
    ]
    y = 335
    for idx, (number, title, body) in enumerate(evidence):
        draw.ellipse((1255, y, 1290, y + 35), fill=PANEL, outline=BLUE, width=2)
        draw.text((1267, y + 6), number, font=F_SMALL, fill=BLUE)
        draw.text((1305, y), title, font=F_H2, fill=INK)
        draw_wrapped(draw, (1305, y + 25), body, F_SMALL, fill=MUTED, max_width=230)
        if idx < len(evidence) - 1:
            arrow(draw, (1272, y + 42), (1272, y + 73), fill=LIGHT, width=2, seed=420 + idx)
        y += 88

    note(
        draw,
        (1245, 755, 1545, 835),
        "Implementation",
        "D3.js + local CSV + state.",
        accent=GREEN,
        seed=430,
    )
    footer(draw, "Sheet 5 is the final design specification used to guide the implemented D3 narrative.")
    return image


def build_pdf(image_paths):
    page_w, page_h = landscape(A4)
    pdf = canvas.Canvas(str(PDF_PATH), pagesize=(page_w, page_h))
    for image_path in image_paths:
        pdf.drawImage(str(image_path), 0, 0, width=page_w, height=page_h)
        pdf.showPage()
    pdf.save()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheets = [sheet_1(), sheet_2(), sheet_3(), sheet_4(), sheet_5()]
    image_paths = []
    for index, image in enumerate(sheets, start=1):
        path = OUT_DIR / f"sheet{index}_revised.png"
        image.save(path, "PNG", optimize=True)
        image_paths.append(path)
    build_pdf(image_paths)
    print(PDF_PATH)
    for path in image_paths:
        print(path)


if __name__ == "__main__":
    main()
