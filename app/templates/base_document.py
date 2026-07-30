from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.templates.styles import (
    apply_font,
    apply_paragraph_style,
    apply_page_style,
    apply_normal_style,
    ALIGN_CENTER,
    ALIGN_JUSTIFY,
    ALIGN_RIGHT,
)


class BaseDocument:

    def __init__(self):
        self.doc = Document()
        self.setup_page()
        self.setup_font()

    # =====================================================
    # Thiết lập khổ giấy
    # =====================================================

    def setup_page(self):
        apply_page_style(self.doc)

    # =====================================================
    # Font mặc định
    # =====================================================

    def setup_font(self):
        apply_normal_style(self.doc)

    # =====================================================
    # Paragraph chuẩn
    # =====================================================

    def paragraph(
        self,
        text="",
        bold=False,
        italic=False,
        align=ALIGN_JUSTIFY,
        size=13,
    ):

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=align,
        )

        run = p.add_run(text)

        apply_font(
            run,
            size=size,
            bold=bold,
            italic=italic,
        )

        return p

    # =====================================================
    # Thêm nhiều đoạn văn
    # =====================================================

    def add_text(
        self,
        text,
        align=ALIGN_JUSTIFY,
    ):

        for line in text.split("\n"):

            line = line.strip()

            if not line:
                continue

            self.paragraph(
                text=line,
                align=align,
            )
    # =====================================================
    # Tiêu đề dùng chung
    # =====================================================

    def add_heading(
        self,
        text,
        level=1,
        align=ALIGN_CENTER,
    ):

        if level == 1:
            size = 15
            bold = True

        elif level == 2:
            size = 14
            bold = True

        elif level == 3:
            size = 13
            bold = True

        else:
            size = 13
            bold = False

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=align,
            indent=False,
        )

        run = p.add_run(text)

        apply_font(
            run,
            size=size,
            bold=bold,
        )

        return p
    # =====================================================
    # Header chuẩn Nghị định 30
    # =====================================================
    # =====================================================
    # Bảng dùng chung
    # =====================================================

    def add_table(
        self,
        headers,
        rows,
    ):

        table = self.doc.add_table(
            rows=1,
            cols=len(headers)
        )

        table.style = "Table Grid"

        # -------------------------
        # Header
        # -------------------------

        hdr = table.rows[0].cells

        for i, text in enumerate(headers):

            p = hdr[i].paragraphs[0]

            apply_paragraph_style(
                p,
                align=ALIGN_CENTER,
                indent=False,
            )

            run = p.add_run(str(text))

            apply_font(
                run,
                bold=True,
            )

        # -------------------------
        # Data
        # -------------------------

        for row in rows:

            cells = table.add_row().cells

            for i, value in enumerate(row):

                p = cells[i].paragraphs[0]

                apply_paragraph_style(
                    p,
                    align=ALIGN_LEFT,
                    indent=False,
                )

                run = p.add_run(str(value))

                apply_font(run)

        return table
        # =====================================================
    # Nơi nhận
    # =====================================================

    def add_recipient(self, recipients):

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_LEFT,
            indent=False,
        )

        run = p.add_run("Nơi nhận:")

        apply_font(
            run,
            bold=True,
            italic=True,
        )

        for item in recipients:

            p = self.doc.add_paragraph()

            apply_paragraph_style(
                p,
                align=ALIGN_LEFT,
                indent=False,
            )

            run = p.add_run(f"- {item}")

            apply_font(run)
                # =====================================================
    # Footer / Ghi chú cuối văn bản
    # =====================================================

    def add_footer(self, text=""):

        if not text:
            return

        self.blank()

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        run = p.add_run(text)

        apply_font(
            run,
            italic=True,
            size=11,
        )
    def create_header(
        self,
        agency,
        unit,
        location,
        date_text,
        number=""
    ):

        table = self.doc.add_table(rows=1, cols=2)
        table.autofit = False

        table.columns[0].width = Cm(8)
        table.columns[1].width = Cm(8)

        left = table.cell(0, 0)
        right = table.cell(0, 1)

        # ==========================
        # CỘT TRÁI
        # ==========================

        p = left.paragraphs[0]

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        run = p.add_run(agency + "\n")

        apply_font(
            run,
            bold=True,
        )

        run = p.add_run(unit)

        apply_font(
            run,
            bold=True,
        )

        p = left.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        p.add_run("_______________")

        p = left.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        run = p.add_run(f"Số: {number}")

        apply_font(run)

        # ==========================
        # CỘT PHẢI
        # ==========================

        p = right.paragraphs[0]

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        run = p.add_run(
            "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n"
        )

        apply_font(
            run,
            bold=True,
        )

        run = p.add_run(
            "Độc lập - Tự do - Hạnh phúc"
        )

        apply_font(
            run,
            bold=True,
        )

        p = right.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        p.add_run("_______________")

        p = right.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_CENTER,
            indent=False,
        )

        run = p.add_run(f"{location}, {date_text}")

        apply_font(
            run,
            italic=True,
        )

        self.blank()

    # =====================================================
    # Tiêu đề
    # =====================================================

    def create_title(
        self,
        title,
        subtitle=""
    ):

        self.add_heading(
            title.upper(),
            level=1,
        )

        if subtitle:

            self.add_heading(
                subtitle,
                level=3,
            )

        self.blank()

    # =====================================================
    # Nội dung
    # =====================================================

    def create_content(self, text):

        self.add_text(text)

    # =====================================================
    # Người ký
    # =====================================================

    def create_signature(
        self,
        position,
        signer
    ):

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_RIGHT,
            indent=False,
        )

        run = p.add_run(position)

        apply_font(
            run,
            bold=True,
        )

        self.blank(3)

        p = self.doc.add_paragraph()

        apply_paragraph_style(
            p,
            align=ALIGN_RIGHT,
            indent=False,
        )

        run = p.add_run(signer)

        apply_font(
            run,
            bold=True,
        )

    # =====================================================
    # Xuống dòng
    # =====================================================

    def blank(self, lines=1):

        for _ in range(lines):
            self.doc.add_paragraph()

    # =====================================================
    # Lưu file
    # =====================================================

    def save(self, path):

        self.doc.save(path)