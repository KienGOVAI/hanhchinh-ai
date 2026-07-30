"""
===========================================================
HÀNH CHÍNH AI
Document Engine V3
styles.py

Quản lý toàn bộ định dạng Word.
Không chứa logic tạo văn bản.

Author : Hành Chính AI
Version: 0.6 Alpha
===========================================================
"""

from dataclasses import dataclass

from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn


# ==========================================================
# FONT
# ==========================================================

DEFAULT_FONT = "Times New Roman"

DEFAULT_FONT_SIZE = 13

TITLE_FONT_SIZE = 15

BIG_TITLE_SIZE = 16


# ==========================================================
# PAGE
# ==========================================================

TOP_MARGIN = Cm(2)

BOTTOM_MARGIN = Cm(2)

LEFT_MARGIN = Cm(3.5)

RIGHT_MARGIN = Cm(2)


# ==========================================================
# PARAGRAPH
# ==========================================================

LINE_SPACING = 1.15

FIRST_LINE_INDENT = Cm(1)

SPACE_BEFORE = Pt(0)

SPACE_AFTER = Pt(0)


# ==========================================================
# TABLE
# ==========================================================

HEADER_LEFT_WIDTH = Cm(8)

HEADER_RIGHT_WIDTH = Cm(8)


# ==========================================================
# ALIGNMENT
# ==========================================================

ALIGN_LEFT = WD_ALIGN_PARAGRAPH.LEFT

ALIGN_CENTER = WD_ALIGN_PARAGRAPH.CENTER

ALIGN_RIGHT = WD_ALIGN_PARAGRAPH.RIGHT

ALIGN_JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY


# ==========================================================
# STYLE CLASS
# ==========================================================

@dataclass
class DocumentStyle:

    font_name: str = DEFAULT_FONT

    font_size: int = DEFAULT_FONT_SIZE

    title_size: int = TITLE_FONT_SIZE

    big_title_size: int = BIG_TITLE_SIZE

    line_spacing: float = LINE_SPACING

    first_line_indent = FIRST_LINE_INDENT

    space_before = SPACE_BEFORE

    space_after = SPACE_AFTER

    top_margin = TOP_MARGIN

    bottom_margin = BOTTOM_MARGIN

    left_margin = LEFT_MARGIN

    right_margin = RIGHT_MARGIN


# ==========================================================
# FONT HELPER
# ==========================================================

def apply_font(
        run,
        size=None,
        bold=False,
        italic=False):

    run.font.name = DEFAULT_FONT

    run._element.rPr.rFonts.set(
        qn("w:eastAsia"),
        DEFAULT_FONT
    )

    run.font.size = Pt(size or DEFAULT_FONT_SIZE)

    run.bold = bold

    run.italic = italic


# ==========================================================
# PARAGRAPH HELPER
# ==========================================================

def apply_paragraph_style(
        paragraph,
        align=ALIGN_JUSTIFY,
        indent=True):

    paragraph.alignment = align

    fmt = paragraph.paragraph_format

    fmt.line_spacing_rule = WD_LINE_SPACING.MULTIPLE

    fmt.line_spacing = LINE_SPACING

    fmt.space_before = SPACE_BEFORE

    fmt.space_after = SPACE_AFTER

    if indent:

        fmt.first_line_indent = FIRST_LINE_INDENT

    else:

        fmt.first_line_indent = Cm(0)


# ==========================================================
# PAGE HELPER
# ==========================================================

def apply_page_style(document):

    section = document.sections[0]

    section.top_margin = TOP_MARGIN

    section.bottom_margin = BOTTOM_MARGIN

    section.left_margin = LEFT_MARGIN

    section.right_margin = RIGHT_MARGIN


# ==========================================================
# NORMAL STYLE
# ==========================================================

def apply_normal_style(document):

    style = document.styles["Normal"]

    style.font.name = DEFAULT_FONT

    style._element.rPr.rFonts.set(
        qn("w:eastAsia"),
        DEFAULT_FONT
    )

    style.font.size = Pt(DEFAULT_FONT_SIZE)