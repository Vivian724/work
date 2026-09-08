# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────
#  用途：把 deposit_spec.html 里的〈待确认清单〉章节转成 Word 档。
#  执行：在终端机输入  python3 deposit/make_decision_docx.py
#  需先安装一次：python3 -m pip install python-docx
#  产出：deposit/存款活动公版_待确认决策清单_v<版本>.docx
# ─────────────────────────────────────────────────────────────
"""把规格书里的〈待确认清单〉章节转成 Word 档。
   作法是「读 HTML → 转成 Word」，而不是重打一遍，
   这样两边内容永远一致，清单更新后重跑此程式即可。"""
import io, re, sys
from html.parser import HTMLParser
from html import unescape
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SPEC = '/Users/vivian_pm/Desktop/work/deposit/deposit_spec.html'
OUT  = '/Users/vivian_pm/Desktop/work/deposit/存款活动公版_待确认决策清单_v1.9.docx'
FONT = '微软雅黑'

src = io.open(SPEC, encoding='utf-8').read()
panel = src.split('<article class="panel" id="p-decisions">')[1].split('</article>')[0]

# ── 把一格 HTML 转成「段落清单」，每段是 (文字, 是否粗体) 的片段序列 ──
class Cell(HTMLParser):
    def __init__(self):
        super().__init__(); self.paras=[[]]; self.b=0
    def handle_starttag(self, t, attrs):
        if t=='b': self.b+=1
        elif t=='br': self.paras.append([])
        elif t=='span' and dict(attrs).get('class')=='cell-sub': self.paras.append([])
        elif t=='li': self.paras.append([])
    def handle_endtag(self, t):
        if t=='b' and self.b: self.b-=1
    def handle_data(self, d):
        d = d.replace('\n',' ')
        if d.strip()=='' and not self.paras[-1]: return
        self.paras[-1].append((d, self.b>0))
    def result(self):
        out=[]
        for p in self.paras:
            runs=[(re.sub(r'\s+',' ',t), b) for t,b in p]
            txt=''.join(t for t,_ in runs).strip()
            if txt: out.append(runs)
        return out or [[('', False)]]

def cell_paras(html):
    p=Cell(); p.feed(unescape(html)); return p.result()

def plain(html):
    return re.sub(r'\s+',' ', re.sub(r'<[^>]+>','', unescape(html))).strip()

# ── Word 基本设定：A4 横向（表格很宽，直向塞不下） ──
doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21)
for m in ('top_margin','bottom_margin','left_margin','right_margin'):
    setattr(sec, m, Cm(1.5))

def set_font(style_name, size, bold=False, color=None):
    st = doc.styles[style_name]
    st.font.name = FONT; st.font.size = Pt(size); st.font.bold = bold
    if color: st.font.color.rgb = color
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

set_font('Normal', 10)

def para(text_or_runs, size=10, bold=False, space_after=4, color=None, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if indent: p.paragraph_format.left_indent = Cm(indent)
    runs = text_or_runs if isinstance(text_or_runs, list) else [(text_or_runs, bold)]
    for t, b in runs:
        r = p.add_run(t); r.font.name = FONT; r.font.size = Pt(size)
        r.font.bold = b or bold
        r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
        if color: r.font.color.rgb = color
    return p

def shade(cell, hexcolor):
    el = OxmlElement('w:shd'); el.set(qn('w:fill'), hexcolor)
    cell._tc.get_or_add_tcPr().append(el)

def fill_cell(cell, paras, size=8.5, bold=False):
    cell.paragraphs[0]._element.getparent().remove(cell.paragraphs[0]._element)
    for runs in paras:
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.1
        for t, b in runs:
            r = p.add_run(t); r.font.name = FONT; r.font.size = Pt(size)
            r.font.bold = b or bold
            r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

def add_table(rows_html, widths, blank_last=False):
    """rows_html: [[cell_html, ...], ...]，第一列为表头"""
    n = len(rows_html[0])
    t = doc.add_table(rows=0, cols=n)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, row in enumerate(rows_html):
        cells = t.add_row().cells
        for j, html in enumerate(row):
            if i == 0:
                fill_cell(cells[j], [[(plain(html), True)]], size=8.5)
                shade(cells[j], 'EEF0FB')
            else:
                if blank_last and j == n-1 and plain(html) in ('—',''):
                    fill_cell(cells[j], [[('', False)]])
                else:
                    fill_cell(cells[j], cell_paras(html), size=8.5)
            cells[j].width = Cm(widths[j])
    # 逐格再设一次宽度（Word 需要每格都写）
    for row in t.rows:
        for j, c in enumerate(row.cells): c.width = Cm(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ══════════ 封面资讯 ══════════
para('存款活动公版　待确认决策清单', size=19, bold=True, space_after=2)
para('文件版本 v1.9　│　对应规格书：deposit_spec.html〈待确认清单（决策用）〉　│　产出日期：2026-09-08',
     size=9, color=RGBColor(0x6b,0x6b,0x76), space_after=10)

intent = panel.split('<div class="intent-box">')[1].split('</div>')[0]
for runs in cell_paras(intent):
    para(runs, size=10, space_after=4)

para('', size=4, space_after=6)
para('共 64 项：A 组 运营决策 49 项（P0 阻塞 11／P1 影响会员权益 11／P2 细节 27）、'
     'B 组 向系统查证 10 项（不需运营回答）、C 组 待前台原型 5 项。'
     '最右「决议」栏已标上本轮状态（✅ 已回填／🟡 待补一句／⬜ 未答）；未答与待补一句者请直接在该栏填写。', size=10, bold=True, space_after=10)

# ══════════ 逐节转换 ══════════
BLOCK = re.compile(r'<div class="change-note">(.*?)</div>|<table[^>]*>(.*?)</table>|<ol[^>]*>(.*?)</ol>', re.S)
ROW   = re.compile(r'<tr>(.*?)</tr>', re.S)
CELL  = re.compile(r'<t[hd][^>]*>(.*?)</t[hd]>', re.S)

# 各表格的栏宽（公分），依栏数对应
WIDTHS = {5: [2.6, 4.6, 4.4, 9.6, 5.5], 4: [2.6, 5.4, 12.7, 6.0], 2: [2.6, 24.1]}

sections = panel.split('<div class="section">')[1:]
for s in sections:
    num  = plain(s.split('<div class="num">')[1].split('</div>')[0])
    head = plain(s.split('<h3>')[1].split('</h3>')[0])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    para([(num + '　', True), (head, True)], size=13.5,
         color=RGBColor(0x2b,0x2b,0x8a), space_after=5)

    for m in BLOCK.finditer(s):
        note, tbl, ol = m.group(1), m.group(2), m.group(3)
        if note is not None:
            para(cell_paras(note)[0] if len(cell_paras(note))==1 else
                 [r for pp in cell_paras(note) for r in pp],
                 size=9, space_after=6, color=RGBColor(0x40,0x40,0x8a))
        elif tbl is not None:
            rows = [CELL.findall(r) for r in ROW.findall(tbl)]
            rows = [r for r in rows if r]
            n = len(rows[0])
            last = plain(rows[0][-1])
            add_table(rows, WIDTHS.get(n, [29.7/n]*n),
                      blank_last=('决议' in last or '负责' in last))
        elif ol is not None:
            for i, li in enumerate(re.findall(r'<li[^>]*>(.*?)</li>', ol, re.S), 1):
                runs = [r for pp in cell_paras(li) for r in pp]
                para([('%d. ' % i, True)] + runs, size=10, space_after=3, indent=0.5)

doc.save(OUT)
print('saved:', OUT)
