"""
Knowledge File Scanner
----------------------

Quét toàn bộ file trong Knowledge Base.
"""

from pathlib import Path


class FileScanner:
    """
    Quét file trong thư mục Knowledge.
    """

    def __init__(
        self,
        root: Path,
    ):

        self.root = root

    # =====================================================
    # PUBLIC
    # =====================================================

    def scan(
        self,
        extensions: tuple[str, ...],
    ) -> list[Path]:
        """
        Quét toàn bộ file theo phần mở rộng.

        Parameters
        ----------
        extensions:
            Ví dụ:
                (".md",)
                (".pdf",)
                (".docx",)

        Returns
        -------
        list[Path]
        """

        if not self.root.exists():
            return []

        files: list[Path] = []

        for file in self.root.rglob("*"):

            if (
                file.is_file()
                and file.suffix.lower() in extensions
            ):
                files.append(file)

        return sorted(files)

    def count(
        self,
        extensions: tuple[str, ...],
    ) -> int:
        """
        Đếm số lượng file.
        """

        return len(
            self.scan(extensions)
        )

    def is_empty(
        self,
        extensions: tuple[str, ...],
    ) -> bool:
        """
        Kiểm tra có dữ liệu hay không.
        """

        return self.count(
            extensions
        ) == 0