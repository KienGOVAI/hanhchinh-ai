from pathlib import Path


class PromptService:

    def __init__(self):

        self.prompt_folder = (
            Path(__file__).parent.parent
            / "prompts"
        )

    def load(self, name: str):

        file_path = self.prompt_folder / f"{name}.md"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy Prompt: {file_path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )