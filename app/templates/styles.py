"""
===========================================================
HÀNH CHÍNH AI
Document Engine V3

styles.py

Quản lý toàn bộ Style của Word Document.

Không chứa logic sinh văn bản.

Author : Hành Chính AI
Version: 1.0
===========================================================
"""

from dataclasses import dataclass
from typing import Final

from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
)
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


# =====================================================
# FONT
# =====================================================

DEFAULT_FONT: Final = "Times New Roman"

DEFAULT_FONT_SIZE: Final = 13

TITLE_FONT_SIZE: Final = 15

BIG_TITLE_SIZE: Final = 16

# =====================================================
# PAGE
# =====================================================

TOP_MARGIN: Final = Cm(2)

BOTTOM_MARGIN: Final = Cm(2)

LEFT_MARGIN: Final = Cm(3.5)

RIGHT_MARGIN: Final = Cm(2)

# =====================================================
# PARAGRAPH
# =====================================================

LINE_SPACING: Final = 1.15

FIRST_LINE_INDENT: Final = Cm(1)

SPACE_BEFORE: Final = Pt(0)

SPACE_AFTER: Final = Pt(0)

# =====================================================
# TABLE
# =====================================================

HEADER_LEFT_WIDTH: Final = Cm(8)

HEADER_RIGHT_WIDTH: Final = Cm(8)

# =====================================================
# ALIGNMENT
# =====================================================

ALIGN_LEFT = WD_ALIGN_PARAGRAPH.LEFT
ALIGN_CENTER = WD_ALIGN_PARAGRAPH.CENTER
ALIGN_RIGHT = WD_ALIGN_PARAGRAPH.RIGHT
ALIGN_JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY


# =====================================================
# STYLE MODEL
# =====================================================

@dataclass(slots=True, frozen=True)
class DocumentStyle:
    """
    Định nghĩa Style mặc định của văn bản.
    """

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


DEFAULT_STYLE = DocumentStyle()

# =====================================================
# FONT
# =====================================================


def apply_font(
    run,
    *,
    size: int | None = None,
    bold: bool = False,
    italic: bool = False,
) -> None:
    """
    Áp dụng Font.
    """

    run.font.name = DEFAULT_STYLE.font_name

    run._element.rPr.rFonts.set(
        qn("w:eastAsia"),
        DEFAULT_STYLE.font_name,
    )

    run.font.size = Pt(
        size or DEFAULT_STYLE.font_size
    )

    run.bold = bold

    run.italic = italic


# =====================================================
# PARAGRAPH
# =====================================================


def apply_paragraph_style(
    paragraph,
    *,
    align=ALIGN_JUSTIFY,
    indent: bool = True,
) -> None:
    """
    Áp dụng Paragraph Style.
    """

    paragraph.alignment = align

    fmt = paragraph.paragraph_format

    fmt.line_spacing_rule = (
        WD_LINE_SPACING.MULTIPLE
    )

    fmt.line_spacing = DEFAULT_STYLE.line_spacing

    fmt.space_before = DEFAULT_STYLE.space_before

    fmt.space_after = DEFAULT_STYLE.space_after

    fmt.first_line_indent = (
        DEFAULT_STYLE.first_line_indent
        if indent
        else Cm(0)
    )


# =====================================================
# PAGE
# =====================================================


def apply_page_style(document) -> None:
    """
    Áp dụng Page Style.
    """

    for section in document.sections:

        section.top_margin = DEFAULT_STYLE.top_margin

        section.bottom_margin = (
            DEFAULT_STYLE.bottom_margin
        )

        section.left_margin = DEFAULT_STYLE.left_margin

        section.right_margin = (
            DEFAULT_STYLE.right_margin
        )


# =====================================================
# NORMAL STYLE
# =====================================================


def apply_normal_style(document) -> None:
    """
    Áp dụng Normal Style.
    """

    style = document.styles["Normal"]

    style.font.name = DEFAULT_STYLE.font_name

    style._element.rPr.rFonts.set(
        qn("w:eastAsia"),
        DEFAULT_STYLE.font_name,
    )

    style.font.size = Pt(
        DEFAULT_STYLE.font_size
    )