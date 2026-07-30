from app.models import CongVanData
from app.templates.cong_van import CongVanTemplate


def test_cong_van():

    data = CongVanData(
        type="cong_van",
        title="Demo",
        content="Hello"
    )

    template = CongVanTemplate()

    doc = template.build(data)

    assert doc is not None