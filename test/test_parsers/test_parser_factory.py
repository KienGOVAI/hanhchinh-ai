from app.knowledge.parsers import (
    DOCXParser,
    PDFParser,
    ParserFactory,
    TextParser,
)


def test_pdf_factory():
    parser = ParserFactory.create(
        "test.pdf"
    )

    assert isinstance(
        parser,
        PDFParser,
    )


def test_docx_factory():
    parser = ParserFactory.create(
        "test.docx"
    )

    assert isinstance(
        parser,
        DOCXParser,
    )


def test_txt_factory():
    parser = ParserFactory.create(
        "test.txt"
    )

    assert isinstance(
        parser,
        TextParser,
    )