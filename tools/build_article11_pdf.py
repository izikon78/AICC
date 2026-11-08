"""Build the Draft 11 review PDF from its Markdown source and audited figures."""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
from urllib.parse import urljoin

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/article/AICC_Article_Draft_11.md"
WEB = "https://github.com/izikon78/AICC/blob/research/ain-article-draft-11/docs/article/"
WIDTH = letter[0] - 108


def register_fonts():
    directory = Path("C:/Windows/Fonts")
    fonts = {"Article": "arial.ttf", "ArticleBold": "arialbd.ttf", "ArticleItalic": "ariali.ttf",
             "ArticleMono": "consola.ttf"}
    for name, filename in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily("Article", normal="Article", bold="ArticleBold",
                                 italic="ArticleItalic", boldItalic="ArticleBold")


def inline(text):
    tokens = []

    def link(match):
        label, target = match.groups()
        target = target if target.startswith(("https://", "http://", "#")) else urljoin(WEB, target)
        tokens.append('<link color="#174B68" href="' + html.escape(target, quote=True) + '">'
                      + html.escape(label) + "</link>")
        return f"ARTICLELINK{len(tokens)-1}END"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="ArticleMono" size="9.5">\1</font>', text)
    for index, token in enumerate(tokens):
        text = text.replace(f"ARTICLELINK{index}END", token)
    return text


def styles():
    body = ParagraphStyle("body", fontName="Article", fontSize=10.6, leading=14.7,
                          spaceAfter=7, allowWidows=0, allowOrphans=0)
    return {
        "body": body,
        "title": ParagraphStyle("title", parent=body, fontName="ArticleBold", fontSize=23,
                                leading=27, spaceAfter=9, keepWithNext=True),
        "subtitle": ParagraphStyle("subtitle", parent=body, fontSize=12.3, leading=16.3,
                                   spaceAfter=8, keepWithNext=True),
        "heading": ParagraphStyle("heading", parent=body, fontName="ArticleBold", fontSize=14,
                                  leading=18, spaceBefore=13, spaceAfter=7, keepWithNext=True),
        "subheading": ParagraphStyle("subheading", parent=body, fontName="ArticleBold", fontSize=11.6,
                                     leading=15, spaceBefore=10, spaceAfter=6, keepWithNext=True),
        "code": ParagraphStyle("code", fontName="ArticleMono", fontSize=8.5, leading=10.8,
                               spaceBefore=2, spaceAfter=8, leftIndent=7),
        "cell": ParagraphStyle("cell", parent=body, fontSize=8.7, leading=11.4, spaceAfter=0),
        "header": ParagraphStyle("header", parent=body, fontName="ArticleBold", fontSize=8.7,
                                 leading=11.4, textColor=colors.white, spaceAfter=0),
        "caption": ParagraphStyle("caption", parent=body, fontSize=9.1, leading=12.3, spaceAfter=9),
        "reference": ParagraphStyle("reference", parent=body, fontSize=9, leading=12.2, spaceAfter=5),
        "label": ParagraphStyle("label", parent=body, fontName="ArticleBold", fontSize=9.4,
                                leading=12, spaceAfter=4, keepWithNext=True),
    }


def make_table(rows, sheet):
    ratios = {2: [0.28, 0.72], 3: [0.23, 0.41, 0.36],
              4: [0.28, 0.23, 0.25, 0.24], 5: [0.20, 0.20, 0.20, 0.20, 0.20]}
    fractions = ratios.get(len(rows[0]), [1 / len(rows[0])] * len(rows[0]))
    content = [[Paragraph(inline(cell), sheet["header"] if index == 0 else sheet["cell"])
                for cell in row] for index, row in enumerate(rows)]
    result = Table(content, colWidths=[WIDTH * value for value in fractions], repeatRows=1,
                   hAlign="LEFT", splitByRow=True)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234C63")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def build(output):
    register_fonts()
    sheet = styles()
    text = SOURCE.read_text(encoding="utf-8")
    if "{{" in text:
        raise ValueError("Article source still contains an unresolved placeholder")
    lines = text.splitlines()
    story = []
    index = 0
    references = False
    example_start = None
    example_headings = {"C# database access", "Python API request", "C++ thread management",
                        "Ruby grouped totals", "Java collection pipeline"}
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            index += 1
            code = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            if any(pdfmetrics.stringWidth(item, "ArticleMono", 8.5) > WIDTH - 14 for item in code):
                raise ValueError("A code line exceeds the print width")
            block = Preformatted("\n".join(code), sheet["code"])
            story.append(block if example_start is not None else KeepTogether([block]))
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            story.extend([make_table(rows, sheet), Spacer(1, 8)])
            continue
        image = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if image:
            from PIL import Image as PILImage
            path = SOURCE.parent / image.group(2)
            with PILImage.open(path) as source:
                width, height = source.size
            physical_width = 6.5 * inch
            graphic = Image(str(path), width=physical_width, height=physical_width * height / width)
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            group = [graphic, Spacer(1, 4)]
            if index < len(lines) and lines[index].startswith("Figure "):
                caption = []
                while index < len(lines) and lines[index].strip():
                    caption.append(lines[index].strip())
                    index += 1
                group.append(Paragraph(inline(" ".join(caption)), sheet["caption"]))
            story.append(KeepTogether(group))
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            heading = line.lstrip("#").strip()
            if example_start is not None:
                story[example_start:] = [KeepTogether(story[example_start:])]
                example_start = None
            if heading in example_headings:
                example_start = len(story)
            references = heading == "References"
            style = "title" if level == 1 else "subtitle" if index == 2 else "heading" if level == 2 else "subheading"
            story.append(Paragraph(inline(heading), sheet[style]))
            index += 1
            continue
        paragraph = [line]
        index += 1
        while (index < len(lines) and lines[index].strip()
               and not lines[index].lstrip().startswith(("#", "|", "```", "!["))
               and not (references and re.match(r"^\d+\.\s", lines[index].strip()))):
            paragraph.append(lines[index].strip())
            index += 1
        paragraph = " ".join(paragraph)
        style = "reference" if references else "label" if paragraph.endswith("source") or paragraph == "AIN illustration" else "body"
        story.append(Paragraph(inline(paragraph), sheet[style]))

    def footer(canvas, document):
        canvas.setFont("Article", 8)
        canvas.setFillColor(colors.HexColor("#505A61"))
        canvas.drawString(54, 30, "Izik Bachar  |  AIN research draft 11  |  7 November 2026")
        canvas.drawRightString(letter[0] - 54, 30, str(document.page))

    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=letter, leftMargin=54, rightMargin=54,
                                 topMargin=47, bottomMargin=47, title="AIN A Native Language for More Efficient AI",
                                 author="Izik Bachar", subject="AIN theory, experiments, AICC and future implementation")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SOURCE.with_name("AICC_Article_Draft_11_Review.pdf"))
    build(parser.parse_args().output)
