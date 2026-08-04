from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Chuẩn response chung cho toàn bộ API.
    """

    success: bool = True

    message: str = "Success"

    data: Optional[T] = None