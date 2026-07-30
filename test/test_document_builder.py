from app.models import CongVanData
from app.services.document_builder import DocumentBuilder


def test_generate_cong_van():

    data = CongVanData(
        type="cong_van",
        title="Kiểm thử",
        content="Đây là nội dung kiểm thử."
    )

    builder = DocumentBuilder()

    result = builder.build(data)

    assert result["success"] is True

    assert result["file_name"].endswith(".docx")