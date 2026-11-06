from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'docs/article/AICC_Article_Draft_9.md'
TARGET = SOURCE.with_name('AICC_Article_Draft_9_Review.pdf')
FONT = Path(r'C:\Windows\Fonts')
pdfmetrics.registerFont(TTFont('Arial', str(FONT/'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', str(FONT/'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Italic', str(FONT/'ariali.ttf')))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-Bold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyAIN', fontName='Arial', fontSize=10.8, leading=15,
                          textColor=colors.HexColor('#202d36'), spaceAfter=8,
                          allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle(name='TitleAIN', parent=styles['BodyAIN'], fontName='Arial-Bold',
                          fontSize=25, leading=29, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name='SubtitleAIN', parent=styles['BodyAIN'], fontSize=12,
                          leading=16, textColor=colors.HexColor('#52616d'), spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name='HeadingAIN', parent=styles['BodyAIN'], fontName='Arial-Bold',
                          fontSize=13, leading=17, textColor=colors.HexColor('#075f68'),
                          spaceBefore=12, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name='CellAIN', parent=styles['BodyAIN'], fontSize=9.2, leading=12, spaceAfter=0))
styles.add(ParagraphStyle(name='CellHeadAIN', parent=styles['CellAIN'], fontName='Arial-Bold', textColor=colors.white))

def normalize(text):
    return re.sub('[\u2010-\u2015\u2212]', '-', text)

def inline(text):
    tokens = []
    def link(m):
        label, target = m.groups()
        if not target.startswith(('https:', 'http:', '#')):
            resolved = (SOURCE.parent / target).resolve()
            relative = resolved.relative_to(REPO.resolve()).as_posix()
            kind = 'tree' if resolved.is_dir() else 'blob'
            target = 'https://github.com/izikon78/AICC/' + kind + '/research/native-ain-hypothesis-reassessment/' + relative
        tokens.append('<link color="#075f68" href="' + html.escape(target, quote=True) + '">' + html.escape(normalize(label)) + '</link>')
        return f'AINLINK{len(tokens)-1}END'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, normalize(text))
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    for i, token in enumerate(tokens):
        text = text.replace(f'AINLINK{i}END', token)
    return text

lines = SOURCE.read_text(encoding='utf-8').splitlines()
story, paragraph, i = [], [], 0
def flush():
    if paragraph:
        story.append(Paragraph(inline(' '.join(paragraph)), styles['BodyAIN']))
        paragraph.clear()

while i < len(lines):
    line = lines[i].strip()
    if not line:
        flush(); i += 1; continue
    if line.startswith('|'):
        flush(); rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                style = styles['CellHeadAIN'] if not rows else styles['CellAIN']
                rows.append([Paragraph(inline(c), style) for c in cells])
            i += 1
        table = Table(rows, colWidths=[100, 162, 242], repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#075f68')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f1f6f7')),
            ('GRID', (0,0), (-1,-1), .4, colors.HexColor('#c8d6da')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.extend([table, Spacer(1, 10)]); continue
    if line.startswith('#'):
        flush()
        level = len(line) - len(line.lstrip('#'))
        name = 'TitleAIN' if level == 1 else 'SubtitleAIN' if level == 2 else 'HeadingAIN'
        story.append(Paragraph(inline(line.lstrip('#').strip()), styles[name]))
    else:
        paragraph.append(line)
    i += 1
flush()

def page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#52616d'))
    canvas.drawString(54, 758, 'AIN - native-learning research')
    canvas.drawRightString(558, 758, 'Draft 9 | 6 November 2026')
    canvas.setStrokeColor(colors.HexColor('#c8d6da'))
    canvas.line(54, 748, 558, 748)
    canvas.drawString(54, 34, 'Izik Bachar | Research draft for review')
    canvas.drawRightString(558, 34, str(doc.page))
    canvas.restoreState()

doc = SimpleDocTemplate(str(TARGET), pagesize=letter, rightMargin=54, leftMargin=54,
                        topMargin=59, bottomMargin=52,
                        title='AIN: A Native Language for More Efficient AI - Research draft 9', author='Izik Bachar',
                        subject='Native learning, programming efficiency and computational reuse')
doc.build(story, onFirstPage=page, onLaterPages=page)
from pypdf import PdfReader
reader = PdfReader(str(TARGET))
text = '\n'.join(p.extract_text() or '' for p in reader.pages)
normalized_text = ' '.join(text.split())
for required in ('AIN: A Native Language for More Efficient AI', 'It started with a beep', 'plips', 'What native knowledge changes', 'Three claims', 'Credits and evidence scope', 'Izik Bachar'):
    assert required in normalized_text, required
assert not any(term in text for term in ('AINLINK', '\ufffd', '\u25a0'))
print({'pages': len(reader.pages), 'bytes': TARGET.stat().st_size, 'path': str(TARGET)})
