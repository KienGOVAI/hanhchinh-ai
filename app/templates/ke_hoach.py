from app.templates.base_document import BaseDocument


class KeHoachTemplate(BaseDocument):

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
            number="...../KH-UBND",
        )

        # =====================================================
        # TIÊU ĐỀ
        # =====================================================

        self.create_title(
            title="KẾ HOẠCH",
            subtitle=data.title,
        )

        # =====================================================
        # MỤC ĐÍCH
        # =====================================================

        if hasattr(data, "purpose") and data.purpose:

            self.add_heading(
                "I. MỤC ĐÍCH",
                level=2,
            )

            self.add_text(
                data.purpose,
            )

            self.blank()

        # =====================================================
        # YÊU CẦU
        # =====================================================

        if hasattr(data, "requirements") and data.requirements:

            self.add_heading(
                "II. YÊU CẦU",
                level=2,
            )

            self.add_text(
                data.requirements,
            )

            self.blank()

        # =====================================================
        # NỘI DUNG
        # =====================================================

        self.add_heading(
            "III. NỘI DUNG THỰC HIỆN",
            level=2,
        )

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
        # TỔ CHỨC THỰC HIỆN
        # =====================================================

        if hasattr(data, "organization") and data.organization:

            self.add_heading(
                "IV. TỔ CHỨC THỰC HIỆN",
                level=2,
            )

            self.add_text(
                data.organization,
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