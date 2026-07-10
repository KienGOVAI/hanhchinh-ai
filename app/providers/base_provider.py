from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Tất cả AI Provider đều phải kế thừa lớp này.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Sinh nội dung từ AI.
        """
        raise NotImplementedError