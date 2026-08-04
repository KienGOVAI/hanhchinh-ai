from typing import Any

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    """
    Chuẩn dữ liệu trả về khi API phát sinh lỗi.
    """

    success: bool = Field(
        default=False,
        description="Trạng thái xử lý"
    )

    message: str = Field(
        ...,
        description="Thông báo lỗi"
    )

    error_code: str | None = Field(
        default=None,
        description="Mã lỗi"
    )

    detail: Any | None = Field(
        default=None,
        description="Thông tin chi tiết"
    )


class ValidationErrorResponse(ApiError):
    """
    Response khi dữ liệu gửi lên không hợp lệ.
    """

    error_code: str = "VALIDATION_ERROR"


class ProviderErrorResponse(ApiError):
    """
    Response khi AI Provider phát sinh lỗi.
    """

    error_code: str = "PROVIDER_ERROR"


class InternalServerErrorResponse(ApiError):
    """
    Response khi Backend xảy ra lỗi.
    """

    error_code: str = "INTERNAL_SERVER_ERROR"