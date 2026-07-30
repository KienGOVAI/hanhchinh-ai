from app.templates.factory import TemplateFactory


def test_factory():

    template = TemplateFactory.create(
        "cong_van"
    )

    assert template is not None