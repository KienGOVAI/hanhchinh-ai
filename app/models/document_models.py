from typing import List, Optional

from pydantic import BaseModel


class TableData(BaseModel):
    headers: List[str]
    rows: List[List[str]]


class BaseDocumentData(BaseModel):
    type: str

    title: str

    content: str

    table: Optional[TableData] = None

    recipients: Optional[List[str]] = None

    footer: Optional[str] = None


class CongVanData(BaseDocumentData):
    pass


class QuyetDinhData(BaseDocumentData):
    legal_basis: Optional[str] = None


class ThongBaoData(BaseDocumentData):
    pass


class BaoCaoData(BaseDocumentData):
    introduction: Optional[str] = None
    conclusion: Optional[str] = None


class KeHoachData(BaseDocumentData):
    purpose: Optional[str] = None
    requirements: Optional[str] = None
    organization: Optional[str] = None


class ToTrinhData(BaseDocumentData):
    receiver: Optional[str] = None
    legal_basis: Optional[str] = None
    proposal: Optional[str] = None