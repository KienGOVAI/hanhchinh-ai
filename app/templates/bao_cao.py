from app.templates.base_document import BaseDocument


class BaoCaoTemplate(BaseDocument):

    def __init__(self):
        super().__init__()

    def build(self, data):

        # =====================================================
        # HEADER
        # =====================================================

        self.create_header(
            agency="ỦY BAN NHÂN DÂN",
            unit="XÃ YÊN MINH",
            location="Yên Minh",
            date_text="ngày ..... tháng ..... năm 2026",
            number="...../BC-UBND",
        )

        # =====================================================
        # TIÊU ĐỀ
        # =====================================================

        self.create_title(
            title="BÁO CÁO",
            subtitle=data.title,
        )

        # =====================================================
        # MỞ ĐẦU
        # =====================================================

        if hasattr(data, "introduction") and data.introduction:

            self.add_heading(
                "I. MỞ ĐẦU",
                level=2,
            )

            self.add_text(
                data.introduction,
            )

            self.blank()

        # =====================================================
        # NỘI DUNG
        # =====================================================

        self.add_heading(
            "II. NỘI DUNG",
            level=2,
        )

        self.create_content(
            data.content,
        )

        self.blank()

        # =====================================================
        # BẢNG
        # =====================================================

        if hasattr(data, "table") and data.table:

            self.add_heading(
                "III. BẢNG THỐNG KÊ",
                level=2,
            )

            self.add_table(
                headers=data.table["headers"],
                rows=data.table["rows"],
            )

            self.blank()

        # =====================================================
        # KẾT LUẬN
        # =====================================================

        if hasattr(data, "conclusion") and data.conclusion:

            self.add_heading(
                "IV. KẾT LUẬN",
                level=2,
            )

            self.add_text(
                data.conclusion,
            )

            self.blank()

        # =====================================================
        # CHỮ KÝ
        # =====================================================

        self.create_signature(
            position="CHỦ TỊCH",
            signer="Nguyễn Văn A",
        )

        # =====================================================
        # NƠI NHẬN
        # =====================================================

        if hasattr(data, "recipients") and data.recipients:

            self.blank()

            self.add_recipient(
                data.recipients,
            )

        # =====================================================
        # FOOTER
        # =====================================================

        if hasattr(data, "footer") and data.footer:

            self.add_footer(
                data.footer,
            )

        return self.doc