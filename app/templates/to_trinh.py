from app.templates.base_document import BaseDocument


class ToTrinhTemplate(BaseDocument):

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
            number="...../TTr-UBND",
        )

        # =====================================================
        # TIÊU ĐỀ
        # =====================================================

        self.create_title(
            title="TỜ TRÌNH",
            subtitle=data.title,
        )

        # =====================================================
        # KÍNH GỬI
        # =====================================================

        if hasattr(data, "receiver") and data.receiver:

            self.add_heading(
                "Kính gửi:",
                level=2,
            )

            self.add_text(
                data.receiver,
            )

            self.blank()

        # =====================================================
        # CĂN CỨ
        # =====================================================

        if hasattr(data, "legal_basis") and data.legal_basis:

            self.add_heading(
                "Căn cứ",
                level=2,
            )

            self.add_text(
                data.legal_basis,
            )

            self.blank()

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
        # KIẾN NGHỊ
        # =====================================================

        if hasattr(data, "proposal") and data.proposal:

            self.add_heading(
                "Kiến nghị",
                level=2,
            )

            self.add_text(
                data.proposal,
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