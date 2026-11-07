"""Build the editable article from its Markdown, verified examples and figures.

Use the Codex bundled Python runtime with python-docx. PDF rendering is a
separate Word/packaged-renderer step so both formats share actual pagination.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
from urllib.parse import urljoin

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/article/AICC_Article_Draft_10.md'
WEB_BASE = 'https://github.com/izikon78/AICC/blob/research/approved-core-article-draft-10/docs/article/'


def clean(text):
    return re.sub('[\u2010-\u2015\u2212]', '-', text)


def font(run, name=None, size=None, bold=None):
    if name:
        run.font.name = name
        run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    return run


def hyperlink(paragraph, label, target):
    if not target.startswith(('https://', 'http://', '#')): target = urljoin(WEB_BASE, target)
    rel = paragraph.part.relate_to(target,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    link = OxmlElement('w:hyperlink'); link.set(qn('r:id'), rel)
    run = OxmlElement('w:r'); props = OxmlElement('w:rPr')
    color = OxmlElement('w:color'); color.set(qn('w:val'), '174B68'); props.append(color)
    under = OxmlElement('w:u'); under.set(qn('w:val'), 'single'); props.append(under)
    run.append(props); value = OxmlElement('w:t'); value.text = clean(label); run.append(value)
    link.append(run); paragraph._p.append(link)


def inline(paragraph, text, size=None, bold=None):
    pattern = r'(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|`[^`]+`)'
    for piece in re.split(pattern, clean(text)):
        if not piece: continue
        if piece.startswith('[') and re.fullmatch(r'\[[^\]]+\]\([^)]+\)', piece):
            match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', piece)
            hyperlink(paragraph, *match.groups())
        elif piece.startswith('**') and piece.endswith('**'):
            font(paragraph.add_run(piece[2:-2]), size=size, bold=True)
        elif piece.startswith('`') and piece.endswith('`'):
            font(paragraph.add_run(piece[1:-1]), name='Consolas', size=(size or 11)-.5, bold=bold)
        else:
            font(paragraph.add_run(piece), size=size, bold=bold)


def table(document, rows):
    n = len(rows[0])
    if n == 4: widths = [2.04, 1.58, 1.75, 1.4]
    elif n == 6: widths = [1.2, 1.13, 1.0, 1.05, 1.05, 1.34]
    else: widths = [6.77/n]*n
    t = document.add_table(rows=1, cols=n)
    t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for index,width in enumerate(widths): t.columns[index].width = Inches(width)
    props = t._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        node = OxmlElement('w:'+edge)
        for key,value in (('val','single'),('sz','4'),('color','D9D9D9')): node.set(qn('w:'+key),value)
        borders.append(node)
    props.append(borders)
    for ri,row in enumerate(rows):
        cells = t.rows[0].cells if ri == 0 else t.add_row().cells
        row_props = t.rows[ri]._tr.get_or_add_trPr()
        no_split = OxmlElement('w:cantSplit'); row_props.append(no_split)
        if ri == 0:
            repeated = OxmlElement('w:tblHeader'); repeated.set(qn('w:val'),'true'); row_props.append(repeated)
        for ci,value in enumerate(row):
            cell = cells[ci]; cell.width = Inches(widths[ci]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = cell._tc.get_or_add_tcPr()
            margins = OxmlElement('w:tcMar')
            for edge,amount in (('top','95'),('bottom','95'),('left','100'),('right','100')):
                m = OxmlElement('w:'+edge); m.set(qn('w:w'),amount); m.set(qn('w:type'),'dxa'); margins.append(m)
            cp.append(margins)
            shade = OxmlElement('w:shd'); shade.set(qn('w:fill'),'E4ECF1' if ri == 0 else ('F6F8FA' if ri%2 == 0 else 'FFFFFF')); cp.append(shade)
            p = cell.paragraphs[0]; p.style = 'Table Text'
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            inline(p,value,size=9.3,bold=(ri==0))
    spacer = document.add_paragraph(); spacer.paragraph_format.space_after = Pt(4)
    spacer.paragraph_format.space_before = Pt(0); spacer.paragraph_format.line_spacing = .4
    return t


def build(output):
    source = SOURCE.read_text(encoding='utf-8')
    if '{{EXAMPLE_' in source: raise ValueError('Inject verified example snippets before authoring')
    doc = Document(); section = doc.sections[0]
    section.page_width = Inches(8.27); section.page_height = Inches(11.69)
    section.left_margin = section.right_margin = Inches(.75)
    section.top_margin = Inches(.72); section.bottom_margin = Inches(.72)
    section.header_distance = section.footer_distance = Inches(.3)
    normal = doc.styles['Normal']; normal.font.name='Cambria'; normal.font.size=Pt(11)
    normal.font.color.rgb=RGBColor(0,0,0)
    normal.paragraph_format.line_spacing=1.12
    normal.paragraph_format.space_after=Pt(7)
    normal.paragraph_format.widow_control=True
    for name,size in [('Title',25),('Subtitle',12.5),('Heading 1',14),('Heading 2',12),('Heading 3',11)]:
        style=doc.styles[name]; style.font.name='Cambria'; style.font.size=Pt(size)
        style.font.color.rgb=RGBColor(0,0,0)
        style.font.bold=name not in ('Subtitle',)
        style.paragraph_format.space_before=Pt(13 if name.startswith('Heading') else 0)
        style.paragraph_format.space_after=Pt(7)
        style.paragraph_format.keep_with_next=True
        if style._element.pPr is not None:
            for node in list(style._element.pPr):
                if node.tag == qn('w:pBdr'): style._element.pPr.remove(node)
    for name,size in [('Table Text',9.3),('Code Block',8.6),('Figure Caption',9.3),('Metadata',9.5)]:
        if name not in doc.styles: doc.styles.add_style(name,1)
        style=doc.styles[name]; style.base_style=normal; style.font.name='Consolas' if name=='Code Block' else 'Calibri'
        style.font.size=Pt(size); style.font.color.rgb=RGBColor(0,0,0)
        style.paragraph_format.line_spacing=1.0 if name=='Code Block' else 1.08
        style.paragraph_format.space_after=Pt(8 if name!='Table Text' else 0)
    doc.styles['Code Block'].paragraph_format.left_indent=Inches(.12)
    doc.styles['Code Block'].paragraph_format.keep_together=True
    doc.styles['Figure Caption'].paragraph_format.space_before=Pt(3)
    footer=section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    font(footer.add_run('Izik Bachar  |  AIN research draft 10  |  '),name='Calibri',size=8)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.core_properties.author='Izik Bachar'
    doc.core_properties.title='AIN: A Native Language for More Efficient AI'
    doc.core_properties.subject='Conditional approved-core workflow accounting and independent reconstruction'
    doc.core_properties.keywords='AIN, AICC, approved core, conditional accounting, Grok pending'
    lines=source.splitlines(); i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1; continue
        if line=='<!-- pagebreak -->': doc.add_page_break(); i+=1; continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]);i+=1
            p=doc.add_paragraph(style='Code Block')
            font(p.add_run('\n'.join(code)),name='Consolas',size=8.6)
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in row): rows.append(row)
                i+=1
            table(doc,rows);continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:
            from PIL import Image
            path=(SOURCE.parent/image.group(2)).resolve()
            with Image.open(path) as picture: ratio=picture.height/picture.width
            width=min(6.5, 3.35/ratio)
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(1)
            pic=p.add_run().add_picture(str(path),width=Inches(width))
            pic._inline.docPr.set('descr',image.group(1))
            i+=1;continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));text=line.lstrip('#').strip()
            style='Title' if level==1 else 'Subtitle' if level==2 and i<8 else 'Heading 1' if level<=3 else 'Heading 2'
            p=doc.add_paragraph(style=style);inline(p,text)
            i+=1;continue
        if re.match(r'^\d+\. ',line):
            p=doc.add_paragraph();p.paragraph_format.space_after=Pt(5)
            inline(p,line);i+=1;continue
        block=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','```','![','<!--')):
            block.append(lines[i].strip());i+=1
        text=' '.join(block)
        style='Figure Caption' if text.startswith('Figure ') else 'Metadata' if text.startswith('Izik Bachar') else 'Normal'
        p=doc.add_paragraph(style=style);inline(p,text)
        if re.match(r'^\d+\. ',text): p.paragraph_format.space_after=Pt(5)
    output.parent.mkdir(parents=True,exist_ok=True);doc.save(output)
    print(output)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=SOURCE.with_name('AICC_Article_Draft_10_Review.docx'))
    build(parser.parse_args().output)
