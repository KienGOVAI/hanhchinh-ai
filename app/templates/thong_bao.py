from app.templates.base_document import BaseDocument


class ThongBaoTemplate(BaseDocument):

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
            number="...../TB-UBND",
        )

        # =====================================================
        # TIÊU ĐỀ
        # =====================================================

        self.create_title(
            title="THÔNG BÁO",
            subtitle=data.title,
        )

        # =====================================================
        # NỘI DUNG
        # =====================================================

        self.create_content(
            data.content,
        )

        self.blank()

        # =====================================================
        # BẢNG (nếu có)
        # =====================================================

        if hasattr(data, "table") and data.table:

            self.add_table(
                headers=data.table["headers"],
                rows=data.table["rows"],
            )

            self.blank()

        # =====================================================
        # CHỮ KÝ
        # =====================================================

        self.create_signature(
            position="KT. CHỦ TỊCH\nPHÓ CHỦ TỊCH",
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