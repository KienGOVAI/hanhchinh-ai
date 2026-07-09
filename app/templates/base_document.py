from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


class BaseDocument:

    def __init__(self):
        self.doc = Document()
        self.setup_page()
        self.setup_font()

    # =====================================================
    # Thiết lập khổ giấy
    # =====================================================

    def setup_page(self):

        section = self.doc.sections[0]

        section.top_margin = Cm(2)

        section.bottom_margin = Cm(2)

        section.left_margin = Cm(3)

        section.right_margin = Cm(2)

    # =====================================================
    # Font mặc định
    # =====================================================

    def setup_font(self):

        style = self.doc.styles["Normal"]

        style.font.name = "Times New Roman"

        style._element.rPr.rFonts.set(
            qn("w:eastAsia"),
            "Times New Roman"
        )

        style.font.size = Pt(13)

    # =====================================================
    # Tạo Paragraph
    # =====================================================

    def paragraph(
        self,
        text="",
        bold=False,
        italic=False,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        size=13,
    ):

        p = self.doc.add_paragraph()

        p.alignment = align

        run = p.add_run(text)

        run.bold = bold
        run.italic = italic

        run.font.name = "Times New Roman"

        run._element.rPr.rFonts.set(
            qn("w:eastAsia"),
            "Times New Roman"
        )

        run.font.size = Pt(size)

        return p

    # =====================================================
    # Header chuẩn Nghị định 30
    # =====================================================

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

        # ----------------------
        # CỘT TRÁI
        # ----------------------

        p = left.paragraphs[0]

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p.add_run(agency + "\n")

        run.bold = True

        run.font.size = Pt(13)

        run.font.name = "Times New Roman"

        run = p.add_run(unit)

        run.bold = True

        run.font.size = Pt(13)

        run.font.name = "Times New Roman"

        p = left.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        p.add_run("_______________")

        p = left.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p.add_run(f"Số: {number}")

        run.font.size = Pt(13)

        run.font.name = "Times New Roman"

        # ----------------------
        # CỘT PHẢI
        # ----------------------

        p = right.paragraphs[0]

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p.add_run(
            "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n"
        )

        run.bold = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

        run = p.add_run(
            "Độc lập - Tự do - Hạnh phúc"
        )

        run.bold = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

        p = right.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        p.add_run("_______________")

        p = right.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p.add_run(
            f"{location}, {date_text}"
        )

        run.italic = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

        self.doc.add_paragraph()

    # =====================================================
    # Tiêu đề văn bản
    # =====================================================

    def create_title(
        self,
        title,
        subtitle=""
    ):

        p = self.doc.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p.add_run(title.upper())

        run.bold = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(15)

        if subtitle != "":

            p = self.doc.add_paragraph()

            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = p.add_run(subtitle)

            run.bold = True

            run.font.name = "Times New Roman"

            run.font.size = Pt(13)

        self.doc.add_paragraph()

    # =====================================================
    # Nội dung
    # =====================================================

    def create_content(
        self,
        text
    ):

        p = self.doc.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        run = p.add_run(text)

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

    # =====================================================
    # Người ký
    # =====================================================

    def create_signature(
        self,
        position,
        signer
    ):

        p = self.doc.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        run = p.add_run(position)

        run.bold = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

        self.doc.add_paragraph()

        self.doc.add_paragraph()

        self.doc.add_paragraph()

        p = self.doc.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        run = p.add_run(signer)

        run.bold = True

        run.font.name = "Times New Roman"

        run.font.size = Pt(13)

    # =====================================================
    # Xuống dòng
    # =====================================================

    def blank(self):

        self.doc.add_paragraph()

    # =====================================================
    # Lưu file
    # =====================================================

    def save(
        self,
        path
    ):

        self.doc.save(path)