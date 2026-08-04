from pydantic import BaseModel


class CongVanData(BaseModel):
    type: str
    title: str
    content: str

    table: list | None = None
    recipients: list[str] | None = None
    footer: str | None = None