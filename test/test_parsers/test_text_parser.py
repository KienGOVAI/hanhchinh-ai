from pathlib import Path

from app.knowledge.parsers import TextParser


def test_text_parser():

    file_path = (
        Path(__file__).parent
        / "sample.txt"
    )

    parser = TextParser()

    result = parser.parse(
        file_path
    )

    assert result.text

    assert (
        "YÊN MINH"
        in result.text
    )

    assert result.source == (
        "sample.txt"
    )

    assert len(
        result.pages
    ) == 1