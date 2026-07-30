from app.templates.cong_van import CongVanTemplate
from app.templates.quyet_dinh import QuyetDinhTemplate
from app.templates.thong_bao import ThongBaoTemplate
from app.templates.bao_cao import BaoCaoTemplate
from app.templates.ke_hoach import KeHoachTemplate
from app.templates.to_trinh import ToTrinhTemplate


class TemplateFactory:

    templates = {
        "cong_van": CongVanTemplate,
        "quyet_dinh": QuyetDinhTemplate,
        "thong_bao": ThongBaoTemplate,
        "bao_cao": BaoCaoTemplate,
        "ke_hoach": KeHoachTemplate,
        "to_trinh": ToTrinhTemplate,
    }

    @classmethod
    def create(cls, template_name):

        template = cls.templates.get(template_name)

        if template is None:
            raise ValueError(
                f"Không hỗ trợ template '{template_name}'"
            )

        return template()