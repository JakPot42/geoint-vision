"""pdf_report.py — assembles the three-panel figure + change stats +
vision analysis into a GEOINT-style change brief PDF (ReportLab)."""
from __future__ import annotations

import datetime as _dt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer

import config


def _banner(text: str, styles) -> Paragraph:
    style = ParagraphStyle(
        "Banner", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8,
        textColor=colors.white, alignment=TA_CENTER, backColor=colors.HexColor("#7a1f1f"),
        borderPadding=(4, 4, 4, 4), leading=11,
    )
    return Paragraph(text, style)


def build_change_brief_pdf(
    output_path: str, figure_path: str, analysis_text: str,
    location_name: str, before_date: str, after_date: str,
) -> str:
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=16, alignment=TA_CENTER)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#475569"))
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, alignment=TA_LEFT, leading=13, fontName="Courier")

    story = [
        _banner(config.SCOPE_DISCLAIMER, styles),
        Spacer(1, 10),
        Paragraph("GEOINT Vision Pipeline", title_style),
        Paragraph("Change Detection Brief", styles["Heading2"]),
        Paragraph(
            f"{location_name} &nbsp;|&nbsp; {before_date} vs {after_date} &nbsp;|&nbsp; "
            f"Generated: {_dt.datetime.now():%Y-%m-%d %H:%M} &nbsp;|&nbsp; DEMO_MODE={config.DEMO_MODE}",
            meta_style,
        ),
        Spacer(1, 10),
        HRFlowable(width="100%", color=colors.HexColor("#1e293b")),
        Spacer(1, 10),
        Image(figure_path, width=7.3 * inch, height=7.3 * inch * (5.5 / 15.0)),
        Spacer(1, 12),
    ]

    for para in analysis_text.split("\n\n"):
        safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))
    story.append(_banner(config.SCOPE_DISCLAIMER, styles))

    doc.build(story)
    return output_path
