from app.templates.base_document import BaseDocument


class CongVanTemplate(BaseDocument):

    def __init__(self):
        super().__init__()

    def build(self, data):

        # =====================================
        # HEADER
        # =====================================

        self.create_header(
            agency="ỦY BAN NHÂN DÂN",
            unit="XÃ YÊN MINH",
            location="Yên Minh",
            date_text="ngày ..... tháng ..... năm 2026",
            number="...../UBND-VP",
        )

        # =====================================
        # TITLE
        # =====================================

        self.create_title(
            title="CÔNG VĂN",
            subtitle=data.title,
        )

        # =====================================
        # CONTENT
        # =====================================

        self.create_content(
            data.content,
        )

        self.blank()

        # =====================================
        # SIGNATURE
        # =====================================

        self.create_signature(
            position="CHỦ TỊCH",
            signer="Nguyễn Văn A",
        )

        return self.doc